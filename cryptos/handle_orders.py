from .models import UserAvlbBalance,UserCrypto,Orders
from decimal import Decimal
from django.core.exceptions import ValidationError
from datetime import datetime

def handle_market_order(user,symbol,quantity,is_buy,current_price,take_profit,stop_loss):
    
   
    avaliable_balance = UserAvlbBalance.objects.get(user = user)

    #Buy logic 
    if is_buy:
        transaction_cost = current_price * quantity  #Transaction cost for order

    #If transaction cost higher than avaliable_balance return error.
        if transaction_cost > avaliable_balance.avlb_balance: 
            raise ValidationError("Insufficent Balance")
        
        #Store record in orders table
        Orders.objects.create(
            user = user,
            symbol = symbol,
            status = "EXECUTED",
            order_type = 'MARKET',
            price = current_price,
            quantity = quantity,
            take_profit = take_profit,
            stop_loss = stop_loss,
            is_buy = is_buy
        )

        #Deduct transaction cost and update time in UserAvlbBalance table
        avaliable_balance.updated_at = datetime.now()
        avaliable_balance.avlb_balance -= transaction_cost
        avaliable_balance.save()


        #Update UserCrypto table
        object,created = UserCrypto.objects.get_or_create(
            user = user,
            symbol = symbol,
            #If new instance is created
            defaults={
            'avg_price': current_price,
            'quantity': quantity
                     }
        )
        #If created just save the instance
        if created:
            object.save()

        #Else we are updating a current instance
        else:
            object.updated_at = datetime.now()
            object.avg_price = (current_price * quantity + object.avg_price * object.quantity)/(quantity + object.quantity)
            object.quantity += quantity
            object.save()

    #Sell logic 
    else:
        # If you don't own the crypto you can't sell nothing.
        try:
            current_crypto = UserCrypto.objects.get(user = user)
        except UserCrypto.DoesNotExist:
            raise ValidationError("You don't own this crypto.")
        
        if current_crypto.quantity < quantity:
            raise ValidationError("Quantity higher than the amount you own")
        
        
        

        

        


        
        
       
        
        









    

    

