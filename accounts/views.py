from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, AccountForm, UserProfileForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from orders.models import Order

# verification sent email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes   
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from carts.models import Cart, CartItem
from store.models import Product
from accounts.models import UserProfile



def _get_cart_items_ids_and_existing_variations(cart_items):
    ids = []
    existing_variations = []
    for item in cart_items:
        existing_variation = item.variations.all()
        existing_variations.append(list(existing_variation))
        ids.append(item.id)
    return ids, existing_variations

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

def _is_variation_in_cart(cart):
    return CartItem.objects.filter(cart=cart).exists()

def _get_product_based_by_ID(product_id):
    return Product.objects.get(id=product_id)

#-- Major Endpoints --#
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)    
        if form.is_valid():
            first_name      = form.cleaned_data['first_name']
            last_name       = form.cleaned_data['last_name']
            phone_number    = form.cleaned_data['phone_number']
            email           = form.cleaned_data['email']
            username        = email.split('@')[0]
            password        = form.cleaned_data['password']

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()


            # Create User Profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user-pic.png'
            profile.save()




            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'ACCOUNT ACTIVATION'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Success! Account Registered! An activation link was sent to the email provided, activate to log in.')
            return redirect('/accounts/login/?command=verification&email=' + email)
    else:
        form = RegistrationForm()
            
    context = {
        "form": form,
    }
    return render(request, 'accounts/register.html', context)

# def combine_session_to_user_cart_variations():


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = _get_current_users_cart(request)
                if _is_variation_in_cart(cart):
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    # Getting the product variation by ID
                    product_variations = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variations.append(list(variation))

                    # Get the cart items from the Users product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ids, existing_variations = _get_cart_items_ids_and_existing_variations(cart_item)

                    for product in product_variations:
                        if product in existing_variations:
                            index = existing_variations.index(product)
                            item_id = ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You have successfully logged in.")
            url = request.META.get('HTTP_REFERER') # NOTE: returns us to the url we had before this page
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&')) # NOTE: this removes the '=' from the query to be used as a param
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)                
            except:
                return redirect('dashboard') 
        else:
            messages.error(request, "Invalid login credentials provided.")

    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have logged out.')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid) #NOTE: this returns the user object
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    num_orders = orders.count()

    context = {
        'num_orders': num_orders,
    }

    return render(request, 'accounts/dashboard.html', context)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email):
            user = Account.objects.get(email__exact=email) #NOTE: '__exact' is the case sensitive way
            # user = Account.objects.get(email__iexact=email) #NOTE: '__iexact' doesn't care about case sensitivity
            
            # RESET PASSWORD EMAIL
            current_site = get_current_site(request)
            mail_subject = 'GreatKart: Reset password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Error! No existing account found with the email you submitted.')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid) #NOTE: this returns the user object
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('reset_password')
    else:
        messages.error(request, 'Error. This link has expired.')
        return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password) #NOTE: must use of this as it hashes the password for security reasons-- cannot just .save() 
            user.save()
            messages.success(request, 'Password has successfully been reset.')
            return redirect('login')
        else: 
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')

    return render(request, 'accounts/reset_password.html')

def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at') # NOTE: hyphen means descending order

    context = {
        'orders': orders
    }
    return render(request, 'accounts/my_orders.html', context)

def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = AccountForm(request.POST, instance=request.user) #NOTE: instance updates existing
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = AccountForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'user_profile_form': user_profile_form,
        'user_profile': user_profile,         
    }
    return render(request, 'accounts/edit_profile.html', context)

