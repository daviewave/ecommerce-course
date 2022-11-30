from django.shortcuts import render
from .models import Product

def store(request):
    products = Product.objects.filter(is_available=True)
    num_product = products.count()
    
    context = {
        'products': products,
        'num_product': num_product,
    }

    return render(request, 'store/store.html', context)
