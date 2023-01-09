from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from orders.models import Order, OrderProduct, Payment
from store.models import Product
import datetime
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse

def _calculate_total_and_quantities(cart_items: CartItem):
    total = 0
    quantity = 0    
    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity

    return total, quantity

def _apply_tax(tax_percentage: float, total_amount: float):
    return (tax_percentage * total_amount) / 100

def _calculate_grand_total(total: float, tax: float):
    return total + tax

def _check_if_shopping_cart_empty(cart_items: CartItem):
    if cart_items.count() <= 0:
        return redirect('store')
    return

def _collect_form_data(request, user, tax: float, grand_total: float):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        try:
            if form.is_valid():
                data = Order()
                data.user = user
                data.first_name     = form.cleaned_data['first_name']
                data.last_name      = form.cleaned_data['last_name']
                data.email          = form.cleaned_data['email']
                data.phone          = form.cleaned_data['phone']
                data.addr_1         = form.cleaned_data['addr_1']
                data.addr_2         = form.cleaned_data['addr_2']
                data.city           = form.cleaned_data['city']
                data.state          = form.cleaned_data['state']
                data.country        = form.cleaned_data['country']
                data.order_note     = form.cleaned_data['order_note']
                data.zip_code       = form.cleaned_data['zip_code']

                data.tax            = tax
                data.order_total    = grand_total
                data.ip_addr        = request.META.get('REMOTE_ADDR')
                data.save()

                # Generate order number based on current data + the id
                # create seperate function called 'generate_order_number(data: Dict): -> order_number'
                year            = int(datetime.date.today().strftime('%Y'))
                month           = int(datetime.date.today().strftime('%m'))
                day             = int(datetime.date.today().strftime('%d'))
                today           = datetime.date(year, month, day)
                current_date    = today.strftime("%Y%m%d")

                order_number        = current_date + str(data.id)
                data.order_number   = order_number

                data.save()
                
                return Order.objects.get(user=user, is_ordered=False, order_number=order_number)

        except Exception as invalid_form:
            raise(invalid_form)
            
def place_order(request, total=0, quantity=0):
    user = request.user
    
    # make 1 common query method here
    cart_items = CartItem.objects.filter(user=user)
    _check_if_shopping_cart_empty(cart_items)

    total, quantity = _calculate_total_and_quantities(cart_items)
    
    grand_total, tax = 0, 0
    tax = _apply_tax(total, 2)
    grand_total = _calculate_grand_total(total, tax)

    order = _collect_form_data(request, user, tax, grand_total)

    context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'orders/payment.html', context)


def _get_user_order(user, body: dict):
    return Order.objects.get(user=user, is_ordered=False, order_number=body['orderID'])

def _get_user_order_total(order: dict):
    return order.order_total

def _create_payment(user, body: dict, order: dict):
    payment = Payment(
        user            = user,
        payment_id      = body['transactionID'],
        payment_method  = body['payment_method'],
        amount_paid     = _get_user_order_total(order),
        status          = body['status'],
    )
    payment.save()
    return payment

def _link_payment_to_order(order: dict, payment: dict):
    order.payment = payment

def _confirm_payment(order: dict):
    order.is_ordered = True
    order.save()

def get_current_user_cart(user):
    return CartItem.objects.filter(user=user)

def _link_foreign_keys_to_order_products(order_product, item):
    cart_item = CartItem.objects.get(id=item.id)
    product_variation = cart_item.variations.all()
    order_product = OrderProduct.objects.get(id=order_product.id)
    order_product.product_variation.set(product_variation)
    order_product.save()

def _save_products_in_cart_at_time_of_order(cart_items, user, order, payment):
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.account_id = user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.is_ordered = True
        order_product.save()

        _link_foreign_keys_to_order_products(order_product, item)
        
def _clear_cart_items(user):
    CartItem.objects.filter(user=user).delete()

def _send_order_confirmation_email_to_purchaser(user, order):
    mail_subject = 'Your order has been completed.'
    message = render_to_string('orders/order_confirmation_email.html', {
        'user': user,
        'order': order,
    })
    to_email = user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

def payment(request):
    body = json.loads(request.body)
    order = _get_user_order(request.user, body)
    payment = _create_payment(request.user, body, order)
    cart_items = get_current_user_cart(request.user)

    _link_payment_to_order(order, payment)
    _confirm_payment(order)
    _save_products_in_cart_at_time_of_order(cart_items, request.user, order, payment)
    _clear_cart_items(request.user)
    _send_order_confirmation_email_to_purchaser(request.user, order)
    
    data = {
        'order_number': order.order_number,
        'transactionID': payment.payment_id,
    }
    return JsonResponse(data)

def order_complete(request):
    return render(request, 'orders/order_complete.html')
