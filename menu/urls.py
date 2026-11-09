from django.urls import path

from . import views


urlpatterns = [
    path("", views.menu_view, name="menu"),

    path(
        "cart/",
        views.cart_view,
        name="cart",
    ),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart_view,
        name="add_to_cart",
    ),

    path(
        "cart/update/<int:product_id>/",
        views.update_cart_view,
        name="update_cart",
    ),

    path(
        "cart/delete/<int:product_id>/",
        views.delete_from_cart_view,
        name="delete_from_cart",
    ),
]
