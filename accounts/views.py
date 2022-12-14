from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# verification sent email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes   
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from ecommerce_course import settings


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

            # send_mail(
            #     mail_subject,
            #     message,
            #     settings.EMAIL_HOST_USER,
            #     [to_email],
            #     fail_silently=False
            # )
            messages.success(request, 'Success! Account Successfully Registered!')
            return redirect('register')
    else:
        form = RegistrationForm()
            
    context = {
        "form": form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You have successfully logged in.")
            # return redirect('home')
        else:
            messages.error(request, "Invalid login credentials provided.")

    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have logged out.')
    return redirect('login')

def activate(request, uidb64, token):
    return HttpResponse('SUCCESS')