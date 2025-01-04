from .models import UserAvlbBalance,UserCrypto,Orders
from decimal import Decimal

def handle_market_order(user,symbol,quantity,is_buy,current_price,take_profit,stop_loss):
    
    transaction_cost = current_price * quantity  #Transaction cost for order
    avaliable_balance = UserAvlbBalance.objects.get(user = user)

    #If transaction cost higher than avaliable_balance return error.
    if transaction_cost > avaliable_balance.avlb_balance: 

    

