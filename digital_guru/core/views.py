from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Item, OrderItem, Order


class HomeListView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'core/home.html'


class OrderSummeryView(LoginRequiredMixin, View): # Не работает редирект для анонима. Исправить страницы авторизации?
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'core/order_summery.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'You have no orders')
            return redirect('core:home')


class ItemDetailView(DetailView):
    model = Item
    template_name = 'core/detail.html'


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'products.html', context)


def checkout(request):
    return render(request, 'core/checkout.html')


@login_required # Не работает редирект для анонима. Исправить страницы авторизации?
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first()  # заменить на order_qs[0], если не будет работать
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f'{item.title} quantity increased to {order_item.quantity}')
            return redirect('core:detail', slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, f'{item.title} was added to your cart')
            return redirect('core:detail', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, f'{item.title} was added to your cart')
        return redirect('core:detail', slug=slug)


@login_required # Не работает редирект для анонима. Исправить страницы авторизации?
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first()  # заменить на order_qs[0], если не будет работать
        if order.items.filter(item__slug=item.slug).exists():
            order_item = order.items.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, f'{item.title} was removed from your cart')
            return redirect('core:detail', slug=slug)
        else:
            messages.info(request, f'{item.title} was not in your cart')
            return redirect('core:detail', slug=slug)
    else:
        messages.info(request, f'You do not have an active order')
        return redirect('core:detail', slug=slug)
