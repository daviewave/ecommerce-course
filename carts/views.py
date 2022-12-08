from django.shortcuts import render, redirect, HttpResponse
from store.models import Product
from .models import Cart, CartItem

def get_product_based_by_ID(product_id):
    return Product.objects.get(id=product_id)

def _get_session_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def _get_current_users_cart(request):
    try: 
        cart = Cart.objects.get(cart_id=_get_session_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_get_session_id(request))
    cart.save()
    return cart

def _apply_tax(tax_percentage, total_amount):
    return (tax_percentage * total_amount) / 100

def _calculate_grand_total(total, tax):
    return total + tax

def calculate_total_and_quantities(cart_items):
    total = 0
    quantity = 0    
    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity

    return total, quantity

def add_to_cart(request, product_id):
    color = request.GET['color']
    size = request.GET['size']
    print(color)
    print(size)
    
    product = get_product_based_by_ID(product_id)
    cart = _get_current_users_cart(request)
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product, 
            quantity=1, 
            cart=cart
        )
        cart_item.save()
    return redirect('cart')

def remove_from_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart = _get_current_users_cart(request)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else: 
        cart_item.delete()
    return redirect('cart')

def remove_all_cart_item(request, product_id):
    cart = _get_current_users_cart(request)
    product = Product.objects.get(id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try: 
        cart = Cart.objects.get(cart_id=_get_session_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total, quantity = calculate_total_and_quantities(cart_items)        
        tax = _apply_tax(2, total)
        grand_total = _calculate_grand_total(total, tax)

    except Cart.DoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }

    return render(request, 'store/cart.html', context)