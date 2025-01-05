from django.db import transaction
from .models import Orders, UserAvlbBalance, UserCrypto, CryptoSymbols
from decimal import Decimal
from django.core.exceptions import ValidationError


def handle_market_order(user, symbol, quantity, is_buy, current_price, take_profit, stop_loss):
    try:
        with transaction.atomic():
            # Retrieve or create user balance
            balance = UserAvlbBalance.objects.get(user=user)

            # Retrieve the CryptoSymbols instance
            crypto_symbol = CryptoSymbols.objects.get(symbol=symbol)

            if is_buy:
                transaction_cost = current_price * quantity
                if balance.avlb_balance < transaction_cost:
                    raise ValidationError("Insufficient Balance")
                balance.avlb_balance -= transaction_cost
                balance.save()


                #Take profit can't be lower than current price for buy orders
                if take_profit is not None and take_profit <= current_price:
                    raise ValidationError("Take profit must be higher than current market price")
                

                # Create the order
                order = Orders.objects.create(
                    user=user,
                    symbol=crypto_symbol,
                    order_type='MARKET',
                    price=current_price,
                    quantity=quantity,
                    take_profit=take_profit,
                    stop_loss=stop_loss,
                    is_buy=is_buy,
                    status='EXECUTED'
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
                
                #Take profit must be lower than current price for sell orders
                if take_profit is not None and take_profit >= current_price:
                    raise ValidationError("Take profit can't be higher than current price")
                

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
                    take_profit=take_profit,
                    stop_loss=stop_loss,
                    is_buy=is_buy,
                    status='EXECUTED'
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

'''
def handle_limit_order(user, symbol, quantity, is_buy, current_price, take_profit, stop_loss,limit_price):
    try:
        with transaction.atomic():
            balance = UserAvlbBalance.objects.get(user=user)

            # Retrieve the CryptoSymbols instance
            crypto_symbol = CryptoSymbols.objects.get(symbol=symbol)



'''









            

            

