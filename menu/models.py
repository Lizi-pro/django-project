from django.db import models
from django.conf import settings

# კატეგორიების ცხრილი
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):      # განსაზღვრავს როგორ გამოჩნდება კატეგორია Admin-ში
        return self.name


# პროდუქტების ცხრილი
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    nuts = models.BooleanField(default=False)
    image = models.URLField(max_length=500)
    vegetarian = models.BooleanField(default=False)
    spiciness = models.IntegerField(default=0)

    category = models.ForeignKey(
        Category,                    # თითოეული პროდუქტი დაკავშირებულია ერთ კატეგორიასთან
        on_delete=models.PROTECT,    # არ გვაძლევს კატეგორიის წაშლის საშუალებას, სანამ ამ კატეგორიაში პროდუქტები არსებობს
        related_name="products"      # კატეგორიასთან დაკავშირებულ ყველა პროდუქტს ვიღებთ
    )

    def __str__(self):
        return self.name


# კალათების ცხრილი
class Basket(models.Model):
    user = models.OneToOneField(       # ერთ კალათას მხოლოდ ერთი მომხმარებელი ეკუთვნის
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,      # მომხმარებლის წაშლისას მისი კალათაც წაიშლება
        related_name="basket"
    )

    created_at = models.DateTimeField(auto_now_add=True)    # კალათის შექმნის თარიღი და დრო ავტომატურად შეინახება

    def __str__(self):
        return f"{self.user}'s basket"


# კალათაში მოთავსებული პროდუქტების ცხრილი
class BasketItem(models.Model):
    basket = models.ForeignKey(        # მიუთითებს რომელ კალათას ეკუთვნის ეს ჩანაწერი
        Basket,
        on_delete=models.CASCADE,       # კალათის წაშლისას მისი პროდუქტებიც წაიშლება
        related_name="items"
    )

    product = models.ForeignKey(         # მიუთითებს რომელი პროდუქტია კალათაში
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(                   # ერთი და იგივე პროდუქტი ერთ კალათაში მხოლოდ ერთ ჩანაწერად ინახება
                fields=["basket", "product"],
                name="unique_product_per_basket"
            )
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"



