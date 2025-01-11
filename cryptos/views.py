from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,redirect
from cryptos.models import UserCrypto,UserAvlbBalance,UserBalance,UserLimitBalance
from .forms import MarketOrderForm,LimitOrderForm,StopLimitOrderForm
from cryptos.scripts.get_current_prices import get_current_prices
from .handle_orders import handle_market_order,handle_limit_order
from decimal import Decimal
from django.contrib import messages
from datetime import datetime, timedelta

@login_required
def home_page(request):
    # Fetch all symbols and their current prices
    symbol_prices = get_current_prices()
    return render(request, 'home.html', {'symbol_prices': symbol_prices})

@login_required
def get_updated_prices(request):
    symbol_prices = get_current_prices()
    return JsonResponse(symbol_prices)

@login_required
def portfolio(request):
    symbol_prices = get_current_prices()
    limit_balance = UserLimitBalance.objects.get(user=request.user).limit_balance
    avaliable_balance = UserAvlbBalance.objects.get(user=request.user).avlb_balance
    balance = limit_balance + avaliable_balance

    # Calculate value of crypto holdings and add to balance
    crypto_holdings = UserCrypto.objects.filter(user=request.user)
    for crypto in crypto_holdings:
        current_price = Decimal(symbol_prices.get(crypto.symbol.symbol, 0))
        balance += crypto.quantity * current_price

    # Fetch balance this hour
    balance_this_hour = UserBalance.objects.filter(user=request.user).first()

    if not balance_this_hour:
        return {"error": "No balance record for this hour."}

    # Fetch balance 24 hours ago
    balance_last_day = UserBalance.objects.filter(
        user=request.user,
        updated_at=balance_this_hour.updated_at - timedelta(days=1)
    ).first()
    balance_last_day_value = balance_last_day.balance if balance_last_day else 0

    # Fetch balance from the start of this week
    time_last_hour = balance_this_hour.updated_at
    start_of_week = time_last_hour - timedelta(days=time_last_hour.weekday())
    balance_last_week = UserBalance.objects.filter(
        user=request.user,
        updated_at=start_of_week
    ).first()
    balance_last_week_value = balance_last_week.balance if balance_last_week else 0

    # Fetch balance from the start of this month
    start_of_month = time_last_hour.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    balance_last_month = UserBalance.objects.filter(
        user=request.user,
        updated_at=start_of_month
    ).first()
    balance_last_month_value = balance_last_month.balance if balance_last_month else 0

    # Fetch balance from the start of this year
    start_of_year = time_last_hour.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    balance_last_year = UserBalance.objects.filter(
        user=request.user,
        updated_at=start_of_year
    ).first()
    balance_last_year_value = balance_last_year.balance if balance_last_year else 0

    # Balance at the start is 1000
    balance_all_time = 1000

    # Calculate returns
    return_from_last_day = (
        0 if balance_last_day_value == 0
        else ((balance / balance_last_day_value) - 1) * 100
    )

    return_from_last_week = (
        0 if balance_last_week_value == 0
        else ((balance / balance_last_week_value) - 1) * 100
    )

    return_from_last_month = (
        0 if balance_last_month_value == 0
        else ((balance / balance_last_month_value) - 1) * 100
    )

    return_from_last_year = (
        0 if balance_last_year_value == 0
        else ((balance / balance_last_year_value) - 1) * 100
    )

    return_from_all_time = (
        0 if balance_all_time == 0
        else ((balance / balance_all_time) - 1) * 100
    )

    # Prepare context
    balance_context = {
        "current_balance": balance,
        "return_from_all_time": return_from_all_time,
        "balance_last_day": balance_last_day_value,
        "return_from_last_day": return_from_last_day,
        "balance_last_week": balance_last_week_value,
        "return_from_last_week": return_from_last_week,
        "balance_last_month": balance_last_month_value,
        "return_from_last_month": return_from_last_month,
        "balance_last_year": balance_last_year_value,
        "return_from_last_year": return_from_last_year,
    }

    return render(request, "portfolio.html", balance_context)


#Central template for spot orders
@login_required
def spot(request):
    current_positions = UserCrypto.objects.filter(user = request.user)
    current_avlb_balance = UserAvlbBalance.objects.get(user = request.user)
    context = {
        'current_positions': current_positions,
        'current_avlb_balance':current_avlb_balance
    }


    return render(request, 'spot.html',context)

