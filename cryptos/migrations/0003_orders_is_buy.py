# Generated by Django 5.1.3 on 2025-01-04 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cryptos", "0002_orders_order_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="orders",
            name="is_buy",
            field=models.BooleanField(default=1),
        ),
    ]
