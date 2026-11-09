from django.contrib import admin
from .models import Category, Product, Basket, BasketItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
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


admin.site.register(Basket)
admin.site.register(BasketItem)
