# Generated by Django 5.1.3 on 2025-01-05 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cryptos", "0003_orders_is_buy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orders",
            name="is_buy",
            field=models.BooleanField(),
        ),
    ]
