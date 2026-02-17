# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Options Flow Analyzer
Analyzes Put/Call ratios and unusual volume for a watchlist of key stocks
"""

import os
import json
import logging
import yfinance as yf
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class OptionsFlowAnalyzer:
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.output_file = os.path.join(data_dir, 'options_flow.json')
        self.watchlist = ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'SPY', 'QQQ', 'AMD', 'NFLX', 'DIS']
    
    def get_options_summary(self, ticker: str) -> Dict:
        """Fetch and analyze option chain data for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            exps = stock.options
            if not exps:
                return {'ticker': ticker, 'error': 'No options data found'}
            
            # Use the nearest expiration to check current flow sentiment
            opt = stock.option_chain(exps[0])
            calls, puts = opt.calls, opt.puts
            
            call_vol = calls['volume'].sum() if 'volume' in calls and not calls['volume'].isna().all() else 0
            put_vol = puts['volume'].sum() if 'volume' in puts and not puts['volume'].isna().all() else 0
            
            call_oi = calls['openInterest'].sum() if 'openInterest' in calls and not calls['openInterest'].isna().all() else 0
            put_oi = puts['openInterest'].sum() if 'openInterest' in puts and not puts['openInterest'].isna().all() else 0
            
            pc_ratio = put_vol / (call_vol + 1e-9) if call_vol > 0 else 1.0
            
            # Simple unusual activity detection (vol > 3x mean of the chain)
            unusual_calls = len(calls[calls['volume'] > calls['volume'].mean() * 3]) if len(calls) > 0 else 0
            unusual_puts = len(puts[puts['volume'] > puts['volume'].mean() * 3]) if len(puts) > 0 else 0
            
            sentiment = "Bullish" if pc_ratio < 0.7 else "Bearish" if pc_ratio > 1.2 else "Neutral"
            
            return {
                'ticker': ticker,
                'metrics': {
                    'pc_ratio': round(float(pc_ratio), 2),
                    'sentiment': sentiment,
                    'call_vol': int(call_vol), 
                    'put_vol': int(put_vol),
                    'call_oi': int(call_oi), 
                    'put_oi': int(put_oi)
                },
                'unusual': {'calls': unusual_calls, 'puts': unusual_puts},
                'last_price': round(stock.history(period='1d')['Close'].iloc[-1], 2)
            }
        except Exception as e:
            logger.debug(f"Error fetching options for {ticker}: {e}")
            return {'ticker': ticker, 'error': str(e)}

    def analyze_watchlist(self):
        logger.info(f"📊 Analyzing options flow for {len(self.watchlist)} tickers...")
        results = []
        for t in self.watchlist:
            res = self.get_options_summary(t)
            if 'error' not in res:
                results.append(res)
        
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'options_flow': results
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Saved options flow to {self.output_file}")

if __name__ == "__main__":
    OptionsFlowAnalyzer().analyze_watchlist()
