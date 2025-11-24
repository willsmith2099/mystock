import os
import requests
import akshare as ak

# Clear proxy envs
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

print("Testing connection to eastmoney...")
try:
    # URL similar to what akshare uses
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    resp = requests.get(url, timeout=5)
    print(f"Direct request status: {resp.status_code}")
except Exception as e:
    print(f"Direct request failed: {e}")

print("\nTesting AkShare stock list...")
try:
    df = ak.stock_info_a_code_name()
    print(f"Got {len(df)} stocks")
    print(df.head())
except Exception as e:
    print(f"AkShare failed: {e}")
