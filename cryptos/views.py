from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render,redirect
from cryptos.models import CryptoSymbols
from .forms import MarketOrderForm,LimitOrderForm,StopLimitOrderForm
from cryptos.scripts.get_current_prices import get_current_prices
from .handle_orders import handle_market_order,handle_limit_order
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
    Handle the creation of market, limit, and stop limit buy/sell orders.
    """
    if request.method == 'POST':
        # Determine the form to use based on the order_type in the POST data
        order_type = request.POST.get('order_type', 'MARKET')
        if order_type == 'LIMIT':
            form = LimitOrderForm(request.POST)
        elif order_type == 'STOP_LIMIT':
            form = StopLimitOrderForm(request.POST)
        else:  # Default to Market Order
            form = MarketOrderForm(request.POST)

        if form.is_valid():
            # Extract common cleaned data
            order_type = form.cleaned_data['order_type']
            symbol_str = form.cleaned_data['symbol'].symbol
            quantity = form.cleaned_data['quantity']
            is_buy = form.cleaned_data['is_buy']
            take_profit = form.cleaned_data['take_profit']
            stop_loss = form.cleaned_data['stop_loss']
            is_buy = True if is_buy == 'True' else False

            # Fetch current prices
            current_prices = get_current_prices()
            current_price = current_prices.get(symbol_str)

            if current_price is None:
                messages.error(request, f"Current price for symbol '{symbol_str}' not found.")
                return render(request, 'spot.html', {'form': form})

            user = request.user

            # Handle order types
            try:
                if order_type == 'MARKET':
                    handle_market_order(
                        user=user,
                        symbol=symbol_str,
                        quantity=quantity,
                        is_buy=is_buy,
                        current_price=Decimal(current_price),
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                elif order_type == 'LIMIT':
                    limit_price = form.cleaned_data['limit_price']
                    handle_limit_order(
                        user=user,
                        symbol=symbol_str,
                        quantity=quantity,
                        is_buy=is_buy,
                        current_price=Decimal(current_price),
                        limit_price=Decimal(limit_price),
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                elif order_type == 'STOP_LIMIT':
                    limit_price = form.cleaned_data['limit_price']
                    stop_price = form.cleaned_data['stop_price']
                    handle_limit_order(
                        user=user,
                        symbol=symbol_str,
                        quantity=quantity,
                        is_buy=is_buy,
                        current_price=Decimal(current_price),
                        limit_price=Decimal(limit_price),
                        stop_price=Decimal(stop_price),
                        take_profit=take_profit,
                        stop_loss=stop_loss
                    )
                else:
                    messages.error(request, "Unsupported order type.")
                    return render(request, 'spot.html', {'form': form})

                messages.success(request, "Order placed successfully!")
                return redirect('home_page')  # Adjust as needed
            except ValidationError as ve:
                form.add_error(None, ve.message)
            except Exception as e:
                messages.error(request, "An unexpected error occurred while processing the order.")
        else:
            messages.error(request, "Invalid form submission. Please check your inputs.")

    else:
        # Default form for GET request
        form = MarketOrderForm()

    return render(request, 'spot.html', {'form': form})