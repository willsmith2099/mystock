import akshare as ak
import os

# Unset proxy
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

print("Testing Sina Daily History...")
try:
    # Sina usually uses sh/sz prefix
    df = ak.stock_zh_a_daily(symbol="sh600519", start_date="20240101", end_date="20241121")
    print(f"Sina daily shape: {df.shape}")
    print(df.tail())
except Exception as e:
    print(f"Sina daily failed: {e}")

print("\nTesting Sina Spot (if exists)...")
try:
    if hasattr(ak, 'stock_zh_a_spot_sina'):
        df = ak.stock_zh_a_spot_sina()
        print(f"Sina spot shape: {df.shape}")
        print(df.head())
    else:
        print("stock_zh_a_spot_sina not found")
except Exception as e:
    print(f"Sina spot failed: {e}")
