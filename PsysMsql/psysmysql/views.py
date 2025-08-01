import json
from django.contrib import messages
from django.db import DatabaseError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.views import View
from django.utils.decorators import method_decorator
from .tasks import send_sell_confirmation_email


from .models import Products
from .models import Sell
from .models import SellProducts
from .models import Stock
from .models import RegistersellDetail
from .models import Clients
from django.contrib.auth.models import User, Group


from .forms import ProductForm
from .forms import DeleteProductForm
from .forms import SearchProduct
from .forms import SearchEmailForm
from .forms import SellForm
from .forms import StockForm
from .forms import SentSellForm
from .forms import AssginUserToGroupForm
from .forms import RegisterSellDetailForm
from .forms import ClientsForm


def is_admin(user):
    if user.is_authenticated:
        if user.groups.filter(name="Administrador").exists():
            return True
    return False


def is_seller(user):
    if user.is_authenticated:
        if user.groups.filter(name="Vendedor").exists():
            return True
    return False


def app(request):
    return render(request, "app.html")


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return render(request, "admin/admin_dashboard.html")
        elif is_seller(request.user):
            return render(request, "admin/admin_seller_dashboard.html")
    return redirect("login")


@login_required
@permission_required("psysmysql.add_products", login_url="error")
def register_product(request):
    if request.method == "POST":
        formregister = ProductForm(request.POST)
        if formregister.is_valid():
            name = formregister.cleaned_data["name"]
            price = formregister.cleaned_data["price"]
            description = formregister.cleaned_data["description"]

            try:
                product = Products(name=name, price=price, description=description)
                if Products.objects.filter(name=product.name):
                    messages.info(request, "el producto ya existe")
                else:
                    product.save()
                    messages.success(request, "producto guardado con exito")
            except Product.DoesNotExist:
                messages.error(request, "El producto no existe")
            except DatabaseError as e:
                messages.error(request, f"Error inesperado: {e}")

            formregister = ProductForm()
            return redirect("register_product")
    else:
        formregister = ProductForm()
    return render(request, "registerproduct.html", {"formregister": formregister})


def view_product(request):
    all_products = Products.objects.all().order_by("name")
    total_products = Products.objects.count()
    return render(
        request,
        "allproducts.html",
        {"allproducts": all_products, "total_products_save": total_products},
    )


@login_required
@permission_required("psysmysql.delete_products", login_url="error")
def delete_product(request):
    if request.method == "POST":
        form = DeleteProductForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            delete_product = Products.objects.get(name=name)

            wait_time = 5  # Duración de los mensajes en pantalla.
            try:
                if delete_product:
                    delete_product.delete()
                    form = DeleteProductForm()
                else:
                    messages.error(request, "El producto no existe")
            except ValueError as e:
                messages.error(request, f"El valor a buscar es erroneo {e}")
            except TypeError as e:
                messages.error(request, f"Typo de dato erroneo {e}")
            except DatabaseError as e:
                messages.error(request, f"Error en la base de datos: {e}")
            return render(
                request,
                "deleteproductdone.html",
                {"wait_time": wait_time, "product_delete": delete_product},
            )
    else:
        form = DeleteProductForm()
        return render(request, "deleteproduct.html", {"form": form})


def delete_product_done(request):
    return render(request, "deleteproductdone.html")


