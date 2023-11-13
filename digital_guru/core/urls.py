from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import HomeListView, ItemDetailView, checkout, add_to_cart

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('detail/<slug>', ItemDetailView.as_view(), name='product'),
    path('checkout/', checkout, name='checkout'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
]