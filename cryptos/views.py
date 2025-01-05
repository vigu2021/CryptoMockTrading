from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render,redirect
from cryptos.models import CryptoSymbols
from .forms import MarketOrderForm
from cryptos.scripts.get_current_prices import get_current_prices
from .handle_orders import handle_market_order
from decimal import Decimal
from django.contrib import messages
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
    """
    Handle the creation of market buy/sell orders.
    """
    if request.method == 'POST':
        form = MarketOrderForm(request.POST)
        if form.is_valid():
            # Extract cleaned data from the form
            order_type = form.cleaned_data['order_type']
            symbol_str = form.cleaned_data['symbol'].symbol
            quantity = form.cleaned_data['quantity']
            is_buy = form.cleaned_data['is_buy']
            take_profit = form.cleaned_data['take_profit'] if form.cleaned_data['take_profit'] else None
            stop_loss = form.cleaned_data['stop_loss'] if form.cleaned_data['stop_loss'] else None

            # Convert is_buy from string to boolean
            is_buy = True if is_buy == 'True' else False

            # Fetch current prices
            current_prices = get_current_prices()

            # Retrieve the current price for the selected symbol
            current_price = current_prices.get(symbol_str)
            
            if current_price is None:
                messages.error(request, f"Current price for symbol '{symbol_str}' not found.")
                return render(request, 'spot.html', {'form': form})

            user = request.user

            if order_type == 'MARKET':
                try:
                    # Call handle_market_order with correct parameters
                    handle_market_order(
                        user=user,
                        symbol=symbol_str,
                        quantity=quantity,
                        is_buy=is_buy,
                        current_price=Decimal(current_price),  # Ensure it's a Decimal
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                    messages.success(request, "Order placed successfully!")
                    return redirect('home_page')  # Replace with your desired redirect
                except ValidationError as ve:
                    form.add_error(None, ve.message)
                except Exception as e:
                    # Handle unexpected errors
                    messages.error(request, "An unexpected error occurred while processing the order.")
            else:
                messages.error(request, "Unsupported order type.")
        
    else:
        # For GET requests, instantiate a blank form
        form = MarketOrderForm()

    return render(request, 'spot.html', {'form': form})
