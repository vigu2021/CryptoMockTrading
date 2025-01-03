
'''
Uploads crypto pairs into symbols database
This will be used as choices of cryptos user can choose to mock trade
'''

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cryptotrader.settings')
django.setup()

from cryptos.models import CryptoSymbols
#For now only these ones
crypto_usdt_pairs = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "SOLUSDT",
    "ADAUSDT",
    "TRXUSDT",
    "DOTUSDT",
    "LTCUSDT",
    "LINKUSDT",
    "SHIBUSDT",
    "MATICUSDT",
    "BCHUSDT",
    "XLMUSDT",
    "UNIUSDT",
    "ATOMUSDT",
    "ETCUSDT",
    "FILUSDT",
    "APEUSDT"
]

def upload_symbols(trading_pairs):
    """
    Uploads a list of trading pairs to the CryptoSymbols table in the database.
    If a symbol already exists, it skips the insertion.
    """
    for symbol in trading_pairs:
        # Check if the symbol already exists in the database
        if not CryptoSymbols.objects.filter(symbol=symbol).exists():
            # Create a new entry if it doesn't exist
            CryptoSymbols.objects.create(symbol=symbol)
            print(f"Added: {symbol}")
        else:
            print(f"Symbol already exists: {symbol}")

if __name__ == '__main__':
    upload_symbols(crypto_usdt_pairs)
