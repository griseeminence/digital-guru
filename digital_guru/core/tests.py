

from django.contrib.messages import get_messages

from django.db.models import QuerySet

from core.forms import CheckoutForm
from core.models import Item, Order, OrderItem
from core.views import HomeListView, OrderSummeryView


import unittest
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse, render, redirect
from django.contrib.messages.middleware import MessageMiddleware
from .models import Order, Address
from .views import CheckoutView

class CheckoutViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем тестового пользователя для запросов
        cls.user = User.objects.create_user(username='testuser', password='testpassword')

    def setUp(self):
        # Создаем экземпляр CheckoutView
        self.view = CheckoutView()

        # Создаем фабрику запросов Django
        self.factory = RequestFactory()

        # Создаем middleware для обработки сообщений
        self.middleware = MessageMiddleware()

    def test_get_success(self):
        # Создаем заказ для пользователя
        order = Order.objects.create(user=self.user, ordered=False)

        # Создаем запрос GET
        request = self.factory.get(reverse('checkout'))

        # Аутентифицируем пользователя в запросе
        request.user = self.user

        # Применяем middleware
        self.middleware.process_request(request)

        # Применяем middleware для обработки сообщений
        response = self.view.get(request)

        # Проверяем, что пользователь получает корректный ответ
        self.assertEqual(response.status_code, 200)

        # Проверяем, что используется правильный шаблон
        self.assertTemplateUsed(response, 'core/checkout.html')

        # Проверяем наличие формы в контексте
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CheckoutForm)  # Заменить

        # Проверяем наличие других элементов в контексте
        self.assertIn('couponform', response.context)
        self.assertIn('order', response.context)
        self.assertIn('DISPLAY_COUPON_FORM', response.context)

        def test_post_success(self):
            # Создаем заказ для пользователя
            order = Order.objects.create(user=self.user, ordered=False)

            # Создаем запрос POST
            request_data = {
                # Здесь передайте данные для успешной отправки формы
                'use_default_shipping': True,
                'use_default_billing': True,
                'same_billing_address': True,
                'payment_option': 'S',
                # ...
            }
            request = self.factory.post(reverse('checkout'), data=request_data)

            # Аутентифицируем пользователя в запросе
            request.user = self.user

            # Применяем middleware
            self.middleware.process_request(request)

            # Применяем middleware для обработки сообщений
            response = self.view.post(request)

            # Проверяем, что пользователь перенаправлен на правильный URL
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response,
                                 reverse('core:payment', kwargs={'payment_option': 'stripe'}))  # Замените на свой URL

            # Здесь можете добавить дополнительные проверки в соответствии с вашей логикой

class HomeListViewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем тестового пользователя для запросов
        cls.user = User.objects.create_user(username='testuser', password='testpassword')

    def setUp(self):
        # Создаем несколько тестовых объектов Item для использования в тестах
        for i in range(15):
            Item.objects.create(name=f'Test Item {i}')

        # Создаем экземпляр HomeListView
        self.view = HomeListView()

        # Создаем фабрику запросов Django
        self.factory = RequestFactory()

    def test_model(self):
        # Убеждаемся, что модель класса HomeListView - Item
        self.assertEqual(self.view.model, Item)

    def test_paginate_by(self):
        # Убеждаемся, что количество объектов на странице равно 10
        self.assertEqual(self.view.paginate_by, 10)

    def test_template_name(self):
        # Убеждаемся, что имя шаблона равно 'core/home.html'
        self.assertEqual(self.view.template_name, 'core/home.html')

    def test_queryset(self):
        # Создаем запрос GET
        request = self.factory.get(reverse('home'))

        # Аутентифицируем пользователя в запросе
        request.user = self.user

        # Получаем контекст представления
        context = self.view.get_context_data(request=request)

        # Получаем QuerySet из контекста
        queryset = context['object_list']

        # Убеждаемся, что это QuerySet
        self.assertIsInstance(queryset, QuerySet)

        # Убеждаемся, что количество элементов в QuerySet равно 10
        self.assertEqual(queryset.count(), 10)

    def test_pagination(self):
        # Создаем запрос GET для второй страницы
        request = self.factory.get(reverse('home'), {'page': 2})

        # Аутентифицируем пользователя в запросе
        request.user = self.user

        # Получаем контекст представления
        context = self.view.get_context_data(request=request)

        # Получаем QuerySet из контекста
        queryset = context['object_list']

        # Убеждаемся, что это QuerySet
        self.assertIsInstance(queryset, QuerySet)

        # Убеждаемся, что количество элементов в QuerySet равно 5 (вторая страница)
        self.assertEqual(queryset.count(), 5)


class OrderSummaryViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем тестового пользователя для запросов
        cls.user = User.objects.create_user(username='testuser', password='testpassword')

    def setUp(self):
        # Создаем экземпляр OrderSummaryView
        self.view = OrderSummeryView()

        # Создаем фабрику запросов Django
        self.factory = RequestFactory()

        # Создаем middleware для обработки сообщений
        self.middleware = MessageMiddleware()

    def test_redirect_if_no_order(self):
        # Создаем запрос GET
        request = self.factory.get(reverse('order-summary'))

        # Аутентифицируем пользователя в запросе
        request.user = self.user

        # Применяем middleware
        self.middleware.process_request(request)

        # Применяем middleware для обработки сообщений
        response = self.view.get(request)

        # Проверяем, что пользователь перенаправлен на 'core:home'
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:home'))

        # Проверяем наличие сообщения об ошибке в запросе
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You have no orders')

    def test_render_if_order_exists(self):
        # Создаем заказ для пользователя
        order = Order.objects.create(user=self.user, ordered=False)

        # Создаем запрос GET
        request = self.factory.get(reverse('order-summary'))

        # Аутентифицируем пользователя в запросе
        request.user = self.user

        # Применяем middleware
        self.middleware.process_request(request)

        # Применяем middleware для обработки сообщений
        response = self.view.get(request)

        # Проверяем, что пользователь получает корректный ответ
        self.assertEqual(response.status_code, 200)

        # Проверяем, что используется правильный шаблон
        self.assertTemplateUsed(response, 'core/order_summery.html')

        # Проверяем, что объект заказа передается в контекст
        self.assertEqual(response.context['object'], order)




if __name__ == '__main__':
    unittest.main()


class AddToCartViewTest(TestCase):
    def setUp(self):
        self.client = User()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.item = Item.objects.create(title='Test Item', slug='test-item', price=10.0)

    def test_add_to_cart_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('add_to_cart', args=[self.item.slug]))

        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('core:order-summary'))

        order_item = OrderItem.objects.get(item=self.item, user=self.user, ordered=False)
        self.assertEqual(order_item.quantity, 1)

        # Check if the message is displayed
        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn(f'Test Item was added to your cart', messages)

    def test_add_to_cart_unauthenticated_user(self):
        response = self.client.post(reverse('add_to_cart', args=[self.item.slug]))

        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('login') + f'?next={reverse("add_to_cart", args=[self.item.slug])}')

    def test_add_to_cart_existing_order_item(self):
        self.client.login(username='testuser', password='testpassword')
        order = Order.objects.create(user=self.user, ordered_date=timezone.now())
        order_item = OrderItem.objects.create(item=self.item, user=self.user, ordered=False, quantity=2)
        order.items.add(order_item)

        response = self.client.post(reverse('add_to_cart', args=[self.item.slug]))

        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('core:order-summary'))

        order_item.refresh_from_db()
        self.assertEqual(order_item.quantity, 3)  # Quantity should be increased by 1

    def test_add_to_cart_new_order(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('add_to_cart', args=[self.item.slug]))

        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('core:order-summary'))

        order_item = OrderItem.objects.get(item=self.item, user=self.user, ordered=False)
        self.assertEqual(order_item.quantity, 1)

        order = Order.objects.get(user=self.user, ordered=False)
        self.assertIn(order_item, order.items.all())


class RequestRefundViewTest(TestCase):
    def setUp(self):
        # Создаем пользователя и заказ для тестирования
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.order = Order.objects.create(user=self.user, ref_code='123456', total=100.00)

    def test_get_request_refund_view(self):
        # Проверяем, что GET запрос возвращает код 200
        self.client.force_login(self.user)
        response = self.client.get(reverse('core:request-refund'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/request_refund.html')
        self.assertIsInstance(response.context['form'], RefundForm)

    def test_post_request_refund_view_success(self):
        # Проверяем успешный POST запрос на возврат
        self.client.force_login(self.user)
        data = {
            'ref_code': '123456',
            'message': 'Test refund message',
            'email': 'test@example.com',
        }
        response = self.client.post(reverse('core:request-refund'), data)
        self.assertEqual(response.status_code, 302)  # Перенаправление после успешного запроса
        self.assertRedirects(response, reverse('core:request-refund'))

        # Проверяем, что заказ помечен как запрошенный на возврат
        self.order.refresh_from_db()
        self.assertTrue(self.order.refund_requested)

        # Проверяем создание объекта Refund
        self.assertEqual(Refund.objects.count(), 1)
        refund = Refund.objects.first()
        self.assertEqual(refund.order, self.order)
        self.assertEqual(refund.reason, 'Test refund message')
        self.assertEqual(refund.email, 'test@example.com')

        # Проверяем наличие сообщения об успешном запросе возврата
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully requested refund')

    def test_post_request_refund_view_no_active_order(self):
        # Проверяем POST запрос с несуществующим ref_code
        self.client.force_login(self.user)
        data = {
            'ref_code': 'invalid_ref_code',
            'message': 'Test refund message',
            'email': 'test@example.com',
        }
        response = self.client.post(reverse('core:request-refund'), data)
        self.assertEqual(response.status_code, 302)  # Перенаправление после запроса

        # Проверяем, что пользователя информируют о отсутствии активного заказа
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You do not have an active order')