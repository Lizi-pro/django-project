from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm


from decimal import Decimal

from .forms import RegisterForm
from .models import Category, Product, Basket, BasketItem


# MENU PAGE

def menu_view(request):

    # კატეგორიები და პროდუქტები მოგვაქვს ჩვენი ბაზიდან
    categories = Category.objects.all().order_by("id")
    products = Product.objects.select_related("category").all()

    # ფილტრების მნიშვნელობები URL-იდან
    category_id = request.GET.get("category", "all")
    spiciness = request.GET.get("spiciness", "4")
    nuts = request.GET.get("nuts", "")
    vegetarian = request.GET.get("vegetarian", "")

    # სიმწარის მაქსიმალური დონის შემოწმება
    try:
        max_spiciness = max(0, min(4, int(spiciness)))
    except (TypeError, ValueError):
        max_spiciness = 4

    # პროდუქტების ფილტრაცია
    products = products.filter(spiciness__lte=max_spiciness)

    # კატეგორიის ფილტრი
    if category_id not in ("", "all"):
        try:
            products = products.filter(category_id=int(category_id))
        except (TypeError, ValueError):
            category_id = "all"

    # თხილის არქონის ფილტრი
    if nuts == "true":
        products = products.filter(nuts=False)

    # ვეგეტარიანული პროდუქტების ფილტრი
    if vegetarian == "true":
        products = products.filter(vegetarian=True)

    context = {
        "categories": categories,
        "products": products,
        "selected_category": category_id,
        "selected_spiciness": max_spiciness,
        "nuts_selected": nuts == "true",
        "vegetarian_selected": vegetarian == "true",
    }

    return render(request, "menu/index.html", context)


# ADD PRODUCT TO CART

@login_required(login_url="login")
@require_POST
def add_to_cart_view(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    # ვპოულობთ მომხმარებლის კალათას ან ვქმნით ახალს
    basket, created = Basket.objects.get_or_create(user=request.user)

    # ვამოწმებთ, არის თუ არა პროდუქტი უკვე კალათაში
    basket_item, created = BasketItem.objects.get_or_create(
        basket=basket,
        product=product,
        defaults={
            "quantity": 1,
            "price": product.price,
        }
    )

    # თუ პროდუქტი უკვე არსებობდა, რაოდენობას ვზრდით
    if not created:
        basket_item.quantity += 1
        basket_item.save(update_fields=["quantity"])

    return redirect("cart")


# CART PAGE

@login_required(login_url="login")
def cart_view(request):

    # მხოლოდ მიმდინარე მომხმარებლის კალათა
    basket = Basket.objects.filter(user=request.user).first()

    cart_items = []
    total = Decimal("0.00")

    if basket:
        items = basket.items.select_related("product").all()

        for item in items:
            subtotal = item.price * item.quantity
            total += subtotal

            cart_items.append({
                "product_id": item.product.id,
                "name": item.product.name,
                "image": item.product.image,
                "price": item.price,
                "quantity": item.quantity,
                "subtotal": subtotal,
            })

    context = {
        "cart_items": cart_items,
        "total": total,
    }

    return render(request, "menu/cart.html", context)


# UPDATE CART QUANTITY

@login_required(login_url="login")
@require_POST
def update_cart_view(request, product_id):

    try:
        quantity = int(request.POST.get("quantity", "1"))

        if quantity < 1:
            return HttpResponse(
                "Quantity must be at least 1.",
                status=400,
            )

    except (ValueError, TypeError):
        return HttpResponse(
            "Invalid quantity.",
            status=400,
        )

    basket = get_object_or_404(Basket, user=request.user)

    # ვეძებთ პროდუქტს მხოლოდ ამ მომხმარებლის კალათაში
    basket_item = get_object_or_404(
        BasketItem,
        basket=basket,
        product_id=product_id,
    )

    basket_item.quantity = quantity
    basket_item.save(update_fields=["quantity"])

    return redirect("cart")


# DELETE PRODUCT FROM CART

@login_required(login_url="login")
@require_POST
def delete_from_cart_view(request, product_id):

    basket = get_object_or_404(Basket, user=request.user)

    # წაიშლება მხოლოდ მიმდინარე მომხმარებლის კალათიდან
    basket_item = get_object_or_404(
        BasketItem,
        basket=basket,
        product_id=product_id,
    )

    basket_item.delete()

    return redirect("cart")


# USER REGISTRATION

def register_view(request):

    if request.user.is_authenticated:
        return redirect("menu")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("menu")

    else:
        form = RegisterForm()

    return render(request, "menu/register.html", {"form": form})


# USER LOGIN

def login_view(request):

    if request.user.is_authenticated:
        return redirect("menu")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect("menu")

    else:
        form = AuthenticationForm()

    return render(request, "menu/login.html", {"form": form})


# USER LOGOUT

def logout_view(request):

    if request.method == "POST":
        logout(request)

    return redirect("menu")
