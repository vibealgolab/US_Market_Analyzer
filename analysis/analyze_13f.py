# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US 13F Institutional Holdings Analysis
Fetches and analyzes institutional holdings from yfinance (based on 13F filings)
"""

import os
import pandas as pd
import numpy as np
import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
from tqdm import tqdm

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class SEC13FAnalyzer:
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.output_file = os.path.join(data_dir, 'us_13f_holdings.csv')
        
    def analyze_institutional_changes(self, tickers: List[str]) -> pd.DataFrame:
        """
        Analyze institutional ownership and recent changes
        """
        results = []
        
        for ticker in tqdm(tickers, desc="Fetching institutional data"):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Basic ownership info
                held_inst = info.get('heldPercentInstitutions', 0) or 0
                held_insider = info.get('heldPercentInsiders', 0) or 0
                
                # Float and shares
                float_shares = info.get('floatShares', 0) or 0
                short_pct = info.get('shortPercentOfFloat', 0) or 0
                
                # Insider transactions
                try:
                    insider_txns = stock.insider_transactions
                    if insider_txns is not None and not insider_txns.empty:
                        recent = insider_txns.head(10)
                        buys = len(recent[recent['Transaction'].str.contains('Buy', case=False, na=False)])
                        sells = len(recent[recent['Transaction'].str.contains('Sale|Sell', case=False, na=False)])
                        sentiment = 'Buying' if buys > sells else ('Selling' if sells > buys else 'Neutral')
                    else:
                        sentiment = 'Unknown'
                        buys, sells = 0, 0
                except:
                    sentiment, buys, sells = 'Unknown', 0, 0
                
                # Institutional holders count
                try:
                    inst_holders = stock.institutional_holders
                    num_inst = len(inst_holders) if inst_holders is not None else 0
                except:
                    num_inst = 0
                
                # Score calculation (0-100)
                score = 50
                if held_inst > 0.8: score += 15
                elif held_inst > 0.6: score += 10
                elif held_inst < 0.3: score -= 10
                
                if buys > sells: score += 15
                elif sells > buys: score -= 10
                
                if short_pct < 0.03: score += 5
                elif short_pct > 0.1: score -= 10
                elif short_pct > 0.2: score -= 20
                
                score = max(0, min(100, score))
                
                if score >= 70: stage = "Strong Institutional Support"
                elif score >= 55: stage = "Institutional Support"
                elif score >= 45: stage = "Neutral"
                elif score >= 30: stage = "Institutional Concern"
                else: stage = "Strong Institutional Selling"
                
                results.append({
                    'ticker': ticker,
                    'institutional_pct': round(held_inst * 100, 2),
                    'insider_pct': round(held_insider * 100, 2),
                    'short_pct': round(short_pct * 100, 2),
                    'float_shares_m': round(float_shares / 1e6, 2) if float_shares else 0,
                    'num_inst_holders': num_inst,
                    'insider_buys': buys,
                    'insider_sells': sells,
                    'insider_sentiment': sentiment,
                    'institutional_score': score,
                    'institutional_stage': stage
                })
                
                time.sleep(0.1) # Rate limiting
                
            except Exception as e:
                logger.debug(f"Error analyzing {ticker}: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def run(self) -> pd.DataFrame:
        logger.info("🚀 Starting 13F Institutional Analysis...")
        
        stocks_file = os.path.join(self.data_dir, 'us_stocks_list.csv')
        if os.path.exists(stocks_file):
            stocks_df = pd.read_csv(stocks_file)
            tickers = stocks_df['ticker'].tolist()
        else:
            logger.warning("Stock list not found. Using default top tickers.")
            tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA'] # Fallback
            
        logger.info(f"📊 Analyzing {len(tickers)} stocks")
        results_df = self.analyze_institutional_changes(tickers)
        
        if not results_df.empty:
            results_df.to_csv(self.output_file, index=False)
            logger.info(f"✅ Analysis complete! Saved to {self.output_file}")
            
        return results_df


def main():
    import argparse
    parser = argparse.ArgumentParser(description='13F Institutional Analysis')
    parser.add_argument('--dir', default=DEFAULT_DATA_DIR, help='Data directory')
    parser.add_argument('--tickers', nargs='+', help='Specific tickers to analyze')
    args = parser.parse_args()
    
    analyzer = SEC13FAnalyzer(data_dir=args.dir)
    if args.tickers:
        results = analyzer.analyze_institutional_changes(args.tickers)
    else:
        results = analyzer.run()
        
    if not results.empty:
        print("\n🏦 Top 10 Institutional Support:")
        top_10 = results.nlargest(10, 'institutional_score')
        for _, row in top_10.iterrows():
            print(f"   {row['ticker']}: Score {row['institutional_score']} | Inst: {row['institutional_pct']}%")


if __name__ == "__main__":
    main()
