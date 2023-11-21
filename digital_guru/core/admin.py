from django.contrib import admin
from .models import Item, Order, OrderItem, Payment, Coupon


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'ordered')


admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
