from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import HomeListView, ItemDetailView

urlpatterns = [
    path('', HomeListView.as_view(), name='home'),
    path('detail/<slug>', ItemDetailView.as_view(), name='product'),
]