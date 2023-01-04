from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from orders.models import Order
import datetime


def _calculate_total_and_quantities(cart_items):
    total = 0
    quantity = 0    
    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity

    return total, quantity

def _apply_tax(tax_percentage, total_amount):
    return (tax_percentage * total_amount) / 100

def _calculate_grand_total(total, tax):
    return total + tax

def _check_if_shopping_cart_empty(cart_items):
    if cart_items.count() <= 0:
        return redirect('store')
    return

def _collect_form_data(request, user, tax, grand_total):
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

                data.tax            = tax
                data.order_total    = grand_total
                data.ip_addr        = request.META.get('REMOTE_ADDR')
                data.save()

                # Generate order number
                year            = int(datetime.date.today().strftime('%Y'))
                month           = int(datetime.date.today().strftime('%m'))
                day             = int(datetime.date.today().strftime('%d'))
                today           = datetime.date(year, month, day)
                current_date    = today.strftime("%Y%m%d")

                order_number        = current_date + str(data.id)
                data.order_number   = order_number

                data.save()
                # return redirect('checkout')
        except Exception as invalid_form:
            raise(invalid_form)
            
def place_order(request, total=0, quantity=0):
    user = request.user
    
    cart_items = CartItem.objects.filter(user=user)
    _check_if_shopping_cart_empty(cart_items)

    total, quantity = _calculate_total_and_quantities(cart_items)
    
    grand_total, tax = 0, 0
    tax = _apply_tax(total, 2)
    grand_total = _calculate_grand_total(total, tax)

    _collect_form_data(request, user, tax, grand_total)
    return redirect('checkout')