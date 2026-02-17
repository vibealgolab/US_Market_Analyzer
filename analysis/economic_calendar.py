# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity

import os
import json
import requests
import logging
import pandas as pd
import sys
from io import StringIO
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Add parent directory to sys.path to allow imports from utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.gemini_utils import call_gemini

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class EconomicCalendar:
    def __init__(self, data_dir=DEFAULT_DATA_DIR):
        self.output = os.path.join(data_dir, 'weekly_calendar.json')
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
    def get_events(self) -> List[Dict]:
        """Scrape Yahoo Finance Economic Calendar for US events (Next 7 days)"""
        logger.info("📅 Fetching economic calendar events for the week...")
        events = []
        try:
            now_ts = pd.Timestamp.now()
            start_date = now_ts.strftime('%Y-%m-%d')
            end_date = (now_ts + pd.Timedelta(days=7)).strftime('%Y-%m-%d')
            url = f"https://finance.yahoo.com/calendar/economic?from={start_date}&to={end_date}"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                dfs = pd.read_html(StringIO(resp.text))
                if dfs:
                    df = dfs[0]
                    # Forward fill the 'Day' or relevant date column if it exists
                    # Yahoo often only lists the date once per group
                    date_col = 'Day' if 'Day' in df.columns else ('Date' if 'Date' in df.columns else None)
                    if date_col:
                        df[date_col] = df[date_col].ffill()
                    
                    if 'Country' in df.columns:
                        # Some scrapers return 'USD' or 'US' for United States
                        us_events = df[df['Country'].astype(str).str.contains('US', na=False)].head(15)
                        for _, row in us_events.iterrows():
                            event_name = str(row.get('Event', 'N/A'))
                            events.append({
                                'date': str(row.get(date_col, '-')),
                                'time': str(row.get('Time (EDT)', row.get('Event Time', 'N/A'))),
                                'event': event_name,
                                'impact': 'High' if any(x in event_name for x in ['CPI', 'Fed', 'FOMC', 'Employment', 'Retail']) else 'Medium',
                                'actual': str(row.get('Actual', '-')),
                                'estimate': str(row.get('Market Expectation', '-')),
                                'description': f"Prior: {row.get('Prior to This', '-')}"
                            })
                    
            if not events:
                logger.warning("No US events found in scraper. Using proactive week markers.")
                events.append({
                    'date': 'Coming Week',
                    'event': 'Monitor Macro Indicators & Earnings Volatility',
                    'impact': 'Medium',
                    'description': 'Market monitoring US baseline data.'
                })
        except Exception as e:
            logger.error(f"Error scraping Yahoo calendar: {e}")
            events.append({
                'date': 'N/A',
                'event': 'Calendar Service Sync Error',
                'impact': 'Low',
                'description': f'Error details: {str(e)[:50]}'
            })
        
        return events
    
    def enrich_with_ai(self, events: List[Dict]) -> List[Dict]:
        """Use Gemini to explain the impact of high-impact events"""
        logger.info("🤖 Enriching high-impact events with AI insights...")
        for ev in events:
            if ev['impact'] == 'High':
                prompt = f"""
                Explain the potential US stock market impact of this economic event in 2 concise sentences:
                Event: {ev['event']}
                Context: {ev['description']}
                Use professional financial language. English only.
                """
                ai_txt = call_gemini(prompt, temperature=0.3, max_tokens=200)
                if ai_txt and not ai_txt.startswith("Error"):
                    ev['ai_insight'] = ai_txt.strip()
                else:
                    ev['ai_insight'] = None
                    
        return events

    def run(self):
        events = self.get_events()
        enriched_events = self.enrich_with_ai(events)
        
        output_data = {
            'updated': datetime.now().isoformat(),
            'week_start': datetime.now().strftime('%Y-%m-%d'),
            'events': enriched_events
        }
        
        with open(self.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Saved economic calendar with {len(enriched_events)} events.")

if __name__ == "__main__":
    EconomicCalendar().run()
