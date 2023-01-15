from django.shortcuts import render
#-- my imports --#
from store.models import Product, ReviewRating

def _get_all_products_reviews(products):
    for product in products:
        return ReviewRating.objects.filter(product_id=product.id, status=True)
    
    return ReviewRating.objects.filter(product_id=product.id, status=True)

def home(request):
    products = Product.objects.filter(is_available=True).order_by('created_date')
    reviews = _get_all_products_reviews(products)
    
    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request, "home.html", context)
