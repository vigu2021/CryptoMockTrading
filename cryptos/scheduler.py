
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .models import UserBalance,UserLimitBalance,UserAvlbBalance,UserCrypto,Orders
from .scripts.get_current_prices import get_current_prices
from decimal import Decimal
from datetime import datetime,timezone
from apscheduler.triggers.interval import IntervalTrigger




# balance = Avlb balance + Limit balance + Crypto Holdings
def update_balance():

    current_prices = get_current_prices()  # Fetch current prices
    avlb_balances = UserAvlbBalance.objects.iterator()
    current_datetime = datetime.now().replace(minute=0, second=0, microsecond=0) #Fetch at the start of the hour make sure database in consistent


    # Every user has a exactly 1 avlb_balance (one to one relationship)
    for avlb_balance in avlb_balances:

        user = avlb_balance.user

        # Fetch avlb_balance
        try:
            user_avlb_balance = avlb_balance.avlb_balance
        except AttributeError:
            user_avlb_balance = 0

        #Fetch limit_balance
        try:
            user_limit_balance = UserLimitBalance.objects.get(user=user).limit_balance
        except UserLimitBalance.DoesNotExist:
            user_limit_balance = 0
        
        balance = user_limit_balance + user_avlb_balance

        #Calculate crypto holdings
        crypto_holdings = UserCrypto.objects.filter(user=user)
        # Calculate value of crypto holdings and add to balance
        for crypto in crypto_holdings:
            current_price = current_prices.get(crypto.symbol.symbol,0)
            balance += crypto.quantity * Decimal(current_price)
           
        
        UserBalance.objects.create(updated_at=current_datetime, user=user, balance=balance)
        print("uploaded")




def update_order_status():
    current_prices = get_current_prices()  # Fetch the current market prices
    
    # Handle stop-limit orders (PENDING → EXECUTED)
    pending_orders = Orders.objects.filter(status='PENDING')  # Orders pending execution
    for order in pending_orders:
        current_price = Decimal(current_prices.get(order.symbol.symbol))  # Get current price for the asset

        if current_price is None:
            # Skip if the current price is not available for the asset
            continue

        if order.is_buy and current_price >= order.stop_price:
            # Transition from stop-limit to limit order (EXECUTED)
            order.status = 'EXECUTED'
            order.save()

        elif not order.is_buy and current_price <= order.stop_price:
            # Transition from stop-limit to limit order (EXECUTED)
            order.status = 'EXECUTED'
            order.save()

    # Handle limit orders (EXECUTED → COMPLETED)
    executed_orders = Orders.objects.filter(status='EXECUTED')
    for order in executed_orders:
        current_price = Decimal(current_prices.get(order.symbol.symbol))  # Get current price for the asset

        if current_price is None:
            # Skip if the current price is not available for the asset
            continue

        if order.is_buy and current_price <= order.limit_price:
            # Buy order: Fulfill and complete the order
            order.status = 'COMPLETED'
            order.price = current_price
            order.save()

            # Update user holdings
            try:
                current_holdings = UserCrypto.objects.get(user=order.user, symbol=order.symbol)
                current_holdings.avg_price = (
                    (current_holdings.avg_price * current_holdings.quantity + order.quantity * order.price) /
                    (current_holdings.quantity + order.quantity)
                )
                current_holdings.quantity += order.quantity
                current_holdings.save()

            except UserCrypto.DoesNotExist:
                # Create a new holding if none exists
                UserCrypto.objects.create(
                    user=order.user,
                    symbol=order.symbol,
                    avg_price=order.price,
                    quantity=order.quantity
                )
            limit_balance = UserLimitBalance.objects.get(user = order.user)
            limit_balance.limit_balance -= order.price * order.quantity
            limit_balance.save()

        elif not order.is_buy and current_price >= order.limit_price:
            # Sell order: Fulfill and complete the order
            order.status = 'COMPLETED'
            order.price = current_price
            order.save()

            # Update user holdings
            try:
                current_holdings = UserCrypto.objects.get(user=order.user, symbol=order.symbol)
                if current_holdings.quantity >= order.quantity:
                    current_holdings.quantity -= order.quantity
                    current_holdings.save()
                else:
                    raise ValueError(f"Insufficient holdings to sell {order.quantity} of {order.symbol}")

            except UserCrypto.DoesNotExist:
                raise ValueError(f"User does not own any holdings of {order.symbol}")



def start_balance_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_balance,
        trigger=CronTrigger(minute="0"),  # Runs at the start of every hour
        id="scheduled_update_balance",
        replace_existing=True,
        misfire_grace_time=60
    )
    scheduler.start()
    print("Balance Scheduler started")


def start_order_status_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_order_status,
        trigger=IntervalTrigger(seconds=10),  # Runs every 10 seconds
        id="scheduled_update_order_status",
        replace_existing=True,
        misfire_grace_time=60
    )
    scheduler.start()
    print("Order Status Scheduler started")