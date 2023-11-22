from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('P', 'PayPal'),
    ('S', 'Stripe'),
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '123 Main St'
    }))
    apartment_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Apt. 123'
    }))
    country = CountryField(blank_label='(select a country)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100',
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control w-100',
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control w-100',
        'placeholder': 'Coupon Code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2',
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.Textarea()
    email = forms.EmailField()