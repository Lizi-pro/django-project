from django.contrib import admin
from .models import Category, Product, Basket, BasketItem


@admin.register(Category)             # Category მოდელის რეგისტრაცია Django Admin-ში
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)                   # Product მოდელის რეგისტრაცია Django Admin-ში
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "category",
        "vegetarian",
        "nuts",
        "spiciness",
    )

    list_filter = ("category", "vegetarian", "nuts", "spiciness")
    search_fields = ("name",)


admin.site.register(Basket)            # კალათებისა და კალათის პროდუქტების რეგისტრაცია Admin-ში
admin.site.register(BasketItem)
