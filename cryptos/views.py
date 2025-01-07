from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render,redirect
from cryptos.models import CryptoSymbols,Orders
from .forms import MarketOrderForm,LimitOrderForm,StopLimitOrderForm
from cryptos.scripts.get_current_prices import get_current_prices
from .handle_orders import handle_market_order,handle_limit_order
from decimal import Decimal
from django.contrib import messages
@login_required
def home_page(request):
    # Fetch all symbols and their current prices
    symbol_prices = get_current_prices()
    return render(request, 'home.html', {'symbol_prices': symbol_prices})

@login_required
def get_updated_prices(request):
    symbol_prices = get_current_prices()
    return JsonResponse(symbol_prices)


#Central template for spot orders
def spot(request):
    return render(request, 'spot.html')
def market_order_form(request):
    """
    Handle the Market Order form: render and process submissions.
    """
    if request.method == 'POST':
        form = MarketOrderForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].symbol
            quantity = form.cleaned_data['quantity']
            is_buy = form.cleaned_data['is_buy']
            take_profit = form.cleaned_data.get('take_profit')
            stop_loss = form.cleaned_data.get('stop_loss')
            is_buy = True if is_buy == 'True' else False
            current_prices = get_current_prices()
            current_price = current_prices.get(symbol)

            if current_price is None:
                messages.error(request, f"Current price for '{symbol}' not available.")
                return render(request, 'market_order.html', {'form': form, 'order_type': 'market'})

            try:
                handle_market_order(
                    user=request.user,
                    symbol=symbol,
                    quantity=quantity,
                    is_buy=is_buy,
                    current_price=Decimal(current_price),
                    take_profit=Decimal(take_profit) if take_profit else None,
                    stop_loss=Decimal(stop_loss) if stop_loss else None,
                )
                messages.success(request, "Market order placed successfully!")
                return redirect('spot')  # Redirect to the main spot page or a success page
            except Exception as e:
                messages.error(request, f"An error occurred while placing the order: {e}")
    else:
        # For GET requests, ensure the form is always initialized
        form = MarketOrderForm()

    # Ensure the template always receives a `form` context
    return render(request, 'market_order.html', {'form': form, 'order_type': 'market'})

#Limit order form
def limit_order_form(request):
    """
    Render and handle the Limit Order form.
    """
    if request.method == 'POST':
        form = LimitOrderForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = LimitOrderForm()
    return render(request, 'limit_order.html', {'form': form, 'order_type': 'limit'})

#Stop limit form
def stop_limit_order_form(request):
    """
    Render and handle the Stop Limit Order form.
    """
    if request.method == 'POST':
        form = StopLimitOrderForm(request.POST)
        if form.is_valid():
            # Add logic to handle stop-limit order submission
            pass
    else:
        form = StopLimitOrderForm()
    return render(request, 'stop_limit_order.html', {'form': form, 'order_type': 'stop-limit'})

