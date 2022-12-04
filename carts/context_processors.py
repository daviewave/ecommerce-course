from .admin import admin
from .models import Cart, CartItem
from .views import _get_session_id

def calculate_number_of_items(cart_items):
    num_items = 0
    for item in cart_items:
        num_items = num_items + item.quantity
    return num_items

def shopping_cart_counter(request):
    if 'admin' in request.path:
        print('NOT COUNTING ADMIN PAGE')
        return() 
    else: 
        try: 
            cart = Cart.objects.filter(cart_id=_get_session_id(request))
            cart_items = CartItem.objects.filter(cart=cart[:1])
            num_items = calculate_number_of_items(cart_items)
        except Cart.DoesNotExist:
            num_items = 0
    return dict(num_items=num_items)