import unittest
from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import QuerySet

from core.models import Item
from core.views import HomeListView


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



if __name__ == '__main__':
    unittest.main()
