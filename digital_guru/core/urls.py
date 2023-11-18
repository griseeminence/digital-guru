from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import HomeListView, ItemDetailView, checkout, add_to_cart, remove_from_cart, OrderSummeryView, remove_single_item_from_cart

app_name = 'core'

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('detail/<slug>/', ItemDetailView.as_view(), name='detail'),
    path('checkout/', checkout, name='checkout'),
    path('order-summary/', OrderSummeryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
]