from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Item


class HomeListView(ListView):
    model = Item
    template_name = 'home.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product_detail.html'
