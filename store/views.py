from django.shortcuts import render, redirect
from .models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from carts.views import _get_session_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages

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

def get_previous_page_url(request):
    return request.META.get('HTTP_REFERER')

def get_users_review(user, product_id):
    return ReviewRating.objects.get(user__id=user, product__id=product_id)

def get_review_instances(request, reviews):
    return ReviewForm(request.POST, instance=reviews)

def save_review_form_data(request, form, url, product_id):
    data = ReviewRating()
    data.subject = form.cleaned_data['subject']
    data.rating = form.cleaned_data['rating']
    data.review = form.cleaned_data['review']
    data.ip = request.META.get('REMOTE_ADDR')
    data.product_id = product_id
    data.user_id = request.user.id
    data.save()
    messages.success(request, 'Thank you! Your review has been submitted')
    return redirect(url)



def handle_review_form_data(request, user, url, product_id):
    try:
        reviews = get_users_review(user, product_id)
        form = get_review_instances(request, reviews)
        form.save()
        messages.success(request, 'Thank you! Your review has been updated')
        return redirect(url)
    except ReviewRating.DoesNotExist:
        form = ReviewForm(request.POST)
        if form.is_valid():
            save_review_form_data(request, user, url, product_id)


def submit_review(request, product_id):
    url = get_previous_page_url(request)
    if request.method == 'POST':
        handle_review_form_data(request, request.user, url, product_id)

