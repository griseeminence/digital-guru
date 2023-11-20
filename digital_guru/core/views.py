from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .forms import CheckoutForm
from .models import Item, OrderItem, Order, BillingAddress, Payment

import stripe
import stripe, logging

stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'


# stripe.api_key = settings.STRIPE_SECRET_KEY


class HomeListView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'core/home.html'


class OrderSummeryView(LoginRequiredMixin, View):  # Не работает редирект для анонима. Исправить страницы авторизации?
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
    return render(request, 'core/detail.html', context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'core/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality to this fields:
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'S':

                    # TODO: add redirect to selected payment method
                    print(form.cleaned_data)
                    print(f'form is valid')
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, f'Invalid payment option: {payment_option}')
                    return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, 'You have no orders')
            return redirect('core:order-summery')


class PaymentView(View):  # Проблема с получением данных по апи-токену.
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'core/payment.html', context)

    def post(self, *args, **kwargs):

        token = self.request.POST.get('stripeToken')
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = order.get_total() * 100

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency='usd',
                source=token
            )

            #       #create a payment
            payment = Payment()
            payment.stripe_charge_id = charge
            payment.user = self.request.user
            payment.amount = amount
            payment.save()

            # assign the payment
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, f'Your payment was successful')
            return redirect('/')


        except stripe.error.CardError as e:
            logging.error("A payment error occurred: {}".format(e.user_message))
            return redirect('/')
        except stripe.error.InvalidRequestError:
            logging.error("An invalid request occurred.")
            return redirect('/')
        except Exception:
            logging.error("Another problem occurred, maybe unrelated to Stripe.")
            return redirect('/')
        else:
            logging.info("No error.")


@login_required  # Не работает редирект для анонима. Исправить страницы авторизации?
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
            return redirect('core:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request, f'{item.title} was added to your cart')
            return redirect('core:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, f'{item.title} was added to your cart')
        return redirect('core:order-summary')


@login_required  # Не работает редирект для анонима. Исправить страницы авторизации?
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
            return redirect('order-summary')
        else:
            messages.info(request, f'{item.title} was not in your cart')
            return redirect('core:detail', slug=slug)
    else:
        messages.info(request, f'You do not have an active order')
        return redirect('core:detail', slug=slug)


@login_required  # Не работает редирект для анонима. Исправить страницы авторизации?
def remove_single_item_from_cart(request, slug):
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
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, f'Product quantity updated')
            return redirect('core:order-summary')
        else:
            messages.info(request, f'{item.title} was not in your cart')
            return redirect('core:detail', slug=slug)
    else:
        messages.info(request, f'You do not have an active order')
        return redirect('core:detail', slug=slug)
