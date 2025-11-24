import os
import json
import sys
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data_acquisition.stock_data import StockDataFetcher
from src.features.technical import TechnicalIndicators
from src.features.institutional import InstitutionalFeatures

app = Flask(__name__, 
            static_folder='../../web/static',
            template_folder='../../web/templates')
CORS(app)

# Initialize fetchers
fetcher = StockDataFetcher()
tech_calculator = TechnicalIndicators()
inst_extractor = InstitutionalFeatures()

# Cache stock list at startup
print("Initializing stock list cache...")
try:
    stock_list_cache = fetcher.get_stock_list()
    print(f"Stock list cached: {len(stock_list_cache)} stocks")
    print(f"Columns: {stock_list_cache.columns.tolist()}")
    print(f"Sample data:\n{stock_list_cache.head(3)}")
    # Check for specific stocks
    test_codes = ['600519', '600519.SH']
    for test_code in test_codes:
        match = stock_list_cache[stock_list_cache['ts_code'] == test_code]
        print(f"Match for '{test_code}': {len(match)} rows")
        if not match.empty:
            print(f"  -> {match[['ts_code', 'name']].values}")
except Exception as e:
    print(f"Failed to cache stock list: {e}")
    stock_list_cache = None

WATCHLIST_FILE = 'configs/watchlist.json'

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, 'r') as f:
            return json.load(f)
    return {"stocks": [], "updated_at": ""}

def save_watchlist(data):
    data['updated_at'] = datetime.now().isoformat()
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def normalize_code(code):
    """Ensure code has suffix for internal use"""
    if '.' not in code:
        if code.startswith('6'):
            return f"{code}.SH"
        elif code.startswith('0') or code.startswith('3'):
            return f"{code}.SZ"
        elif code.startswith('8') or code.startswith('4'):
            return f"{code}.BJ"
    return code

@app.route('/')
def index():
    return send_from_directory('../../web/templates', 'index.html')

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    data = load_watchlist()
    stocks_data = []
    
    for code in data.get('stocks', []):
        try:
            # Get latest daily data (or realtime if available)
            # For now, we use daily data for simplicity and reliability
            normalized_code = normalize_code(code)
            df = fetcher.get_daily_data(normalized_code)
            
            if not df.empty:
                latest = df.iloc[0]
                prev = df.iloc[1] if len(df) > 1 else latest
                
                # Calculate basic change
                change = latest['close'] - prev['close']
                pct_chg = (change / prev['close']) * 100
                
                # Try to get name from stock list
                stock_name = code
                if stock_list_cache is not None:
                    # Try matching with full code (e.g., 600519.SH)
                    name_match = stock_list_cache[stock_list_cache['ts_code'] == normalized_code]['name']
                    if name_match.empty:
                        # Try matching without suffix (e.g., 600519)
                        name_match = stock_list_cache[stock_list_cache['ts_code'] == code]['name']
                    if not name_match.empty:
                        stock_name = name_match.values[0]
                
                stock_info = {
                    'code': code,
                    'name': stock_name,
                    'price': float(latest['close']),
                    'change': float(change),
                    'pct_chg': float(pct_chg),
                    'volume': float(latest['vol']),
                    'date': latest['trade_date']
                }
                
                stocks_data.append(stock_info)
            else:
                # Try to get name even if data fetch failed
                stock_name = code
                normalized_code = normalize_code(code)
                if stock_list_cache is not None:
                    # Try matching with full code (e.g., 600519.SH)
                    name_match = stock_list_cache[stock_list_cache['ts_code'] == normalized_code]['name']
                    if name_match.empty:
                        # Try matching without suffix (e.g., 600519)
                        name_match = stock_list_cache[stock_list_cache['ts_code'] == code]['name']
                    if not name_match.empty:
                        stock_name = name_match.values[0]
                        
                stocks_data.append({
                    'code': code,
                    'name': stock_name,
                    'error': 'No data'
                })
        except Exception as e:
            print(f"Error fetching {code}: {e}")
            stocks_data.append({
                'code': code,
                'name': code,
                'error': str(e)
            })
            
    return jsonify(stocks_data)

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({'error': 'Code required'}), 400
    
    watchlist = load_watchlist()
    if code not in watchlist['stocks']:
        watchlist['stocks'].append(code)
        save_watchlist(watchlist)
    
    return jsonify({'success': True, 'stocks': watchlist['stocks']})

@app.route('/api/watchlist/<code_to_remove>', methods=['DELETE'])
def remove_from_watchlist(code_to_remove):
    watchlist = load_watchlist()
    if code_to_remove in watchlist['stocks']:
        watchlist['stocks'].remove(code_to_remove)
        save_watchlist(watchlist)
    
    return jsonify({'success': True, 'stocks': watchlist['stocks']})

@app.route('/api/stock/<code>')
def get_stock_detail(code):
    try:
        normalized_code = normalize_code(code)
        
        # Get daily data
        df = fetcher.get_daily_data(normalized_code)
        if df.empty:
            return jsonify({'error': 'No data found'}), 404
            
        # Calculate indicators
        df_indicators = tech_calculator.calculate_all_indicators(df)
        
        # Get institutional features
        inst_features = inst_extractor.extract_all_features(normalized_code, days=30)
        
        # Prepare response
        latest = df_indicators.iloc[0]
        
        # Convert numpy types to python types for JSON serialization
        def convert_val(val):
            if isinstance(val, (np.int64, np.int32)):
                return int(val)
            if isinstance(val, (np.float64, np.float32)):
                return float(val)
            return val

        if 'trade_date' not in latest:
             return jsonify({'error': 'Invalid data format: missing trade_date'}), 500
             
        response = {
            'info': {
                'code': code,
                'date': latest['trade_date'],
                'price': convert_val(latest.get('close', 0)),
                'open': convert_val(latest.get('open', 0)),
                'high': convert_val(latest.get('high', 0)),
                'low': convert_val(latest.get('low', 0)),
                'volume': convert_val(latest.get('vol', 0)),
            },
            'technical': {
                'ma5': convert_val(latest.get('ma_5')),
                'ma20': convert_val(latest.get('ma_20')),
                'rsi': convert_val(latest.get('rsi')),
                'macd': convert_val(latest.get('macd')),
            },
            'institutional': {k: convert_val(v) for k, v in inst_features.items()},
            'history': [] # Can add history for charts later
        }
        
        # Add last 30 days history for sparkline
        history = df_indicators.head(30)[['trade_date', 'close', 'vol']].to_dict('records')
        response['history'] = [{k: convert_val(v) for k, v in r.items()} for r in history]
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cache stock list
stock_list_cache = None

@app.route('/api/search')
def search_stocks():
    global stock_list_cache
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
        
    try:
        if stock_list_cache is None:
            print("Loading stock list cache...")
            stock_list_cache = fetcher.get_stock_list()
            print("Stock list cache loaded.")
            
        df = stock_list_cache
        # Filter by code or name
        mask = df['ts_code'].str.lower().str.contains(query) | df['name'].str.lower().str.contains(query)
        results = df[mask].head(10)
        
        return jsonify(results[['ts_code', 'name']].to_dict('records'))
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
