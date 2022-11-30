from django.urls import path
#-- my imports --#
from . import views

urlpatterns = [
    path('', views.store, name='store')
]
