from django.apps import AppConfig


class CryptosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cryptos"


    def ready(self):
        from .scheduler import start_balance_scheduler,start_order_status_scheduler
        start_balance_scheduler()
        start_order_status_scheduler()