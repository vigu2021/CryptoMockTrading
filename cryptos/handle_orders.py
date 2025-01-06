from django.db import transaction
from .models import Orders,UserAvlbBalance, UserCrypto, CryptoSymbols,UserLimitBalance
from decimal import Decimal
from django.core.exceptions import ValidationError,ObjectDoesNotExist


def handle_market_order(user, symbol, quantity, is_buy, current_price, take_profit, stop_loss):
    try:
        with transaction.atomic():
            # Retrieve or create user balance
            balance = UserAvlbBalance.objects.get(user=user)
            crypto_symbol = CryptoSymbols.objects.get(symbol=symbol)
            if is_buy:
                #Take profit can't be lower than current price for buy orders
                if take_profit is not None and take_profit <= current_price:
                    raise ValidationError("Take profit must be higher than current market price")
                
                #Stop loss can't be higher than current price
                if stop_loss is not None and stop_loss >= current_price:
                    raise ValidationError("Stop loss must be lower than current market price")
        
                transaction_cost = current_price * quantity
                if balance.avlb_balance < transaction_cost:
                    raise ValidationError("Insufficient Balance")
                balance.avlb_balance -= transaction_cost
                balance.save()

                # Create the order
                order = Orders.objects.create(
                    user=user,
                    symbol=crypto_symbol,
                    order_type='MARKET',
                    price=current_price,
                    quantity=quantity,
                    take_profit=take_profit,
                    stop_loss=stop_loss,
                    is_buy=True,
                    status='COMPLETED'
                )

                # Update UserCrypto
                user_crypto, created = UserCrypto.objects.get_or_create(
                    user=user,
                    symbol=crypto_symbol,
                    defaults={'avg_price': current_price, 'quantity': quantity}
                )
                if not created:
                    # Update average price
                    total_cost = user_crypto.avg_price * user_crypto.quantity + current_price * quantity
                    user_crypto.quantity += quantity
                    user_crypto.avg_price = total_cost / user_crypto.quantity
                    user_crypto.save()
            else:
                # Sell logic

                user_crypto = UserCrypto.objects.get(user=user, symbol=crypto_symbol)
                if user_crypto.quantity < quantity:
                    raise ValidationError("Quantity higher than the amount you own")
                
                #Can't have take profit for stop_loss or stop_loss
                if take_profit or stop_loss:
                    raise ValidationError("Take profit and stop loss orders are not allowed for sell transactions.")
                
                proceeds = current_price * quantity
                balance.avlb_balance += proceeds
                balance.save()

                # Create the order
                order = Orders.objects.create(
                    user=user,
                    symbol=crypto_symbol,
                    order_type='MARKET',
                    price=current_price,
                    quantity=quantity,
                    is_buy=False,
                    status='COMPLETED'
                )

                # Update UserCrypto
                user_crypto.quantity -= quantity
                if user_crypto.quantity == 0:
                    user_crypto.delete()
                else:
                    user_crypto.save()

           
    except ValidationError as ve:
        raise ve
    except Exception as e:
        raise ValidationError("An unexpected error occurred while processing the order.")


#Creates order for limit and stop_limit

def handle_limit_order(user, symbol, quantity, is_buy, current_price, take_profit, stop_loss,limit_price,stop_price):
    try:
        with transaction.atomic():
            avlb_balance = UserAvlbBalance.objects.get(user=user)
            limit_balance = UserLimitBalance.objects.get(user = user)
           # Retrieve the CryptoSymbols instance
            crypto_symbol = CryptoSymbols.objects.get(symbol=symbol)

            if is_buy:
                transaction_cost = limit_price * quantity
                if transaction_cost > avlb_balance.avlb_balance:
                    raise ValidationError("Insufficient Balance")
                
                if take_profit is not None and limit_price > take_profit:
                    raise ValidationError("Limit price has to be lower than take profit")
                
                if stop_loss is not None and limit_price < stop_loss:
                    raise ValidationError("Stop price has to be lower than limit price")
                
                #Deduct avalaible balance
                avlb_balance.avlb_balance -= transaction_cost
                avlb_balance.save()
                #Add the transaction cost to current limit balance
                limit_balance.limit_balance += transaction_cost
                limit_balance.save()
                
                #Stop limit order
                if stop_price:
                    order = Orders.objects.create(
                    user=user,
                    symbol=crypto_symbol,
                    order_type='STOPLIMIT',
                    price=current_price,
                    limit_price = limit_price,
                    stop_price = stop_price,
                    quantity=quantity,
                    take_profit=take_profit,
                    stop_loss=stop_loss,
                    is_buy=True,
                    status='PENDING',
                    )
                
                #Limit Order
                else:
                    order = Orders.objects.create(
                    user=user,
                    symbol=crypto_symbol,
                    order_type='LIMIT',
                    price=current_price,
                    limit_price = limit_price,
                    quantity=quantity,
                    is_buy=True,
                    status='EXECUTED',
                    )
                
            else:
                try:
                    user_crypto = UserCrypto.objects.get(user=user, symbol=crypto_symbol)
                except ObjectDoesNotExist:
                    raise ValidationError(f"No holdings for symbol '{symbol}' found")
                

                if user_crypto.quantity < quantity:
                    raise ValidationError("Insufficient crypto balance to sell")
                
                if take_profit or stop_loss:
                    raise ValidationError("Take profit and stop loss orders are not allowed for sell transactions.")

                #Stop Limit order
                if stop_price:
                    order = Orders.objects.create(
                    user=user,
                    symbol=crypto_symbol,
                    order_type='STOPLIMIT',
                    price=current_price,
                    limit_price = limit_price,
                    stop_price = stop_price,
                    quantity=quantity,
                    is_buy=False,
                    status='PENDING',
                    )

                #Limit Order
                else:
                    order = Orders.objects.create(
                    user=user,
                    symbol=crypto_symbol,
                    order_type='LIMIT',
                    price=current_price,
                    limit_price = limit_price,
                    quantity=quantity,
                    is_buy=False,
                    status='EXECUTED',
                    )

    except ValidationError as ve:
        raise ve
    except Exception as e:
        raise ValidationError("An unexpected error occurred while processing the order.")        
            
            
                


            












            

            

