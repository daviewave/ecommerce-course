from django.urls import path
#-- my imports --#
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
]

# app_name = 'store'

