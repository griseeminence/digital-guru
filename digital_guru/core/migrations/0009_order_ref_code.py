# Generated by Django 4.2.7 on 2023-11-21 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_order_being_delivered_order_received_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default=123, max_length=100),
            preserve_default=False,
        ),
    ]
