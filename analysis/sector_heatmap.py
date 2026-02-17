# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sector Performance Heatmap Data Collector
Collects performance and weight data for S&P 500 sectors and key stocks
"""

import os
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class SectorHeatmapCollector:
    """Collect sector ETF performance data for heatmap visualization"""
    
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        # Sector ETFs with descriptive names
        self.sector_etfs = {
            'XLK': 'Technology',
            'XLF': 'Financials',
            'XLV': 'Healthcare',
            'XLE': 'Energy',
            'XLY': 'Consumer Discretionary',
            'XLP': 'Consumer Staples',
            'XLI': 'Industrials',
            'XLB': 'Materials',
            'XLU': 'Utilities',
            'XLRE': 'Real Estate',
            'XLC': 'Communication Services',
        }
        
        # Leading stocks in each sector for a representative tree-map
        self.sector_stocks = {
             'Technology': ['AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CRM', 'AMD', 'ADBE', 'TXN', 'QCOM'],
             'Financials': ['BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'C'],
             'Healthcare': ['LLY', 'UNH', 'JNJ', 'ABBV', 'MRK', 'TMO', 'ABT', 'PFE', 'AMGN', 'ISRG'],
             'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
             'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'SBUX', 'BKNG', 'TJX', 'MAR'],
             'Consumer Staples': ['PG', 'COST', 'KO', 'PEP', 'PM', 'WMT', 'EL', 'MO', 'TGT', 'CL'],
             'Industrials': ['CAT', 'GE', 'UNP', 'HON', 'RTX', 'LMT', 'BA', 'UPS', 'DE', 'MMM'],
             'Materials': ['LIN', 'APD', 'SHW', 'ECL', 'NEM', 'FCX', 'CTVA', 'DOW', 'NUE', 'ALB'],
             'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'SRE', 'EXC', 'PCG', 'XEL', 'PEG'],
             'Real Estate': ['PLD', 'AMT', 'EQIX', 'CCI', 'PSA', 'DLR', 'O', 'VICI', 'WY', 'SBAC'],
             'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'TMUS', 'VZ', 'T', 'CHTR', 'WBD', 'PARA']
        }
    
    def get_full_market_map(self, period: str = '5d') -> Dict:
        """Get full market map data (Sectors -> Stocks) for Treemap"""
        logger.info(f"📊 Fetching full market map data ({period})...")
        
        all_tickers = []
        ticker_to_sector = {}
        for sector, stocks in self.sector_stocks.items():
            all_tickers.extend(stocks)
            for stock in stocks:
                ticker_to_sector[stock] = sector
                
        try:
            # Batch download price history
            data = yf.download(all_tickers, period=period, progress=False)
            
            if data.empty:
                logger.error("No market data downloaded.")
                return {'error': 'No data'}
            
            market_map = {name: [] for name in self.sector_stocks.keys()}
            
            for ticker in all_tickers:
                try:
                    if ticker not in data['Close'].columns: continue
                    prices = data['Close'][ticker].dropna()
                    if len(prices) < 2: continue
                    
                    current = prices.iloc[-1]
                    prev = prices.iloc[-2]
                    change = ((current / prev) - 1) * 100
                    
                    # Estimate weight using Market Cap if available, otherwise price * vol
                    # For visualization, price * vol works as an "activity" proxy
                    vol = data['Volume'][ticker].iloc[-1] if 'Volume' in data.columns else 100000
                    weight = round(current * vol / 1e6, 2)  # Relative weight in millions
                    
                    sector = ticker_to_sector.get(ticker, 'Unknown')
                    if sector in market_map:
                        market_map[sector].append({
                            'x': ticker,
                            'y': weight,
                            'price': round(float(current), 2),
                            'change': round(float(change), 2),
                            'color': self._get_color(change)
                        })
                except Exception as e:
                    logger.debug(f"Ticker processing error ({ticker}): {e}")
                    pass
            
            series = []
            for sector_name, stocks in market_map.items():
                if stocks:
                    # Calculate weight-adjusted average change or simple average for now
                    avg_change = sum(s['change'] for s in stocks) / len(stocks)
                    # Sort stocks by weight within sector
                    stocks.sort(key=lambda x: x['y'], reverse=True)
                    series.append({
                        'name': sector_name, 
                        'avg_change': round(avg_change, 2),
                        'data': stocks
                    })
            
            # Sort sectors by total weight
            series.sort(key=lambda s: sum(i['y'] for i in s['data']), reverse=True)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'period': period,
                'series': series
            }
            
        except Exception as e:
            logger.error(f"Error gathering heatmap data: {e}")
            return {'error': str(e)}
            
    def _get_color(self, change: float) -> str:
        """Map percentage change to heatmap colors"""
        if change >= 3: return '#00C853'    # Strong Up
        elif change >= 1: return '#4CAF50' # Up
        elif change >= 0: return '#81C784' # Slight Up
        elif change >= -1: return '#EF9A9A'# Slight Down
        elif change >= -3: return '#F44336'# Down
        else: return '#B71C1C'             # Strong Down

    def save_data(self):
        data = self.get_full_market_map('5d')
        output_file = os.path.join(self.data_dir, 'sector_heatmap.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Saved sector heatmap to {output_file}")


if __name__ == "__main__":
    SectorHeatmapCollector().save_data()
