from django.conf import settings
from django.db import models
from django.shortcuts import reverse

CATEGORY_CHOICES = (
    ('RAM', 'RAM'),
    ('CPU', 'CPU'),
    ('Video', 'Video Graphics Cards'),
    ('Motherboards', 'Motherboards'),
    ('HDD&SSD', 'HDD & SSD'),
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES,
                                default=None)  # Можно ли здесь None в дефолте?
    label = models.CharField(max_length=2, choices=LABEL_CHOICES, default='P')
    slug = models.SlugField(max_length=100, default=None)  # Можно ли здесь None в дефолте?
    description = models.TextField(blank=True, null=True, default='This is a default description')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:product', kwargs={
            'slug': self.slug,
        })  # product - name для ItemDetailView из core/urls.py,
        # reverse формирует url как 'product/' а дальше ожидает (исходя из url)
        # что к product будет добавлен slug, который мы и передаем в kwargs.
        # соответственно, прямо в шаблоне могу вызывать экземпляры модели через этот метод.


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
