from django import forms
from .models import Orders, CryptoSymbols

class MarketOrderForm(forms.ModelForm):
    BUY_SELL_CHOICES = [
        (True, 'Buy'),
        (False, 'Sell'),
    ]

    is_buy = forms.ChoiceField(
        choices=BUY_SELL_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Action",
        required=True,
    )

    class Meta:
        model = Orders
        fields = ['symbol', 'quantity', 'take_profit', 'stop_loss', 'is_buy']
        widgets = {
            'symbol': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'take_profit': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'stop_loss': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['symbol'].queryset = CryptoSymbols.objects.all()
