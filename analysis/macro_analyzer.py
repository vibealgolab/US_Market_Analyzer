# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Macro Market Analyzer
- Collects macro indicators (VIX, Yields, Commodities, etc.)
- Uses Gemini 2.0 to generate investment strategy
"""

import os
import json
import requests
import yfinance as yf
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
import sys
# Add parent directory to sys.path to allow imports from utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.gemini_utils import call_gemini

# Load .env
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MacroDataCollector:
    """Collect macro market data from various sources"""
    
    def __init__(self):
        self.macro_tickers = {
            'VIX': '^VIX', 'DXY': 'DX-Y.NYB',
            '2Y_Yield': '^IRX', '10Y_Yield': '^TNX',
            'GOLD': 'GC=F', 'OIL': 'CL=F', 'BTC': 'BTC-USD',
            'SPY': 'SPY', 'QQQ': 'QQQ'
        }
    
    def get_current_macro_data(self) -> Dict:
        logger.info("📊 Fetching macro data...")
        macro_data = {}
        try:
            tickers = list(self.macro_tickers.values())
            # Use small period for latest data
            data = yf.download(tickers, period='5d', progress=False)
            
            for name, ticker in self.macro_tickers.items():
                try:
                    if ticker not in data['Close'].columns: continue
                    hist = data['Close'][ticker].dropna()
                    if len(hist) < 2: continue
                    
                    val = hist.iloc[-1]
                    prev = hist.iloc[-2]
                    change = ((val / prev) - 1) * 100
                    
                    # Store data
                    macro_data[name] = {
                        'value': round(float(val), 2),
                        'change_1d': round(float(change), 2)
                    }
                except Exception as e:
                    logger.debug(f"Error for {name}: {e}")
            
            # Yield Spread calculation
            if '2Y_Yield' in macro_data and '10Y_Yield' in macro_data:
                spread = macro_data['10Y_Yield']['value'] - macro_data['2Y_Yield']['value']
                macro_data['YieldSpread'] = {'value': round(float(spread), 2), 'change_1d': 0}
            
        except Exception as e:
            logger.error(f"Error fetching macro indicators: {e}")
        return macro_data

    def get_macro_news(self) -> List[Dict]:
        """Fetch macro news from Google RSS with stable IDs"""
        news = []
        try:
            import xml.etree.ElementTree as ET
            import hashlib
            url = "https://news.google.com/rss/search?q=Federal+Reserve+Economy&hl=en-US&gl=US&ceid=US:en"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall('.//item')[:5]:
                    title = item.find('title').text
                    link = item.find('link').text
                    # Generate stable ID based on title to avoid index-mismatch in frontend
                    news_id = hashlib.md5(title.encode()).hexdigest()[:12]
                    
                    news.append({
                        'id': f"macro-{news_id}",
                        'title': title, 
                        'source': 'Google News',
                        'url': link,
                        'timestamp': datetime.now().isoformat()
                    })
        except Exception as e:
            logger.debug(f"News fetch error: {e}")
        return news


class MacroAIAnalyzer:
    """Gemini 2.0 Analysis for Macro Market"""
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        # Using gemini-2.0-flash for speed and English quality
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def analyze(self, data: Dict, news: List[Dict]) -> str:
        prompt = self._build_prompt(data, news)
        return call_gemini(prompt, temperature=0.5, max_tokens=1000)
    
    def _build_prompt(self, data: Dict, news: List[Dict]) -> str:
        metrics = "\n".join([f"- {k}: {v['value']} ({v['change_1d']}% 1d)" for k,v in data.items()])
        headlines = "\n".join([n['title'] for n in news])
        
        return f"""
        Role: Senior Quantitative Macro Strategist and Institutional Portfolio Manager.
        Task: Provide a high-precision, institutional-grade market intelligence report for the US Stock Market.
        
        Indicators:
        {metrics}
        
        Recent Headlines:
        {headlines}
        
        Request: 
        1. ### Strategic Sentiment: Synthesize macro metrics and news into a high-level market thesis. Identify if we are in a 'Risk-On' or 'Risk-Off' regime based on VIX and Yield levels.
        2. ### Quantitative Impact: Detail the specific impact of the Yield Curve (2Y vs 10Y) on equity valuations and identify the current 'Terminal Rate' expectations.
        3. ### Sector Rotation & Opportunities: Pinpoint exactly which sectors (Tech, defensive, commodities) are seeing momentum based on current DXY/Yield interactions.
        4. ### Actionable Alpha: Provide 2-3 specific tactical moves for a professional portfolio, including specific technical levels (e.g., 'Watch SPY 5000 support').
        
        Requirement: Use professional, analytical language (e.g., "sectoral rotation," "duration risk," "liquidity expansion"). Respond in English markdown headers (###) only.
        """


# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class MacroSystem:
    def __init__(self, data_dir=DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.collector = MacroDataCollector()
        self.ai = MacroAIAnalyzer()
    
    def run(self):
        # 0. Skip Check: Shorter cycle (1 Hour) for high-frequency insights
        path = os.path.join(self.data_dir, 'macro_analysis.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    last_update = datetime.fromisoformat(old_data.get('timestamp', '2000-01-01T00:00:00'))
                    ai_res = old_data.get('ai_analysis', '')
                    
                    if (datetime.now() - last_update).total_seconds() < 3600: # 1 Hour (Reduced from 12h)
                         if "Error" not in ai_res and "failed" not in ai_res.lower():
                             logger.info("⏭️ Skipping Macro AI Analysis (Recent data exists)")
                             return
            except: pass

        # Centralized status update for dashboard visibility
        def update_status(task, progress, details=""):
            try:
                status_path = os.path.join(self.data_dir, 'pipeline_status.json')
                with open(status_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "current_task": task, 
                        "progress": progress, 
                        "details": details,
                        "timestamp": datetime.now().isoformat()
                    }, f, indent=2)
            except: pass

        update_status("Macro Analysis", "0%", "Fetching Data")
        data = self.collector.get_current_macro_data()
        news = self.collector.get_macro_news()
        
        # AI Analysis in English
        update_status("Macro Analysis", "50%", "AI Synthesis")
        analysis = self.ai.analyze(data, news)
        
        # Graceful Fallback: If new analysis fails, try to keep old one
        if "Error" in analysis or "failed" in analysis.lower():
            try:
                path = os.path.join(self.data_dir, 'macro_analysis.json')
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        old_data = json.load(f)
                        old_analysis = old_data.get('ai_analysis', '')
                        if old_analysis and "Error" not in old_analysis and "failed" not in old_analysis.lower():
                            logger.warning("⚠️ New AI Analysis failed. Falling back to previous successful analysis.")
                            # Keep old analysis but append a subtle stale marker if not already present
                            marker = "\n\n*(Note: This is a preserved report from a previous cycle due to temporary API limits)*"
                            if marker not in old_analysis:
                                analysis = old_analysis + marker
                            else:
                                analysis = old_analysis
            except: pass

        output = {
            'timestamp': datetime.now().isoformat(),
            'next_update': (datetime.now() + timedelta(hours=1)).isoformat(),
            'macro_indicators': data,
            'ai_analysis': analysis,
            'news': news
        }
        
        # Save results (unified English version)
        update_status("Macro Analysis", "90%", "Saving Data")
        with open(os.path.join(self.data_dir, 'macro_analysis.json'), 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        # Also save as _en for consistency with expected dashboard paths
        with open(os.path.join(self.data_dir, 'macro_analysis_en.json'), 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        update_status("Market Analysis", "100%", "Completed - Insight Synthesized")
        logger.info("✅ Saved macro analysis to macro_analysis.json")


if __name__ == "__main__":
    MacroSystem().run()
