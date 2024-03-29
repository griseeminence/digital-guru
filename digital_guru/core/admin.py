from django.contrib import admin
from .models import Item, Order, OrderItem, Payment, Coupon, Refund, Address


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_granted=True, refund_requested=False)


make_refund_accepted.short_description = 'Make refunds accepted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted',
                    'billing_address', 'shipping_address', 'payment', 'coupon', ]

    list_display_links = [
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon',
    ]

    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']

    search_fields = [
        'user__username',
        'ref_code',
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'zip',
        'country',
        'address_type',
        'default',
    ]
    list_filter = ['address_type', 'default', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip', 'country']


admin.site.register(Refund)
admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Address, AddressAdmin)
