from django.apps import AppConfig
from .scheduler import start_scheduler 


class CryptosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cryptos"


    def ready(self):
        start_scheduler()  