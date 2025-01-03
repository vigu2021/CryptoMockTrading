# Generated by Django 5.1.3 on 2025-01-03 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orders",
            name="symbol",
        ),
        migrations.RemoveField(
            model_name="usercrypto",
            name="symbol",
        ),
        migrations.RemoveField(
            model_name="orders",
            name="user",
        ),
        migrations.RemoveField(
            model_name="useravlbbalance",
            name="user",
        ),
        migrations.RemoveField(
            model_name="userbalance",
            name="user",
        ),
        migrations.RemoveField(
            model_name="usercrypto",
            name="user",
        ),
        migrations.DeleteModel(
            name="CryptoSymbols",
        ),
        migrations.DeleteModel(
            name="Orders",
        ),
        migrations.DeleteModel(
            name="UserAvlbBalance",
        ),
        migrations.DeleteModel(
            name="UserBalance",
        ),
        migrations.DeleteModel(
            name="UserCrypto",
        ),
    ]