@login_required
def market_order_form(request):

    if request.method == 'POST':
        form = MarketOrderForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].symbol
            quantity = form.cleaned_data['quantity']
            is_buy = form.cleaned_data['is_buy']
            take_profit = form.cleaned_data.get('take_profit')
            stop_loss = form.cleaned_data.get('stop_loss')
            is_buy = True if is_buy == 'True' else False
            current_prices = get_current_prices() #Fetch current price
            current_price = current_prices.get(symbol)

            #Failed to fail price
            if current_price is None:
                messages.error(request, f"Current price for '{symbol}' not available.")
                return render(request, 'market_order.html', {'form': form, 'order_type': 'market'})

            #Function that handles the input form
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
            
            except ValidationError as ve:
                form.add_error(None, str(ve))  # Add the validation error to the form
            except Exception as e:
                form.add_error(None, f"An unexpected error occurred: {e}")  # Catch unexpected errors
    else:
        form = MarketOrderForm()

    return render(request, 'market_order.html', {'form': form, 'order_type': 'market'})

#Limit order form
@login_required
def limit_order_form(request):
    if request.method == 'POST':
        form = LimitOrderForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].symbol
            quantity = form.cleaned_data['quantity']
            is_buy = form.cleaned_data['is_buy']
            take_profit = form.cleaned_data.get('take_profit')
            stop_loss = form.cleaned_data.get('stop_loss')
            is_buy = True if is_buy == 'True' else False
            current_prices = get_current_prices() #Fetch current price
            current_price = current_prices.get(symbol)
            limit_price = form.cleaned_data.get('limit_price')


            #Failed to fail price
            if current_price is None:
                messages.error(request, f"Current price for '{symbol}' not available.")
                return render(request, 'market_order.html', {'form': form, 'order_type': 'market'})

            #Function that handles the input form
            try:
                handle_limit_order(
                    user=request.user,
                    symbol=symbol,
                    quantity=quantity,
                    is_buy=is_buy,
                    current_price=current_price,
                    take_profit=take_profit if take_profit else None,
                    stop_loss=stop_loss if stop_loss else None,
                    limit_price = limit_price,
                    stop_price=None
                )
                messages.success(request, "Limit order placed successfully!")
                return redirect('spot')  # Redirect to the main spot page or a success page
            except ValidationError as ve:
                form.add_error(None, str(ve))  # Add the validation error to the form
            except Exception as e:
                form.add_error(None, f"An unexpected error occurred: {e}")  # Catch unexpected errors
    else:
        form = LimitOrderForm()

    return render(request, 'limit_order.html', {'form': form, 'order_type': 'limit'})

#Stop limit form
@login_required
def stop_limit_order_form(request):

    if request.method == 'POST':
        form = StopLimitOrderForm(request.POST)
        if form.is_valid():
            symbol = form.cleaned_data['symbol'].symbol
            quantity = form.cleaned_data['quantity']
            is_buy = form.cleaned_data['is_buy']
            take_profit = form.cleaned_data.get('take_profit')
            stop_loss = form.cleaned_data.get('stop_loss')
            is_buy = True if is_buy == 'True' else False
            current_prices = get_current_prices() #Fetch current price
            current_price = current_prices.get(symbol)
            limit_price = form.cleaned_data.get('limit_price')
            stop_price = form.cleaned_data.get('stop_price')


            #Failed to fail price
            if current_price is None:
                messages.error(request, f"Current price for '{symbol}' not available.")
                return render(request, 'stop_limit_order.html', {'form': form, 'order_type': 'stop_limit'})

            #Function that handles the input form
            try:
                handle_limit_order(
                    user=request.user,
                    symbol=symbol,
                    quantity=quantity,
                    is_buy=is_buy,
                    current_price=current_price,
                    take_profit=take_profit if take_profit else None,
                    stop_loss=stop_loss if stop_loss else None,
                    limit_price = limit_price,
                    stop_price=stop_price
                )
                messages.success(request, "Stop - Limit order placed successfully!")
                return redirect('spot')  # Redirect to the main spot page or a success page
            
            except ValidationError as ve:
                form.add_error(None, str(ve))  # Add the validation error to the form
            except Exception as e:
                form.add_error(None, f"An unexpected error occurred: {e}")  # Catch unexpected errors
    else:
        form = StopLimitOrderForm()

    return render(request, 'stop_limit_order.html', {'form': form, 'order_type': 'stop_limit'})


