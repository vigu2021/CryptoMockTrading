import requests
import pandas as pd
from datetime import datetime
from candlestick.models import Candlestick
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
        
        # Append to the results
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

#Test

if __name__ == "__main__":
    symbol = "BTCUSDT"
    interval = "5m"  # 5-minute interval
    start_date = "2023-01-01 00:00:00"
    end_date = "2023-01-09 00:00:00"
    
    df = extract_transform_klines(symbol, interval, start_date, end_date)
    print(df.head())


def load_to_database(df, symbol_name):
    
    # Load candlestick data into the database.
    try:
        # Get the CryptoSymbols object for the given symbol_name
        symbol = CryptoSymbols.objects.get(symbol=symbol_name)
        
        with transaction.atomic():
            for _, row in df.iterrows():
                # Create and save a Candlestick object for each row
                Candlestick.objects.create(
                    symbol=symbol,
                    timestamp=row['Timestamp'],
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row['Volume']
                )
                
        print(f"Successfully loaded {len(df)} rows into the database for symbol: {symbol_name}")
    except CryptoSymbols.DoesNotExist:
        print(f"Error: Symbol '{symbol_name}' not found in the database.")
    except Exception as e:
        print(f"An error occurred while loading data: {e}")
