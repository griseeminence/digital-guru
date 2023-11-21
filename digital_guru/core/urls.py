from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import HomeListView, ItemDetailView, CheckoutView, add_to_cart, remove_from_cart, OrderSummeryView, \
    remove_single_item_from_cart, PaymentView, AddCouponView

app_name = 'core'

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('detail/<slug>/', ItemDetailView.as_view(), name='detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('order-summary/', OrderSummeryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
]