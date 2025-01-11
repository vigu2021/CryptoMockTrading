from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime

class CryptoSymbols(models.Model):
    symbol = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'crypto_symbols'
        indexes = [
            models.Index(fields=['symbol']),  
        ]
    
    def __str__(self):
        return self.symbol


class UserCrypto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.ForeignKey(CryptoSymbols, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated timestamp
    avg_price = models.DecimalField(max_digits=20, decimal_places=10)  # Average price of the crypto
    quantity = models.DecimalField(max_digits=20, decimal_places=10)  # Quantity of the crypto

    class Meta:
        db_table = 'user_crypto'
        indexes = [
            models.Index(fields=['user', 'symbol'], name='user_symbol_idx'),  # Composite index
        ]

    def __str__(self):
        return f"{self.user.username} - {self.symbol.symbol}"


class UserAvlbBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the User table
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated timestamp
    avlb_balance = models.DecimalField(max_digits=20, decimal_places=10)  # Available balance
    currency = models.CharField(max_length=10, default="USDT")

    class Meta:
        db_table = 'user_avlb_balance'
        indexes = [
            models.Index(fields=['user']),  
        ]

    def __str__(self):
        return f"{self.user.username} - {self.avlb_balance} {self.currency}"

    def clean(self):
        if self.avlb_balance < 0:
            raise ValidationError("Balance cannot be negative.")


class UserBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(default=datetime.now)
    balance = models.DecimalField(max_digits=20, decimal_places=10)  # Total balance, cannot be negative

    class Meta:
        db_table = 'user_balance'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'updated_at']),  
        ]

    def __str__(self):
        return f"{self.user.username} - {self.balance} USDT"

    def clean(self):
        if self.balance < 0:
            raise ValidationError("Balance cannot be negative.")




class UserLimitBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the User table
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated timestamp
    limit_balance = models.DecimalField(max_digits=20, decimal_places=10)  # Available balance
    currency = models.CharField(max_length=10, default="USDT")

    class Meta:
        db_table = 'user_limit_balance'
        indexes = [
            models.Index(fields=['user']),  
        ]

    def __str__(self):
        return f"{self.user.username} - {self.limit_balance} {self.currency}"

    def clean(self):
        if self.limit_balance < 0:
            raise ValidationError("Balance cannot be negative.")



class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the User table
    symbol = models.ForeignKey('CryptoSymbols', on_delete=models.CASCADE)  # Links to CryptoSymbols
    order_date = models.DateTimeField(auto_now_add=True)  # Automatically set when the order is created
    status = models.CharField(max_length=20, default="PENDING")  # Status of the order (e.g., PENDING, EXECUTED, COMPLETED,CANCELLED)
    order_type = models.CharField(max_length=20,default = 'MARKET')  # Order type (MARKET,LIMIT,STOPLIMIT)
    price = models.DecimalField(max_digits=20, decimal_places=10)  # Price at which the order is placed
    quantity = models.DecimalField(max_digits=20, decimal_places=10)  # Quantity of the asset being traded
    limit_price = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)  # Optional limit price for limit orders
    stop_price = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)  # Optional stop price for stop-loss orders
    take_profit = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)  # Optional take-profit price
    stop_loss = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)  # Optional stop-loss value
    is_buy = models.BooleanField() #Whether buy or sell

    class Meta:
        db_table = 'orders'
        indexes = [
            models.Index(fields=['user', 'status']),  # Composite index for user and symbol
            models.Index(fields=['order_date']),  # Index for order date
        ]

    def __str__(self):
        return f"{self.user.username} - {self.symbol.symbol} - {self.status}"
    
