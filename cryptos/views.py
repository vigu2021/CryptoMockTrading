from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from cryptos.models import CryptoSymbols
from cryptos.scripts.get_current_prices import get_current_prices

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
