import sys
import os
# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cryptotrader.settings')
django.setup()

import requests
from cryptos.models import CryptoSymbols

def get_current_prices(): #For all cryptos in the symbols database
    fetch_all_symbols = CryptoSymbols.objects.all()
    all_symbols  = [entry.symbol for entry in fetch_all_symbols]

    symbol_prices = {}
    for symbol in all_symbols:
        try:
            # Make an API call to Binance to get the current price of the symbol
            url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                price = data['price']
                symbol_prices[symbol] = price
                print(f"{symbol}: {price}")
            else:
                print(f"Failed to fetch price for {symbol}: {data}")
        except Exception as e:
            print(f"Error fetching price for {symbol}: {str(e)}")

    return symbol_prices    


