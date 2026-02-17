# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US Stock ETF Fund Flows Analysis
Tracks major ETFs, calculates flow scores, and generates AI insights using Gemini
"""

import os
import json
import logging
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from tqdm import tqdm
from dotenv import load_dotenv
import sys
# Add parent directory to sys.path to allow imports from utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.gemini_utils import call_gemini

# Load .env for API keys
load_dotenv()

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class ETFFlowAnalyzer:
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.output_csv = os.path.join(data_dir, 'us_etf_flows.csv')
        self.output_ai = os.path.join(data_dir, 'etf_flow_analysis.json')
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
        # Major ETFs to track
        self.etf_list = {
            # Broad Market
            'SPY': {'name': 'S&P 500', 'category': 'Broad Market'},
            'QQQ': {'name': 'Nasdaq 100', 'category': 'Broad Market'},
            'IWM': {'name': 'Russell 2000', 'category': 'Broad Market'},
            'DIA': {'name': 'Dow Jones', 'category': 'Broad Market'},
            
            # S&P Sectors
            'XLK': {'name': 'Technology', 'category': 'Sector'},
            'XLF': {'name': 'Financial', 'category': 'Sector'},
            'XLE': {'name': 'Energy', 'category': 'Sector'},
            'XLV': {'name': 'Health Care', 'category': 'Sector'},
            'XLP': {'name': 'Consumer Staples', 'category': 'Sector'},
            'XLY': {'name': 'Consumer Discretionary', 'category': 'Sector'},
            'XLI': {'name': 'Industrial', 'category': 'Sector'},
            'XLB': {'name': 'Materials', 'category': 'Sector'},
            'XLU': {'name': 'Utilities', 'category': 'Sector'},
            'XLRE': {'name': 'Real Estate', 'category': 'Sector'},
            'XLC': {'name': 'Communication', 'category': 'Sector'},
            
            # Commodities & Others
            'GLD': {'name': 'Gold', 'category': 'Commodity'},
            'USO': {'name': 'Crude Oil', 'category': 'Commodity'},
            'SLV': {'name': 'Silver', 'category': 'Commodity'},
            'TLT': {'name': '20Y Treasury', 'category': 'Bonds'},
            'HYG': {'name': 'High Yield Bond', 'category': 'Bonds'},
            'UUP': {'name': 'USD Index', 'category': 'Currency'},
            'ARKK': {'name': 'Innovation', 'category': 'Growth'},
            'BITO': {'name': 'Bitcoin Strategy', 'category': 'Crypto'}
        }

    def calculate_flow_score(self, ticker: str, df: pd.DataFrame) -> Dict:
        """
        Calculate a proxy for fund flows using:
        - OBV (Supply/Demand)
        - Volume Ratio (Relative intensity)
        - Price Momentum (Sentiment)
        """
        if len(df) < 20:
            return {'ticker': ticker, 'flow_score': 50, 'stage': 'Neutral'}
            
        prices = df['Close'].values
        volumes = df['Volume'].values
        
        # OBV Change (5-day)
        obv = 0
        obvs = [0]
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]: obv += volumes[i]
            elif prices[i] < prices[i-1]: obv -= volumes[i]
            obvs.append(obv)
        
        obv_5d_change = (obvs[-1] - obvs[-5]) / (sum(volumes[-5:]) + 1e-6)
        
        # Volume Ratio (5d vs 20d)
        vol_5d = np.mean(volumes[-5:])
        vol_20d = np.mean(volumes[-20:])
        vol_ratio = vol_5d / vol_20d if vol_20d > 0 else 1
        
        # Price change
        price_change_5d = (prices[-1] / prices[-5] - 1) * 100
        
        # Score calculation
        score = 50
        score += obv_5d_change * 50  # contribution from accumulation
        score += (vol_ratio - 1) * 10 # contribution from high volume
        score += price_change_5d * 2 # contribution from momentum
        
        score = max(0, min(100, score))
        
        if score >= 65: stage = "High Inflow"
        elif score >= 55: stage = "Inflow"
        elif score >= 45: stage = "Neutral"
        elif score >= 35: stage = "Outflow"
        else: stage = "High Outflow"
        
        return {
            'ticker': ticker,
            'price': round(prices[-1], 2),
            'change_5d': round(price_change_5d, 2),
            'vol_ratio': round(vol_ratio, 2),
            'flow_score': round(score, 1),
            'flow_stage': stage
        }

    def fetch_etf_data(self) -> pd.DataFrame:
        logger.info("📊 Fetching ETF data...")
        results = []
        
        for ticker, meta in tqdm(self.etf_list.items(), desc="Processing ETFs"):
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='1mo')
                if hist.empty: continue
                
                flow = self.calculate_flow_score(ticker, hist)
                flow['name'] = meta['name']
                flow['category'] = meta['category']
                results.append(flow)
                
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                
        return pd.DataFrame(results)

    def generate_ai_analysis(self, df: pd.DataFrame) -> str:
        logger.info("🤖 Generating AI Flow Analysis...")
        
        # Prepare context for Gemini
        top_inflows = df.nlargest(5, 'flow_score')[['ticker', 'name', 'flow_score']].to_dict(orient='records')
        top_outflows = df.nsmallest(5, 'flow_score')[['ticker', 'name', 'flow_score']].to_dict(orient='records')
        
        context = f"""
        Analyze current US market fund flows based on ETF data:
        Top Inflows: {top_inflows}
        Top Outflows: {top_outflows}
        
        Provide a concise analysis (3-4 sentences) explaining:
        1. Current market sentiment (Risk-on vs Risk-off)
        2. Leading and laggard sectors/assets
        3. Strategic outlook for the next week
        Respond in English.
        """
        
        return call_gemini(context, temperature=0.5, max_tokens=500)

    def run(self):
        logger.info("🚀 Starting ETF Fund Flows analysis...")
        
        # 1. Fetch and calculate flows
        df = self.fetch_etf_data()
        if df.empty:
            logger.error("No ETF data collected.")
            return
            
        # 2. Save CSV
        df.to_csv(self.output_csv, index=False)
        logger.info(f"✅ Saved flows to {self.output_csv}")
        
        # 3. Check for existing analysis to skip (Quota Optimization)
        if os.path.exists(self.output_ai):
            try:
                with open(self.output_ai, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    if 'ai_analysis' in old_data and "Error" not in old_data['ai_analysis']:
                        last_upd = datetime.fromisoformat(old_data.get('timestamp', '2000-01-01'))
                        if (datetime.now() - last_upd).total_seconds() < 43200: # 12h
                            logger.info("⏭️ Skipping ETF AI Analysis (Recent result exists)")
                            ai_text = old_data['ai_analysis']
                        else:
                            ai_text = self.generate_ai_analysis(df)
                    else:
                        ai_text = self.generate_ai_analysis(df)
            except:
                ai_text = self.generate_ai_analysis(df)
        else:
            ai_text = self.generate_ai_analysis(df)
        
        # 4. Save JSON for web dashboard
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'ai_analysis': ai_text,
            'summary': {
                'total_etfs': len(df),
                'market_sentiment': df[df['category'] == 'Broad Market']['flow_score'].mean()
            }
        }
        
        with open(self.output_ai, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Saved AI analysis to {self.output_ai}")
        print(f"\nAI Analysis Summary:\n{ai_text}")


if __name__ == "__main__":
    analyzer = ETFFlowAnalyzer()
    analyzer.run()
