# forms.py
from django import forms
from django.utils.safestring import mark_safe
from .models import Orders, CryptoSymbols

class MarketOrderForm(forms.ModelForm):
    BUY_SELL_CHOICES = [
        (True, mark_safe('<span style="color:#28a745;font-weight:bold;">Buy</span>')),
        (False, mark_safe('<span style="color:#dc3545;font-weight:bold;">Sell</span>')),
    ]

    ORDER_TYPE_CHOICES = [
        ('MARKET', 'Market Order'),
        ('LIMIT', 'Limit Order'),
        ('STOP_LIMIT', 'Stop Limit Order'),
    ]

    is_buy = forms.ChoiceField(
        choices=BUY_SELL_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Action",
        required=True,
    )
    order_type = forms.ChoiceField(
        choices=ORDER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Order Type",
        required=True,
    )

    class Meta:
        model = Orders
        fields = ['order_type', 'symbol', 'quantity', 'take_profit', 'stop_loss', 'is_buy']
        widgets = {
            'symbol': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'take_profit': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'stop_loss': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        stop_loss = cleaned_data.get('stop_loss')
        take_profit = cleaned_data.get('take_profit')
        is_buy = cleaned_data.get('is_buy')

        #Qunantity must be bigger than 0 
        if quantity and quantity<0:
            raise forms.ValidationError("Quantity must be greater than 0")

        # If buy take profit must be bigger than stop loss
        if is_buy == 'True':
            if stop_loss is not None and take_profit is not None:
                if stop_loss > take_profit:
                    raise forms.ValidationError(
                        "Take profit must be bigger than stop loss for buy orders"
                    )
        else:
            # If the user selected "Sell"...
            if stop_loss is not None or take_profit is not None:
                    raise forms.ValidationError(
                       "Stop Loss and Take profit not allowed for sell orders"
                    )
        return cleaned_data
'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['symbol'].queryset = CryptoSymbols.objects.all()
'''

#Limit Order Form
class LimitOrderForm(MarketOrderForm):
    limit_price = forms.DecimalField(
        max_digits=20,
        decimal_places=10,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        label="Limit Price",
    )
    class Meta(MarketOrderForm.Meta):
        fields = MarketOrderForm.Meta.fields + ['limit_price']
    
    def clean(self):
        cleaned_data = super().clean()
        limit_price = cleaned_data.get('limit_price')

        if limit_price and limit_price <= 0:
            raise forms.ValidationError("Limit Price must be greater than 0")

        return cleaned_data

#Stop Limit Form
class StopLimitOrderForm(LimitOrderForm):
    stop_price = forms.DecimalField(
        max_digits=20,
        decimal_places=10,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        label="Stop Price",
    )
    class Meta(LimitOrderForm.Meta):
        fields = LimitOrderForm.Meta.fields + ['stop_price']
    
    def clean(self):
        cleaned_data = super().clean()
        stop_price = cleaned_data.get('stop_price')
        if stop_price and stop_price <= 0:
            raise forms.ValidationError("Stop Price must be greater than 0")
        
        return cleaned_data
