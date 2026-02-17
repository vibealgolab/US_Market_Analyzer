# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US Market Analyzer - Flask Backend
Provides API endpoints for the dashboard.
"""

import os
import json
import threading
import pandas as pd
import numpy as np
import yfinance as yf
import subprocess
from flask import Flask, render_template, jsonify, request
import traceback
from datetime import datetime

app = Flask(__name__)

# Directory where data files are stored - Absolute path for reliability
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

# Helper to fetch sector if not present
def get_sector(ticker: str) -> str:
    # Simplified sector fetcher for the demo/backend
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('sector', 'N/A')
    except:
        return 'N/A'

@app.route('/')
def index():
    return render_template('index.html')

# --- US MARKET API ENDPOINTS ---

@app.route('/api/us/macro-analysis')
def get_us_macro_analysis():
    """Get macro market indicators and AI analysis"""
    try:
        path = os.path.join(DATA_DIR, 'macro_analysis.json')
        if not os.path.exists(path):
            return jsonify({'error': 'Macro analysis data not found. Run macro_analyzer.py first.'}), 404
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Update key indices with real-time data for the dashboard
        live_tickers = {'SPY': 'SPY', 'QQQ': 'QQQ', 'VIX': '^VIX', 'BTC': 'BTC-USD'}
        for name, ticker in live_tickers.items():
            try:
                stock = yf.Ticker(ticker)
                h = stock.history(period='2d')
                if not h.empty:
                    curr = h['Close'].iloc[-1]
                    prev = h['Close'].iloc[-2]
                    change_pct = ((curr / prev) - 1) * 100
                    if 'macro_indicators' not in data: data['macro_indicators'] = {}
                    data['macro_indicators'][name] = {
                        'value': round(float(curr), 2),
                        'change_1d': round(float(change_pct), 2)
                    }
            except: pass
            
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/smart-money')
def get_us_smart_money():
    """Get current top stock picks"""
    try:
        path = os.path.join(DATA_DIR, 'smart_money_current.json')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify({'top_picks': data.get('picks', []), 'updated': data.get('updated', '--')})
        
        # Fallback to CSV
        csv_path = os.path.join(DATA_DIR, 'smart_money_picks_v2.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path).head(30)
            picks = df.fillna('N/A').to_dict(orient='records')
            return jsonify({'top_picks': picks, 'updated': 'CSV Fallback'})
                
        return jsonify({'error': 'Screener results not found. Run screener first.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/etf-flows')
def get_us_etf_flows():
    """Get ETF fund flow analysis"""
    try:
        csv_path = os.path.join(DATA_DIR, 'us_etf_flows.csv')
        ai_path = os.path.join(DATA_DIR, 'etf_flow_analysis.json')
        
        if not os.path.exists(csv_path):
            return jsonify({'error': 'ETF data not found.'}), 404
            
        df = pd.read_csv(csv_path)
        ai_data = {}
        if os.path.exists(ai_path):
            with open(ai_path, 'r', encoding='utf-8') as f:
                ai_data = json.load(f)
        
        return jsonify({
            'flows': df.to_dict(orient='records'),
            'ai_analysis': ai_data.get('ai_analysis', 'Data available. Run analyze_etf_flows.py for AI insights.')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/sector-heatmap')
def get_us_sector_heatmap():
    """Get sector performance treemap data"""
    try:
        path = os.path.join(DATA_DIR, 'sector_heatmap.json')
        if not os.path.exists(path):
            return jsonify({'error': 'Heatmap data not found.'}), 404
        with open(path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/options-flow')
def get_us_options_flow():
    try:
        path = os.path.join(DATA_DIR, 'options_flow.json')
        if not os.path.exists(path):
            return jsonify({'error': 'Options data not found.'}), 404
        with open(path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/calendar')
def get_us_calendar():
    try:
        path = os.path.join(DATA_DIR, 'weekly_calendar.json')
        if not os.path.exists(path):
            return jsonify({'events': []})
        with open(path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Simple memory cache for stock data
chart_cache = {}
CACHE_TIMEOUT = 3600  # 1 hour

def get_cached_history(ticker, period='1y'):
    """Fetch history with caching to avoid rate limits"""
    # Normalize period (lightweight-charts uses '1m', yfinance needs '1mo')
    yf_period = '1mo' if period == '1m' else period
    
    cache_key = f"{ticker}_{yf_period}"
    now = datetime.now()
    
    if cache_key in chart_cache:
        data, timestamp = chart_cache[cache_key]
        if (now - timestamp).total_seconds() < CACHE_TIMEOUT:
            return data
            
    stock = yf.Ticker(ticker)
    hist = stock.history(period=yf_period)
    
    if not hist.empty:
        chart_cache[cache_key] = (hist, now)
    return hist

@app.route('/api/us/stock-chart/<ticker>')
def get_us_stock_chart(ticker):
    """Get candlestick data for a ticker with caching"""
    try:
        period = request.args.get('period', '1y')
        hist = get_cached_history(ticker, period)
        
        if hist.empty:
            return jsonify({'error': 'No data available or rate limited'}), 404
            
        candles = []
        for date, row in hist.iterrows():
            candles.append({
                'time': int(date.timestamp()),
                'open': round(float(row['Open']), 2),
                'high': round(float(row['High']), 2),
                'low': round(float(row['Low']), 2),
                'close': round(float(row['Close']), 2),
                'volume': int(row['Volume'])
            })
        return jsonify({'ticker': ticker, 'candles': candles})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/technical-indicators/<ticker>')
def get_us_technical_indicators(ticker):
    """Calculate and return indicators using cached data"""
    try:
        period = request.args.get('period', '1y')
        df = get_cached_history(ticker, period)
        
        if df.empty or len(df) < 20:
            return jsonify({'error': 'Insufficient data for indicators'}), 404
            
        close = df['Close']
        
        # 1. RSI (Relative Strength Index) - 14 period
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 2. MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line
        
        # 3. Bollinger Bands
        sma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        bb_upper = sma20 + (std20 * 2)
        bb_lower = sma20 - (std20 * 2)
        
        timestamps = [int(t.timestamp()) for t in df.index]
        
        indicators = {
            'ticker': ticker,
            'timestamps': timestamps,
            'rsi': rsi.fillna(0).tolist(),
            'macd': {
                'line': macd_line.fillna(0).tolist(),
                'signal': signal_line.fillna(0).tolist(),
                'hist': macd_hist.fillna(0).tolist()
            },
            'bb': {
                'upper': bb_upper.fillna(0).tolist(),
                'lower': bb_lower.fillna(0).tolist(),
                'middle': sma20.fillna(0).tolist()
            }
        }
        
        return jsonify(indicators)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/ai-summary/<ticker>')
def get_us_ai_summary(ticker):
    try:
        path = os.path.join(DATA_DIR, 'ai_summaries.json')
        if not os.path.exists(path):
            return jsonify({'summary': None}) # Return null so UI knows to show button
        with open(path, 'r', encoding='utf-8') as f:
            summaries = json.load(f)
            result = summaries.get(ticker)
            if not result or "Failed" in result.get('summary', ''):
                return jsonify({'summary': None})
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/generate-ai-summary/<ticker>', methods=['POST'])
def generate_us_ai_summary(ticker):
    """Triggered on-demand by user button"""
    try:
        from analysis.ai_summary_generator import AIStockAnalyzer
        analyzer = AIStockAnalyzer()
        result = analyzer.analyze_single_ticker(ticker)
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/realtime-prices', methods=['POST'])
def get_realtime_prices():
    """Fetch batch real-time prices for the dashboard"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        if not tickers: return jsonify({})
        
        # Batch fetch via yf.download (faster for multiple)
        df = yf.download(tickers, period='1d', interval='1m', progress=False)
        if df.empty: return jsonify({})
        
        prices = {}
        # Handle both single ticker (Series) and multiple (DataFrame)
        if len(tickers) == 1:
            t = tickers[0]
            prices[t] = {'current': round(float(df['Close'].iloc[-1]), 2)}
        else:
            for t in tickers:
                try:
                    val = df['Close'][t].iloc[-1]
                    if not np.isnan(val):
                        prices[t] = {'current': round(float(val), 2)}
                except: pass
        return jsonify(prices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

PIPELINE_LOCK = threading.Lock()
LAST_PIPELINE_RUN = datetime(2000, 1, 1)

@app.route('/api/run-pipeline', methods=['POST'])
def run_pipeline():
    """Trigger the update_all.py script in background with safety lock"""
    global LAST_PIPELINE_RUN
    
    # Auto-trigger cooldown: 1 minute (for debugging)
    now = datetime.now()
    if (now - LAST_PIPELINE_RUN).total_seconds() < 60:
        return jsonify({'status': 'skipped', 'reason': 'Cooldown active (1m)'})

    if PIPELINE_LOCK.locked():
        return jsonify({'status': 'busy', 'reason': 'Pipeline already running'})

    try:
        def run():
            with PIPELINE_LOCK:
                logger.info("🔥 Starting Full Pipeline Update via Background Thread...")
                subprocess.run(['python', 'update_all.py'], check=True)
                logger.info("✅ Full Pipeline Update Completed.")
        
        LAST_PIPELINE_RUN = now
        threading.Thread(target=run, daemon=True).start()
        return jsonify({'status': 'started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline-status')
def get_pipeline_status():
    """Get real-time progress of the background pipeline"""
    path = os.path.join(DATA_DIR, 'pipeline_status.json')
    if not os.path.exists(path):
        return jsonify({"current_task": "Idle", "progress": "0%", "is_running": PIPELINE_LOCK.locked()})
    
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            data["is_running"] = PIPELINE_LOCK.locked()
            return jsonify(data)
    except:
        return jsonify({"current_task": "Starting...", "is_running": True})
@app.route('/api/us/quota-status')
def get_us_quota_status():
    """Aggregated quota status for Quota Shield 2.0"""
    try:
        path = os.path.join(DATA_DIR, 'quota_states.json')
        if not os.path.exists(path):
            return jsonify({"total_requests_today": 0, "rpd_limit": 1000, "requests_this_minute": 0, "active_keys": 1})
            
        with open(path, 'r', encoding='utf-8') as f:
            states = json.load(f)
            
        total_today = sum(s.get('total_requests_today', 0) for s in states.values())
        active_keys = len(states)
        limit = active_keys * 1000
        max_rpm = max([s.get('requests_this_minute', 0) for s in states.values()] or [0])
        
        return jsonify({
            "total_requests_today": total_today,
            "rpd_limit": limit,
            "requests_this_minute": max_rpm,
            "active_keys": active_keys
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/us/risk-overview')
def get_us_risk_overview():
    """Get aggregated insider moves and portfolio risk signals"""
    try:
        insider_path = os.path.join(DATA_DIR, 'insider_moves.json')
        risk_path = os.path.join(DATA_DIR, 'portfolio_risk.json')
        
        data = {'insider_moves': [], 'risk_signals': {}}
        
        if os.path.exists(insider_path):
            with open(insider_path, 'r', encoding='utf-8') as f:
                data['insider_moves'] = json.load(f).get('moves', [])
        
        if os.path.exists(risk_path):
            with open(risk_path, 'r', encoding='utf-8') as f:
                data['risk_signals'] = json.load(f)
                
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Flask app listens on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
