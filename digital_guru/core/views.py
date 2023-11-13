from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages

from .models import Item, OrderItem, Order


class HomeListView(ListView):
    model = Item
    template_name = 'core/home.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product_detail.html'


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'products.html', context)


def checkout(request):
    return render(request, 'checkout.html')


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first() #заменить на order_qs[0], если не будет работать
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f'{item.title} quantity increased to {order_item.quantity}')
            return redirect('core:products', slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, f'{item.title} was added to your cart')
            return redirect('core:products', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, f'{item.title} was added to your cart')
        return redirect('core:products', slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first() #заменить на order_qs[0], если не будет работать
        if order.items.filter(item__slug=item.slug).exists():
            order_item = order.items.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, f'{item.title} was removed from your cart')
            return redirect('core:products', slug=slug)
        else:
            messages.info(request, f'{item.title} was not in your cart')
            return redirect('core:products', slug=slug)
    else:
        messages.info(request, f'You do not have an active order')
        return redirect('core:products', slug=slug)