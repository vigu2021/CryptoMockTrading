from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render,redirect
from cryptos.models import CryptoSymbols
from cryptos.scripts.get_current_prices import get_current_prices
from .forms import MarketOrderForm
from .scripts import get_current_prices
from decimal import Decimal
@login_required
def home_page(request):
    """
    Render the home page with the current crypto prices.
    """
    # Fetch all symbols and their current prices
    symbol_prices = get_current_prices()

    return render(request, 'home.html', {'symbol_prices': symbol_prices})

@login_required
def get_updated_prices(request):
    
    """
    API endpoint to fetch updated crypto prices.
    """
    # Fetch the updated prices for all symbols
    symbol_prices = get_current_prices()

    return JsonResponse(symbol_prices)

@login_required
def create_order(request):
    if request.method == 'POST':
        form = MarketOrderForm(request.POST)
        order_type = form.cleaned_data['order_type']
        symbol = form.cleaned_data['symbol']
        quantity = form.cleaned_data['quantity']
        is_buy = form.cleaned_data['is_buy']
        current_price = Decimal(str(get_current_prices().get(symbol)))

        #These fields are optional
        take_profit = form.cleaned_data['take_profit'] if form.cleaned_data['take_profit'] else None
        stop_loss = form.cleaned_data['stop_loss'] if form.cleaned_data['stop_loss'] else None

        user = request.user
        if order_type == 'MARKET':
            if form.is_valid():
                #handle_market_order(user,symbol,quantity,is_buy,current_price,take_profit,stop_loss)
                form = MarketOrderForm()  
            else:
                pass
        else:
            # GET request => new blank form
            form = MarketOrderForm()

    return render(request, 'spot.html', {'form': form})

