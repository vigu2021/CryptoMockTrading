from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render,redirect
from cryptos.models import CryptoSymbols
from cryptos.scripts.get_current_prices import get_current_prices
from .forms import MarketOrderForm

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
        if form.is_valid():
            # Process or save the form
            form.save()

            # 1) If you do NOT want to redirect:
            #    - just stay on this URL and optionally
            #    - create a fresh form or keep the data.
            
            # If you WANT a blank form after a successful save, do:
            form = MarketOrderForm()  # re-instantiate so it’s empty
            # If you want to keep the data in the fields, skip this line.

        else:
            # Form is invalid => form already has errors & user data
            # Don’t overwrite `form`; just let it fall through to re-render
            pass
    else:
        # GET request => new blank form
        form = MarketOrderForm()

    return render(request, 'spot.html', {'form': form})

