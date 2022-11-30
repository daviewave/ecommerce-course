from django.shortcuts import render
#-- my imports --#
from store.models import Product

def home(request):
    products = Product.objects.all().filter(is_available=True) # Only bring the available products
    context = {
        'products': products,
    }


    return render(request, "home.html", context)
