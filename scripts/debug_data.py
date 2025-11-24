import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_acquisition.stock_data import StockDataFetcher

# Unset proxy
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

fetcher = StockDataFetcher()
print("Fetching stock list...")
try:
    df = fetcher.get_stock_list()
    print("Columns:", df.columns.tolist())
    print("Head:\n", df.head())
except Exception as e:
    print(f"Error: {e}")
