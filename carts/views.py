from django.shortcuts import render, redirect, HttpResponse
from store.models import Product, Variation
from .models import Cart, CartItem

#-- Helper Methods --#
def _get_product_based_by_ID(product_id):
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

def _calculate_total_and_quantities(cart_items):
    total = 0
    quantity = 0    
    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity

    return total, quantity

def _is_variation_in_cart(product, cart):
    return CartItem.objects.filter(product=product, cart=cart).exists()

def _get_cart_items_ids_and_existing_variations(cart_item, ):
    ids = []
    existing_variations = []
    for item in cart_item:
        existing_variation = item.variations.all()
        existing_variations.append(list(existing_variation))
        ids.append(item.id)
    return ids, existing_variations

def _create_new_cart_item(product, cart):
    return CartItem.objects.create(product=product, quantity=1, cart=cart)

def get_product_variations(request, product):
    product_variations = []
    if request.method == 'POST':    
        for variation_item in request.POST:
            variation_category = variation_item
            variation_category_value = request.POST[variation_category]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=variation_category, variation_value__iexact=variation_category_value)
                product_variations.append(variation)
            except:
                pass
    return product_variations

def handle_duplicate_products(existing_variations, ids, product, cart):
    pass

#-- Major Endpoints --#
def add_to_cart(request, product_id):
    # 1.
    product = _get_product_based_by_ID(product_id)
    
    # 2. 
    product_variations = get_product_variations(request, product)

    # 3. 
    cart = _get_current_users_cart(request)

    # 4. 
    if _is_variation_in_cart(product, cart):
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        ids, existing_variations = _get_cart_items_ids_and_existing_variations(cart_item)

        if product_variations in existing_variations:
            index = existing_variations.index(product_variations)
            item_id = ids[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if len(product_variations) > 0:
                item.variations.clear()
                item.variations.add(*product_variations)
            item.save()
    else:
        cart_item = _create_new_cart_item(product, cart)
        if len(product_variations) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variations)
        cart_item.save()
    
    return redirect('cart')

def remove_from_cart(request, product_id, cart_item_id):
    product = Product.objects.get(id=product_id)
    cart = _get_current_users_cart(request)
    # cart_item = CartItem.objects.get(product=product, cart=cart)

    # create seperate function
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else: 
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_all_cart_item(request, product_id, cart_item_id):
    cart = _get_current_users_cart(request)
    product = Product.objects.get(id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    # create seperate function
    try: 
        cart = Cart.objects.get(cart_id=_get_session_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total, quantity = _calculate_total_and_quantities(cart_items)        
        tax = _apply_tax(total, 2)
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

def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    # create seperate function
    try: 
        cart = Cart.objects.get(cart_id=_get_session_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total, quantity = _calculate_total_and_quantities(cart_items)        
        tax = _apply_tax(total, 2)
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

    return render(request, 'store/checkout.html', context)