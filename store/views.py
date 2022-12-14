from django.shortcuts import render
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _get_session_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

#-- Helper Methods --#
def _get_single_product(category_slug, product_slug):
    try:
        return Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

def _is_already_in_cart(request, single_product):
    return CartItem.objects.filter(cart__cart_id=_get_session_id(request), product=single_product).exists()

def _get_paginated_products(request, products, num_products_per_page):
    paginator = Paginator(products, num_products_per_page)
    page = request.GET.get('page') #NOTE: gets the current page of products to be fetched 
    return paginator.get_page(page)

def handle_category_slug(request, category_slug):
    if category_slug != None:
        categories = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        num_prods = products.count()
        return products, num_prods
    else:
        non_paginated_products = Product.objects.filter(is_available=True).order_by('id')
        num_prods = non_paginated_products.count()
        products = _get_paginated_products(request, non_paginated_products, 4)
        return products, num_prods

#-- Major Endpoints --#
def product_detail(request, category_slug, product_slug):
    single_product = _get_single_product(category_slug, product_slug)
    is_in_cart = _is_already_in_cart(request, single_product)
      
    context = {
        'single_product': single_product,
        'is_in_cart': is_in_cart,
    }
    return render(request, 'store/product_detail.html', context)

def store(request, category_slug=None):
    products, num_prods = handle_category_slug(request, category_slug)
    context = {
        'products': products,
        'num_product': num_prods,
    }
    return render(request, 'store/store.html', context)

def search(request):
    # break down into smaller functions
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)) #NOTE: 'description__icontains' makes it return anything close to the keyword
            num_products = products.count() 

    context = {
        'products': products,
        "num_product": num_products,
    }
    return render(request, 'store/store.html', context)