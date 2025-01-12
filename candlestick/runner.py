import requests
import pandas as pd
from datetime import datetime,timedelta
from .etl import extract_transform_klines,load_to_database
from cryptos.models import CryptoSymbols
from .models import Candlestick
from django.db import transaction


def etl_runner(interval, start_date, end_date):
    '''
    ETL runner for all cryptocurrencies in the CryptoSymbols database.
    Processes data in bulks of 500 rows per symbol.
    '''

    # Get all symbols from the CryptoSymbols database
    all_cryptos = CryptoSymbols.objects.all()
    all_symbols = [crypto.symbol for crypto in all_cryptos]
    print(f"Starting ETL process for {len(all_symbols)} symbols...")

    for symbol_name in all_symbols:
        try:
            print(f"Processing symbol: {symbol_name}...")

            # Extract and transform data for the symbol
            df = extract_transform_klines(symbol_name, interval, start_date, end_date)

            # Get the related CryptoSymbols object
            symbol_obj = CryptoSymbols.objects.get(symbol=symbol_name)

            # Use the load function to load the data into the database
            load_to_database(df, symbol_obj)

        except Exception as e:
            print(f"An error occurred while processing symbol {symbol_name}: {e}")



if __name__ == "__main__":
    interval = "5m"

    end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

    print(f"Loading data from {start_date} to {end_date}...")

    # Run the ETL process
    etl_runner(interval, start_date, end_date)
