from django.shortcuts import render
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _get_session_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        num_product = products.count()
    else:
        products = Product.objects.filter(is_available=True)
        paginator = Paginator(products, 4)
        page = request.GET.get('page') #NOTE: gets the current page of products to be fetched
        paged_products = paginator.get_page(page) #NOTE: this variable stores the paginated products
        num_product = products.count()
    
    context = {
        'products': paged_products,
        'num_product': num_product,
    }

    return render(request, 'store/store.html', context)

def get_single_product(category_slug, product_slug):
    try:
        return Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

def is_already_in_cart(request, single_product):
    return CartItem.objects.filter(cart__cart_id=_get_session_id(request), product=single_product).exists()


def product_detail(request, category_slug, product_slug):
    single_product = get_single_product(category_slug, product_slug)
    is_in_cart = is_already_in_cart(request, single_product)
      
    context = {
        'single_product': single_product,
        'is_in_cart': is_in_cart,
    }

    return render(request, 'store/product_detail.html', context)
