from django.apps import AppConfig


class CryptosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cryptos"


    def ready(self):
        from .scheduler import start_scheduler 
        start_scheduler()  