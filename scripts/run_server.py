import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Unset proxy environment variables to avoid connection issues
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

from src.api.app import app

if __name__ == '__main__':
    print("Starting Stock Watchlist Server...")
    print("Access at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
