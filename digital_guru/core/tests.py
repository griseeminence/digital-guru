import unittest
from unittest import TestCase

from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import QuerySet

from core.forms import CheckoutForm
from core.models import Item, Order
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
