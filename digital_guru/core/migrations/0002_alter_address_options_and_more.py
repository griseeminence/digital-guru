# Generated by Django 4.2.7 on 2023-11-30 07:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': 'Addresses'},
        ),
        migrations.RenameField(
            model_name='address',
            old_name='adress_type',
            new_name='address_type',
        ),
    ]