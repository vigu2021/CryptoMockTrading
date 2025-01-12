import requests
import pandas as pd
from datetime import datetime
from .models import Candlestick
from cryptos.models import CryptoSymbols
from django.db import transaction


def extract_transform_klines(symbol, interval, start_date, end_date):
    """
    Extract and transform candlestick data from Binance API with pagination.
    """
    base_url = "https://api.binance.com/api/v3/klines"
    
    # Convert dates to timestamps in milliseconds
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
    
    all_klines = []  # To store all the paginated results

    while start_timestamp < end_timestamp:
        # Prepare API request
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_timestamp,
            'endTime': end_timestamp,
            'limit': 1000  # Max limit per request
        }
        
        # Fetch data
        response = requests.get(base_url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching data from Binance API: {response.status_code} {response.text}")
        
        # Parse response
        klines = response.json()
        if not klines:
            break  # Break if no more data is returned
        
        all_klines.extend(klines)
        
        # Update start timestamp for the next batch
        start_timestamp = klines[-1][6]  # Use the last candle's close time as the new start time
    
    # Convert to DataFrame
    df = pd.DataFrame(all_klines, columns=[
        'OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume',
        'CloseTime', 'QuoteAssetVolume', 'NumberOfTrades',
        'TakerBuyBaseVolume', 'TakerBuyQuoteVolume', 'Ignore'
    ])
    
    # Transform DataFrame
    df['OpenTime'] = pd.to_datetime(df['OpenTime'], unit='ms')
    df = df.rename(columns={'OpenTime': 'Timestamp'})
    df = df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    
    return df



#Load to database
def load_to_database(df, symbol_obj):

    try:
        # Create a list of Candlestick objects
        candlestick_objects = [
            Candlestick(
                symbol=symbol_obj,
                timestamp=row['Timestamp'],
                open=row['Open'],
                high=row['High'],
                low=row['Low'],
                close=row['Close'],
                volume=row['Volume']
            )
            for _, row in df.iterrows()
        ]
        
        # Bulk insert using batch size of 500
        with transaction.atomic():
            for i in range(0, len(candlestick_objects), 500):
                Candlestick.objects.bulk_create(candlestick_objects[i:i+500], batch_size=500)

        print(f"Successfully loaded {len(candlestick_objects)} rows for symbol: {symbol_obj.symbol}")

    except Exception as e:
        print(f"An error occurred while loading data for symbol {symbol_obj.symbol}: {e}")
