from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
from django.views.decorators.http import require_POST
from decimal import Decimal

BASE_URL = "https://restaurant.stepprojects.ge/api"
TIMEOUT = 15


# API HELPER FUNCTIONS

def api_get(endpoint, params=None):
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def api_post(endpoint, data):
    response = requests.post(
        f"{BASE_URL}/{endpoint}",
        json=data,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response


def api_put(endpoint, data):
    response = requests.put(
        f"{BASE_URL}/{endpoint}",
        json=data,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response


def api_delete(endpoint):
    response = requests.delete(
        f"{BASE_URL}/{endpoint}",
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response


def api_error_message(error):
    if error.response is not None:
        return (
            f"API error: {error.response.status_code}. "
            f"{error.response.text}"
        )

    return str(error)



# MENU PAGE

def menu_view(request):
    try:
        categories = api_get("Categories/GetAll")
        products = api_get("Products/GetAll")

        category_id = request.GET.get("category", "all")
        spiciness = request.GET.get("spiciness", "4")
        nuts = request.GET.get("nuts", "")
        vegetarian = request.GET.get("vegetarian", "")

        try:
            max_spiciness = max(0, min(4, int(spiciness)))
        except (TypeError, ValueError):
            max_spiciness = 4

        filtered_products = []

        for product in products:

            # Filter by category
            if (
                category_id not in ("", "all")
                and str(product.get("categoryId")) != category_id
            ):
                continue

            # Filter by spiciness
            try:
                product_spiciness = int(product.get("spiciness", 0))
            except (TypeError, ValueError):
                product_spiciness = 0

            if product_spiciness > max_spiciness:
                continue

            # Filter by nuts
            if nuts == "true" and product.get("nuts", False):
                continue

            # Filter by vegetarian options
            if (
                vegetarian == "true"
                and not product.get("vegeterian", False)
            ):
                continue

            filtered_products.append(product)

        context = {
            "categories": categories,
            "products": filtered_products,
            "selected_category": category_id,
            "selected_spiciness": max_spiciness,
            "nuts_selected": nuts == "true",
            "vegetarian_selected": vegetarian == "true",
        }

        return render(request, "menu/index.html", context)

    except (requests.RequestException, ValueError) as error:
        return HttpResponse(
            f"Could not load the restaurant menu: {error}",
            status=502,
        )



# ADD PRODUCT TO CART

@require_POST
def add_to_cart_view(request, product_id):
    try:
        products = api_get("Products/GetAll")

        product = next(
            (
                item
                for item in products
                if int(item["id"]) == product_id
            ),
            None,
        )

        if product is None:
            return HttpResponse("Product not found.", status=404)

        basket = api_get("Baskets/GetAll")

        existing_item = next(
            (
                item
                for item in basket
                if int((item.get("product") or {}).get("id", -1)) == product_id
            ),
            None,
        )

        if existing_item:
            new_quantity = int(existing_item.get("quantity", 1)) + 1

            api_put(
                "Baskets/UpdateBasket",
                {
                    "productId": product_id,
                    "quantity": new_quantity,
                    "price": product["price"],
                },
            )

        else:
            api_post(
                "Baskets/AddToBasket",
                {
                    "productId": product_id,
                    "quantity": 1,
                    "price": product["price"],
                },
            )

        return redirect("cart")

    except (requests.RequestException, ValueError, TypeError) as error:
        return HttpResponse(
            f"Could not add the product to the cart: "
            f"{api_error_message(error) if isinstance(error, requests.RequestException) else error}",
            status=502,
        )



# CART PAGE

def cart_view(request):
    try:
        basket = api_get("Baskets/GetAll")

        cart_items = []
        total = Decimal("0.00")

        for item in basket:
            product = item.get("product") or {}

            quantity = int(item.get("quantity", 1))

            price = Decimal(str(item.get("price", product.get("price", 0))))

            subtotal = price * quantity
            total += subtotal

            cart_items.append(
                {
                    "product_id": product.get("id"),
                    "name": product.get("name", "Product"),
                    "image": product.get("image", ""),
                    "price": price,
                    "quantity": quantity,
                    "subtotal": subtotal,
                }
            )

        context = {
            "cart_items": cart_items,
            "total": total,
        }

        return render(request, "menu/cart.html", context)

    except (requests.RequestException, ValueError, TypeError,) as error:
        return HttpResponse(
            f"Could not load the cart: {error}",
            status=502,
        )



# UPDATE CART QUANTITY

@require_POST
def update_cart_view(request, product_id):
    try:
        quantity = int(request.POST.get("quantity", "1"))

        if quantity < 1:
            return HttpResponse(
                "Quantity must be at least 1.",
                status=400,
            )

        products = api_get("Products/GetAll")

        product = next(
            (
                item
                for item in products
                if int(item["id"]) == product_id
            ),
            None,
        )

        if product is None:
            return HttpResponse("Product not found.", status=404)

        api_put(
            "Baskets/UpdateBasket",
            {
                "productId": product_id,
                "quantity": quantity,
                "price": product["price"],
            },
        )

        return redirect("cart")

    except (ValueError, TypeError):
        return HttpResponse(
            "Invalid quantity.",
            status=400,
        )

    except requests.RequestException as error:
        return HttpResponse(
            f"Could not update the cart: {api_error_message(error)}",
            status=502,
        )



# DELETE PRODUCT FROM CART

@require_POST
def delete_from_cart_view(request, product_id):
    try:
        api_delete(f"Baskets/DeleteProduct/{product_id}")

        return redirect("cart")

    except requests.RequestException as error:
        return HttpResponse(
            f"Could not remove the product: "
            f"{api_error_message(error)}",
            status=502,
        )


