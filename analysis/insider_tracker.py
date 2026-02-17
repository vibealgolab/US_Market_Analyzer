# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Insider Trading Tracker
Monitors insider transactions for key stocks using yfinance
"""

import os
import json
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class InsiderTracker:
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.output_file = os.path.join(data_dir, 'insider_moves.json')
        
    def get_insider_activity(self, ticker: str) -> List[Dict]:
        """Fetch recent insider transactions"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.insider_transactions
            if df is None or df.empty:
                return []
            
            # Filter for buys within the last 6 months (approx 180 days)
            cutoff = pd.Timestamp.now() - pd.Timedelta(days=180)
            df = df.sort_index(ascending=False)
            
            recent_buys = []
            for date, row in df.iterrows():
                # Handling TZ-aware or naive datetimes
                if date.tzinfo:
                    date_naive = date.tz_localize(None)
                else:
                    date_naive = date
                    
                if date_naive < cutoff:
                    continue
                    
                text = str(row.get('Text', '')).lower()
                # We specifically look for purchases/buys (Positive Smart Money)
                if 'purchase' not in text and 'buy' not in text:
                    continue
                
                recent_buys.append({
                    'date': str(date.date()),
                    'insider': row.get('Insider', 'N/A'),
                    'position': row.get('Position', 'N/A'),
                    'value': float(row.get('Value', 0) or 0),
                    'shares': int(row.get('Shares', 0) or 0)
                })
            return recent_buys
        except Exception as e:
            logger.debug(f"Error fetching insider data for {ticker}: {e}")
            return []

    def analyze_tickers(self, tickers: List[str]):
        logger.info(f"🕵️ Tracking insider moves for {len(tickers)} stocks...")
        results = {}
        for t in tickers:
            activities = self.get_insider_activity(t)
            if activities:
                # Score based on transaction count and significant value (> $100k)
                score = len(activities) * 5
                large_buys = sum(10 for a in activities if a['value'] > 100000)
                score += large_buys
                
                results[t] = {
                    'insider_confidence_score': score,
                    'transaction_count': len(activities),
                    'recent_trades': activities[:5] # Keep top 5 latest
                }
        
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'details': results,
            'watchlist_count': len(tickers),
            'active_insider_count': len(results)
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Saved insider moves to {self.output_file}")

if __name__ == "__main__":
    # Example tracking for top tech/market leaders
    tracker = InsiderTracker()
    tracker.analyze_tickers(['AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'META', 'GOOGL', 'AMD', 'NFLX', 'COST'])
