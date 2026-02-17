# [vibealgolab.com] 2026-02-17 | VibeCoding with Gemini & Antigravity
import os
import json
import logging
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from typing import List, Dict
import sys
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class PortfolioRiskAnalyzer:
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.output_file = os.path.join(data_dir, 'portfolio_risk.json')
        self.picks_file = os.path.join(data_dir, 'smart_money_current.json')

    def get_latest_tickers(self) -> List[str]:
        """Fetch current tickers from smart_money_current.json"""
        if not os.path.exists(self.picks_file):
            logger.warning("No smart_money_current.json found. Using defaults.")
            return ['AAPL', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA']
            
        try:
            with open(self.picks_file, 'r', encoding='utf-8') as f:
                picks_data = json.load(f)
                tickers = [p['ticker'] for p in picks_data.get('picks', [])]
                return tickers if tickers else ['SPY', 'QQQ']
        except Exception as e:
            logger.error(f"Error loading picks: {e}")
            return ['SPY', 'QQQ']

    def update_status(self, task: str, progress: str, details: str = ""):
        """Update central pipeline status"""
        try:
            status_path = os.path.join(self.data_dir, 'pipeline_status.json')
            with open(status_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "current_task": task, 
                    "progress": progress, 
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.debug(f"Status update failed: {e}")

    def analyze_portfolio(self, tickers: List[str] = None):
        """Calculate volatility and correlation for the provided tickers or latest picks"""
        if tickers is None:
            tickers = self.get_latest_tickers()
            
        logger.info(f"📉 Analyzing portfolio risk for {len(tickers)} tickers: {tickers}...")
        if not tickers:
            return
            
        self.update_status("Risk Analysis", "10%", f"Fetching data for {len(tickers)} assets")
        
        try:
            # Download historical closing prices (6 months for stable correlation)
            data = yf.download(tickers, period='6mo', progress=False)['Close']
            if data.empty:
                logger.error("No historical data for risk analysis")
                self.update_status("Risk Analysis", "0%", "Error: No data found")
                return
                
            self.update_status("Risk Analysis", "50%", "Computing correlations")
            
            # Handle single ticker edge case
            if isinstance(data, pd.Series):
                data = data.to_frame()

            returns = data.pct_change().dropna()
            
            # Correlation Analysis
            corr = returns.corr()
            high_corr_threshold = 0.75 
            high_corr_pairs = []
            cols = corr.columns
            
            for i in range(len(cols)):
                for j in range(i+1, len(cols)):
                    val = float(corr.iloc[i, j])
                    if val > high_corr_threshold:
                        high_corr_pairs.append({
                            'tickers': [cols[i], cols[j]],
                            'correlation': round(val, 2)
                        })
            
            self.update_status("Risk Analysis", "80%", "Calculating volatility tokens")
            
            # Portfolio Volatility (Equally Weighted)
            cov_matrix = returns.cov() * 252 # Annualize
            weights = np.array([1.0/len(tickers)] * len(tickers))
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            # Individual volatilities
            vol_series = returns.std() * np.sqrt(252)
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_volatility_pct': round(float(portfolio_volatility * 100), 2),
                'high_correlations': high_corr_pairs,
                'diversification_status': "Diversified" if len(high_corr_pairs) < (len(tickers) / 2) else "Concentrated",
                'ticker_volatilities': vol_series.round(4).to_dict(),
                'correlation_matrix': corr.round(2).to_dict()
            }
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
            self.update_status("Market Analysis", "100%", "Risk Sync Completed")
            logger.info(f"✅ Risk Analysis Complete: Volatility {portfolio_volatility*100:.1f}%")
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {e}")
            self.update_status("Market Analysis", "100%", f"Risk Error: {str(e)[:30]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Portfolio Risk Analyzer')
    parser.add_argument('--tickers', nargs='+', help='List of tickers to analyze')
    args = parser.parse_args()
    
    analyzer = PortfolioRiskAnalyzer()
    analyzer.analyze_portfolio(tickers=args.tickers)
