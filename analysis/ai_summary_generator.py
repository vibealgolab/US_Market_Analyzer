# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Stock Summary Generator
Generates concisely formatted investment summaries using Gemini 2.0
"""

import os
import json
import logging
import time
import requests
import pandas as pd
from tqdm import tqdm
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import sys
# Add parent directory to sys.path to allow imports from utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.gemini_utils import call_gemini
from datetime import datetime

def update_status(data_dir: str, task: str, progress: str, details: str = ""):
    """Helper to update pipeline_status.json for dashboard visibility"""
    try:
        path = os.path.join(data_dir, 'pipeline_status.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "current_task": task,
                "progress": progress,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
    except:
        pass

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsCollector:
    def get_news(self, ticker: str):
        news = []
        try:
            import xml.etree.ElementTree as ET
            import hashlib
            url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall('.//item')[:3]:
                    title = item.find('title').text
                    link = item.find('link').text
                    published = item.find('pubDate').text
                    # Generate stable ID to prevent UI index mismatch
                    news_id = hashlib.md5(title.encode()).hexdigest()[:12]
                    
                    news.append({
                        'id': f"news-{news_id}",
                        'title': title, 
                        'url': link,
                        'published': published,
                        'timestamp': datetime.now().isoformat()
                    })
        except Exception as e:
            logger.debug(f"News error for {ticker}: {e}")
        return news

class GeminiGenerator:
    def __init__(self):
        self.key = os.getenv('GOOGLE_API_KEY')
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
    def generate(self, ticker, row_data, news):
        news_txt = "\n".join([f"- {n['title']}" for n in news])
        score_info = (f"Composite Score: {row_data.get('composite_score')}/100, "
                     f"Grade: {row_data.get('grade')}, "
                     f"Technical: {row_data.get('tech_score')}, "
                     f"Fundamentals: {row_data.get('fund_score')}")
        
        prompt = f"""
        Stock Ticker: {ticker}
        Data: {score_info}
        Recent News:
        {news_txt}
        
        Task: Provide a concise (3-4 sentence) investment summary for this stock.
        Highlight technical strength/weakness, fundamental value, and recent news sentiment.
        Tone: Professional, objective, and analytical.
        Language: English only.
        """

        return call_gemini(prompt, temperature=0.4, max_tokens=400)

# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class AIStockAnalyzer:
    def __init__(self, data_dir=DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.output = os.path.join(data_dir, 'ai_summaries.json')
        self.gen = GeminiGenerator()
        self.news = NewsCollector()
        
    def run(self, top_n=20):
        # Load the latest smart money picks from JSON (Refined source)
        json_path = os.path.join(self.data_dir, 'smart_money_current.json')
        if not os.path.exists(json_path):
            logger.warning("JSON picks not found. Falling back to CSV.")
            csv_path = os.path.join(self.data_dir, 'smart_money_picks_v2.csv')
            if not os.path.exists(csv_path):
                logger.error("No source data found for summaries.")
                return
            df = pd.read_csv(csv_path)
        else:
            with open(json_path, 'r', encoding='utf-8') as f:
                df = pd.DataFrame(json.load(f).get('picks', []))

        if df.empty:
            logger.error("No stocks to analyze.")
            return

        # Load existing summaries
        results = {}
        if os.path.exists(self.output):
            try:
                with open(self.output, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            except: pass
            
        logger.info(f"🎨 Generating AI summaries for top {len(df)} priority stocks...")
        
        for i, (idx, row) in enumerate(tqdm(df.head(top_n).iterrows(), total=min(len(df), top_n)), 1):
            ticker = row['ticker']
            progress_msg = f"[{i}/{min(len(df), top_n)}]"
            
            # Skip check: If summary exists and is recent (last 24h), skip to save quota
            if ticker in results:
                last_update = datetime.fromisoformat(results[ticker].get('updated', '2000-01-01T00:00:00'))
                if (datetime.now() - last_update).total_seconds() < 86400:
                    if "Failed" not in results[ticker].get('summary', ''):
                        logger.info(f"⏭️ Skipping {ticker} (Recent summary exists)")
                        continue

            # 1. Fetch News
            update_status(self.data_dir, f"AI Summary: {ticker}", progress_msg, "Fetching Latest News")
            news = self.news.get_news(ticker)
            
            # 2. Generate Summary
            update_status(self.data_dir, f"AI Summary: {ticker}", progress_msg, "Synthesizing Technical Signals")
            summary_en = self.gen.generate(ticker, row.to_dict(), news)
            
            if "Error" in summary_en or "Failed" in summary_en:
                logger.warning(f"Summary failed for {ticker}")
                # We save the failure so we don't retry in the same loop, but might retry next run
                results[ticker] = {
                    'summary': "Failed to generate summary.",
                    'updated': datetime.now().isoformat()
                }
                continue

            # 3. Finalize Status
            update_status(self.data_dir, f"AI Summary: {ticker}", progress_msg, "Finalizing English Insights")

            results[ticker] = {
                'summary': summary_en, 
                'summary_en': summary_en,
                'news_count': len(news),
                'news_items': news,
                'updated': datetime.now().isoformat()
            }
            # Immediate save
            with open(self.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ AI Summaries updated: {len(results)} total.")

    def analyze_single_ticker(self, ticker: str) -> Dict:
        """On-demand analysis for a single ticker (triggered by UI button)"""
        try:
            # 1. Load data
            csv_path = os.path.join(self.data_dir, 'smart_money_picks_v2.csv')
            json_path = os.path.join(self.data_dir, 'smart_money_current.json')
            
            df = pd.DataFrame()
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
            elif os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    df = pd.DataFrame(json.load(f).get('picks', []))

            if df.empty or ticker not in df['ticker'].values:
                logger.warning(f"No price data found for {ticker} in current picks.")
                # We can still try to generate news, but prompt might be weak
                stock_data = {"ticker": ticker}
            else:
                stock_data = df[df['ticker'] == ticker].iloc[0].to_dict()

            # 2. Check cache first (redundant but safe)
            if os.path.exists(self.output):
                with open(self.output, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                    if ticker in results:
                        last_update = datetime.fromisoformat(results[ticker].get('updated', '2000-01-01T00:00:00'))
                        if (datetime.now() - last_update).total_seconds() < 86400:
                             if "Failed" not in results[ticker].get('summary', ''):
                                 return results[ticker]

            # 3. Perform Analysis
            logger.info(f"⚡ On-demand AI Analysis for {ticker}...")
            news = self.news.get_news(ticker)
            summary = self.gen.generate(ticker, stock_data, news)
            
            result = {
                'summary': summary,
                'summary_en': summary,
                'news_count': len(news),
                'news_items': news,
                'updated': datetime.now().isoformat()
            }
            
            # 4. Save back to main file
            if os.path.exists(self.output):
                with open(self.output, 'r', encoding='utf-8') as f:
                    all_results = json.load(f)
            else:
                all_results = {}
            
            all_results[ticker] = result
            with open(self.output, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
                
            return result
        except Exception as e:
            logger.error(f"Single ticker analysis failed for {ticker}: {e}")
            return {"summary": "Error: Failed to generate on-demand summary.", "error": str(e)}

if __name__ == "__main__":
    import sys
    # Only run full priority list if explicitly called or no args
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage: python ai_summary_generator.py [--run]")
        sys.exit(0)
    
    AIStockAnalyzer().run()
