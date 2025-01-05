# cryptos/scripts/get_current_prices.py

import requests
from cryptos.models import CryptoSymbols
import logging

# Configure logging
logger = logging.getLogger(__name__)

def get_current_prices():
    """
    Fetch current prices for all symbols in the CryptoSymbols database from Binance API.
    Returns a dictionary mapping symbols to their current prices.
    """
    fetch_all_symbols = CryptoSymbols.objects.all()
    all_symbols = [entry.symbol for entry in fetch_all_symbols]

    symbol_prices = {}
    for symbol in all_symbols:
        try:
            # Make an API call to Binance to get the current price of the symbol
            url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
            logger.debug(f"Fetching price for symbol: {symbol}")
            response = requests.get(url, timeout=5)  # Added timeout for better error handling
            data = response.json()

            if response.status_code == 200:
                price = data.get('price')
                if price:
                    symbol_prices[symbol] = price
                    logger.info(f"Retrieved {symbol}: {price}")
                else:
                    logger.warning(f"Price not found in response for {symbol}: {data}")
            else:
                logger.error(f"Failed to fetch price for {symbol}: {data}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error fetching price for {symbol}: {str(req_err)}")
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")

    return symbol_prices

