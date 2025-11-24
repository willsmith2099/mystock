import akshare as ak
import os
import time

# Unset proxy
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

print("Testing Sina Quote...")
try:
    # Sina usually requires sh/sz prefix
    df = ak.stock_zh_a_spot() # This might be deprecated or huge
    print(f"Sina spot shape: {df.shape}")
    print(df.head())
except Exception as e:
    print(f"Sina spot failed: {e}")

print("\nTesting Individual Stock Quote (Sina)...")
try:
    # There isn't a direct single-stock quote in standard public akshare docs easily recallable, 
    # but stock_zh_a_spot is the main one.
    # Let's try a specific function if known.
    pass
except Exception as e:
    print(f"Sina single failed: {e}")

print("\nTesting Eastmoney History (again)...")
try:
    df = ak.stock_zh_a_hist(symbol="600519", period="daily", start_date="20240101", end_date="20240110")
    print(f"Eastmoney hist shape: {df.shape}")
except Exception as e:
    print(f"Eastmoney hist failed: {e}")