@method_decorator(
    [
        login_required(login_url="login"),
        permission_required("psysmysql.change_product", login_url="login"),
    ],
    name="dispatch",
)
class Update(View):
    template_name = "updateproduct.html"

    def get_context_data(
        self, request, formsearch=None, formupdate=None, productsearch=None
    ):
        if formsearch is None:
            formsearch = SearchProduct()
        if formupdate is None:
            formupdate = ProductForm()

        return {
            "form": formsearch,
            "formupdate": formupdate,
            "productsearch": productsearch,
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if "search" in request.POST:
            return self._handle_search_product(request)
        elif "update" in request.POST:
            return self._handle_update_product(request)
        else:
            messages.error(
                request,
                "Acción POST no reconocida. Asegúrate de que el botón tenga un atributo 'name'.",
            )
            context = self.get_context_data(request)
            return render(request, self.template_name, context)

    def _handle_search_product(self, request):
        formsearch = SearchProduct(request.POST)
        formupdate = ProductForm()

        if formsearch.is_valid():
            namesearch = formsearch.cleaned_data["name"]
            productfound = Products.objects.get(name=namesearch)

            if productfound:
                productsearch = productfound  # Obtén el objeto real
                request.session["original_name"] = namesearch

                # ¡LA CLAVE ESTÁ AQUÍ! Inicializa formupdate con la instancia del producto encontrado
                formupdate = ProductForm(instance=productsearch)
                print(productfound)
            else:
                messages.error(request, "No se encontraron productos con ese nombre.")
                productsearch = None
        else:
            messages.error(
                request,
                "Por favor, corrige los errores en el formulario de búsqueda.",
            )
        context = self.get_context_data(
            request,
            formsearch=formsearch,
            formupdate=formupdate,
            productsearch=productsearch,
        )

        return render(request, "updateproduct.html", context)

    def _handle_update_product(self, request):
        original_name = request.session.get("original_name")
        productsearch = None

        if not original_name:
            messages.error(request, "No hay producto con ese nombre")
            context = self.get_context_data(request)
            return render(request, self.template_name, context)

        formupdate = ProductForm(request.POST)
        formsearch = SearchProduct()

        if formupdate.is_valid():
            new_name = formupdate.cleaned_data["name"]
            new_price = formupdate.cleaned_data["price"]
            new_description = formupdate.cleaned_data["description"]

            original_name = request.session.get("original_name")
            try:
                productupdate = Products.objects.get(name=original_name)

                if productupdate:
                    productupdate.name = new_name
                    productupdate.price = new_price
                    productupdate.description = new_description
                    productupdate.save()
                    messages.info(request, "Actualización exitosa")

                    request.session["original_name"] = None
                    productsearch = None
                else:
                    messages.error(
                        request,
                        "Fallo en la Actualización: Producto no encontrado.",
                    )

            except Exception as e:
                messages.error(request, f"Error durante la actualización: {e}")
        else:
            messages.error(
                request,
                "Por favor, corrige los errores en el formulario de actualización.",
            )
            if original_name:
                try:
                    productsearch = Products.objects.get(name=original_name)
                except Products.DoesNotExist:
                    productsearch = None
        formupdate = ProductForm()
        context = self.get_context_data(
            request,
            formsearch=formsearch,
            formupdate=formupdate,
            productsearch=productsearch,
        )
        return render(request, "updateproduct.html", context)


def update_product_done(request):
    return render(request, "updateproductdone.html")


# Ventas
@method_decorator(
    [
        login_required(login_url="login"),
        permission_required("psysmysql.add_sell", login_url="login"),
    ],
    name="dispatch",
)
class SellProductView(View):
    template_name = "sellproduct.html"

    def get_context_data(self, request):
        """
        Método auxiliar para preparar el contexto que se enviará a la plantilla.
        Ahora centraliza la lógica para GET y maneja la búsqueda de clientes.
        """
        formsell = SellForm()
        sentform = SentSellForm()
        formregsitersell = RegisterSellDetailForm()
        list_sell_products = SellProducts.objects.all()

        list_items = []
        total_acumulado_temp = 0

        for item in list_sell_products:
            item_total = item.quantity * item.priceunitaty
            total_acumulado_temp += item_total

            list_items.append(
                {
                    "id_product": item.idproduct.pk,
                    "name": item.idproduct.name,
                    "quantity": item.quantity,
                    "price": float(item.priceunitaty),
                    "pricexquantity": float(item_total),
                }
            )

        quantity_dict = sum(item["quantity"] for item in list_items)
        price_dict = sum(item["price"] for item in list_items)
        price_x_quantity = sum(item["pricexquantity"] for item in list_items)

        formsearch = SearchEmailForm(request.GET or None)
        search_results = []
        search_query = None

        if formsearch.is_valid():
            search_query = formsearch.cleaned_data["query"]
            if search_query:
                search_results = Clients.objects.filter(
                    Q(email__icontains=search_query)
                ).distinct()

        context = {
            "formsell": formsell,
            "sentform": sentform,
            "formregsitersell": formregsitersell,
            "list_sell_products": list_sell_products,
            "list_items_json": json.dumps(list_items),
            "quantity": quantity_dict,
            "price": price_dict,
            "price_x_quantity": price_x_quantity,
            "formsearch": formsearch,
            "search_query": search_query,
            "search_results": search_results,
        }
        return context

    def get(self, request, *args, **kwargs):
        """Maneja las solicitudes GET (cuando se carga la página inicialmente)."""
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if "sell" in request.POST:
            return self._handle_sell_form(request)
        elif "sent" in request.POST:
            return self._handle_sent_form(request)
        elif "add" in request.POST:
            return self._handle_add_form(request)
        else:
            messages.error(
                request,
                "Acción POST no reconocida. Asegúrate de que el botón tenga un atributo 'name'.",
            )
            context = self.get_context_data(request)
            return render(request, self.template_name, context)

    def _handle_sell_form(self, request):
        """Lógica para el formulario 'sell'."""
        formsell = SellForm(request.POST)
        if formsell.is_valid():
            totalsell = formsell.cleaned_data["totalsell"]
            idproduct = formsell.cleaned_data["id_product"]

            try:
                productsell = Sell(
                    totalsell=totalsell,
                    id_product=idproduct,
                )
                productsell.save()
            except Exception as e:
                messages.error(request, f"Error al registrar la venta: {e}")
            return redirect("sell_product")
        else:
            for field, errors in formsell.errors.items():
                for error in errors:
                    messages.error(request, f"Error en '{field}': {error}")
            return redirect("sell_product")

    def _handle_sent_form(self, request):
        """Lógica para el formulario 'sent'."""
        sentform = SentSellForm(request.POST)

        if sentform.is_valid():
            productsell = Sell.objects.all()

            data = []
            for item in productsell:
                data.append(
                    {
                        "id": item.idsell,
                        "dateSell": timezone.localtime(item.datesell).isoformat(),
                        "totalsell": item.totalsell,
                        "id_product": item.id_product_id,
                    }
                )
            request.session["data_json_sell"] = data

            all_data = request.session.get("data_json_sell", [])
            client_email_to_send = request.POST.get(
                "client_email_selected"
            )  # Obtén el correo del campo oculto

            email_subject = "Confirmación de Venta - Su Compra"
            email_message = str(all_data)

            for item in all_data:
                product_id = item["id_product"]
                quantity = item["totalsell"]
                if not product_id or quantity is None:
                    messages.error(
                        request,
                        f"Faltan datos para enviar el producto (ID {product_id} de producto o cantidad{quantity}).",
                    )
                    return redirect("sell_product")
                try:
                    product_stock = Stock.objects.get(id_products=product_id)
                    if product_stock.quantitystock == 0:
                        messages.error(
                            request, f"El stock del producto ID {product_id} es cero."
                        )
                    elif product_stock.quantitystock < quantity:
                        messages.warning(
                            request,
                            f"Solo quedan {product_stock.quantitystock} unidades del producto ID {product_id} en stock. No se pudo enviar {quantity} unidades.",
                        )
                    else:
                        product_stock.quantitystock -= quantity
                        product_stock.save()

                except Stock.DoesNotExist:
                    messages.error(
                        request,
                        f"Producto ID {product_id} no encontrado en stock.",
                    )
                except DatabaseError as e:
                    messages.error(
                        request,
                        f"Error en la base de datos al actualizar stock para el producto ID {product_id}: {e}",
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f"Ocurrió un error inesperado para el producto ID {product_id}: {e}",
                    )

            SellProducts.objects.all().delete()
            messages.success(request, "Proceso de envío de ventas completado.")
            if client_email_to_send:
                send_sell_confirmation_email.delay(
                    client_email_to_send, email_subject, email_message
                )
                messages.info(
                    request,
                    f"Se inició el envío de correo de confirmación a {client_email_to_send}.",
                )
            else:
                messages.warning(
                    request,
                    "No se proporcionó un correo de cliente para enviar la confirmación.",
                )

            return redirect("sell_product")
        else:
            for field, errors in sentform.errors.items():
                for error in errors:
                    messages.error(
                        request,
                        f"Error en el formulario de envío '{field}': {error}",
                    )
            return redirect("sell_product")

    def _handle_add_form(self, request):
        """Lógica para el formulario 'add'."""
        formregsitersell = RegisterSellDetailForm(request.POST)
        if formregsitersell.is_valid():
            type_pay = formregsitersell.cleaned_data["type_pay"]
            state_sell = formregsitersell.cleaned_data["state_sell"]
            notes = formregsitersell.cleaned_data["notes"]

            list_sell_products = SellProducts.objects.all()

            list_items = []
            total_sale_calculated = 0

            for item in list_sell_products:
                item_total = item.quantity * item.priceunitaty
                total_sale_calculated += item_total

                list_items.append(
                    {
                        "id_product": item.idproduct.pk,
                        "name": item.idproduct.name,
                        "quantity": item.quantity,
                        "price": float(item.priceunitaty),
                        "pricexquantity": float(item_total),
                    }
                )

            id_employed = (
                request.user.username if request.user.is_authenticated else "anonymous"
            )

            register_sell = RegistersellDetail(
                id_employed=id_employed,
                total_sell=total_sale_calculated,
                type_pay=type_pay,
                state_sell=state_sell,
                notes=notes,
                detail_sell=json.dumps(list_items),
            )
            try:
                register_sell.save()
            except DatabaseError as e:
                messages.error(
                    request,
                    f"Error en la base de datos al registrar el detalle de venta: {e}",
                )
            except Exception as e:
                messages.error(
                    request,
                    f"Ocurrió un error inesperado al registrar el detalle de venta: {e}",
                )

            return redirect("sell_product")
        else:
            for field, errors in formregsitersell.errors.items():
                for error in errors:
                    messages.error(
                        request,
                        f"Error en el formulario de registro de venta '{field}': {error}",
                    )
            return redirect("sell_product")


def listallsellregisterview(request):
    listallregister = RegistersellDetail.objects.all()
    return render(request, "listallsellregister.html", {"list": listallregister})


# función para mostrar los datos de los registros de ventas.
def detailregisterview(request, pk):
    register_sell_instance = get_object_or_404(RegistersellDetail, idsell=pk)

    detail_products_list = []
    # Verificamos que register_sell_instance no este vacio y que tambien sea una instancia o un objecto de python.
    if register_sell_instance.detail_sell and isinstance(
        register_sell_instance.detail_sell, str
    ):
        try:
            # Decodificación de los datos de tipo Json.
            detail_products_list = json.loads(register_sell_instance.detail_sell)
        except json.JSONDecodeError:
            print(f"Error: detail_sell para idsell={pk} no es JSON válido.")

    context = {
        "register_sell_instance": register_sell_instance,
        "detail": detail_products_list,
    }
    print(detail_products_list)
    return render(request, "listdetailsellregister.html", context)


def delete_sell_item(request, pk):
    sell_detail_item = get_object_or_404(SellProducts, pk=pk)

    if request.method == "POST":
        pass
    else:
        sell_detail_item.delete()

        return redirect("sell_product")
    return render(request, "deletesellitem.html", {"item", sell_detail_item})


def list_product_sell(request):
    list_sell_products = SellProducts.objects.all()
    context = {"list_sell_products": list_sell_products}
    return render(request, "listsellproducts.html", context)


@login_required
@permission_required("psysmysql.add_stock", login_url="error")
def register_stock(request):
    if request.method == "POST":
        stockform = StockForm(request.POST)
        list_stock = None
        if stockform.is_valid():
            id_product_instance = stockform.cleaned_data["id_products"]
            quantitystock = stockform.cleaned_data["quantitystock"]
            try:
                # get_or_create se utiliza para verificar si un objeto existe y si no existe lo crea.
                stock_item, created = Stock.objects.get_or_create(
                    id_products=id_product_instance,
                    defaults={"quantitystock": quantitystock},
                )
                if not created:
                    stock_item.quantitystock += quantitystock
                    stock_item.save()
                    messages.success(request, "stock actualizado")
                else:
                    messages.success(request, "nuevo stock")

                return redirect("stock_products")
            except DatabaseError as e:
                messages.error(request, f"{e}")
            except Exception as e:
                messages.error(request, f"{e}")
        else:
            messages.error(request, "Error al guardar el producto")
            return redirect("stock_products")
    else:
        stockform = StockForm()
        list_stock = Stock.objects.all().order_by("quantitystock")
    return render(
        request,
        "stock.html",
        {"form": stockform, "list_stock": list_stock},
    )


def list_stock(request):
    list_stock = Stock.objects.filter("name")
    return render(request, "liststock.html", {"list_stock": list_stock})


def page_404(request):
    wait_time = 5
    return render(request, "404.html", {"wait_time": wait_time})


@login_required
@permission_required("auth.change_user", raise_exception=True)
def assign_user_to_group(request):
    if request.method == "POST":
        form = AssginUserToGroupForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            selected_groups = form.cleaned_data["groups"]

            user.groups.set(selected_groups)

            messages.success(
                request,
                f"Usuario '{user.username}' actualizado en los grupos con éxito",
            )
            return redirect("assing_user")
    else:
        form = AssginUserToGroupForm()
    users_with_groups = (
        User.objects.all().order_by("username").prefetch_related("groups")
    )

    context = {
        "form": form,
        "title": "Asignar usuario a grupo",
        "users_with_groups": users_with_groups,
    }

    return render(request, "assing_user.html", context)


def register_clients(request):
    if request.method == "POST":
        formclients = ClientsForm(request.POST)
        if formclients.is_valid():
            name = formclients.cleaned_data["name"]
            email = formclients.cleaned_data["email"]
            direction = formclients.cleaned_data["direction"]
            telephone = formclients.cleaned_data["telephone"]
            nit = formclients.cleaned_data["nit"]
            country = formclients.cleaned_data["country"]
            departament = formclients.cleaned_data["departament"]
            city = formclients.cleaned_data["city"]

            new_client = Clients(
                name=name,
                email=email,
                direction=direction,
                nit=nit,
                telephone=telephone,
                country=country,
                departament=departament,
                city=city,
            )

            new_client.save()

            return redirect("register_client")
        else:
            return redirect("register_client")
    else:
        formclients = ClientsForm()
        return render(request, "registerclients.html", {"formclients": formclients})
