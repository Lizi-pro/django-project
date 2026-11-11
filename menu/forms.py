from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):

    class Meta:
        model = User               # ფორმა დაკავშირებულია მომხმარებლის მოდელთან
        fields = ["username"]      # რეგისტრაციისას მომხმარებელს მხოლოდ Username-ს ვთხოვთ

    def clean_username(self):          # Username-ის დამატებითი ვალიდაცია
        username = self.cleaned_data.get("username")       # cleaned_data შეიცავს ვალიდაციის შედეგად მიღებულ მონაცემებს

        if User.objects.filter(username=username).exists():     # ვამოწმებთ, არსებობს თუ არა ასეთი Username მონაცემთა ბაზაში
            raise forms.ValidationError(
                "This username already exists. Please choose another one."
            )

        return username
