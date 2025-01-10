
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .models import UserBalance,UserLimitBalance,UserAvlbBalance,UserCrypto
from .scripts.get_current_prices import get_current_prices
from decimal import Decimal
from datetime import datetime



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


# Initialize and start the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_balance,
        trigger=CronTrigger(minute="0"),  # Runs at the start of every hour
        id="scheduled_update_balance",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started")