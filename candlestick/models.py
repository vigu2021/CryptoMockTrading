from django.db import models
from cryptos.models import CryptoSymbols

class Candlestick(models.Model):
    symbol = models.ForeignKey(CryptoSymbols, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()  # Renamed from 'updated_at' to 'timestamp'
    low = models.FloatField()
    high = models.FloatField()
    open = models.FloatField()
    close = models.FloatField()

    class Meta:
        db_table = 'candlestick'
        indexes = [
            models.Index(fields=['symbol', 'timestamp'], name='symbol_timestamp_idx'),  # Updated index name
        ]
        ordering = ['-timestamp']  # Default ordering by timestamp in descending order

    def __str__(self):
        return f"{self.symbol.symbol} - {self.timestamp}"
