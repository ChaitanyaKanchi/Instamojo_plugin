from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('payment/', views.payment_form, name='payment_form'),
    path('payment/create/', views.create_payment_request, name='create_payment_request'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
]
