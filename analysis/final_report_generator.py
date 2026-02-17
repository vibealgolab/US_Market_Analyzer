# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Report Generator
Consolidates quantitative scores and AI summaries into a ranked list for the dashboard.
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default data directory relative to this script
DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

class FinalReportGenerator:
    def __init__(self, data_dir=DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self.output_report = os.path.join(data_dir, 'final_top10_report.json')
        self.output_current = os.path.join(data_dir, 'smart_money_current.json')
        
    def run(self, top_n=10):
        logger.info("📊 Generating Final Investment Report...")
        
        # 1. Load Quant Data
        stats_path = os.path.join(self.data_dir, 'smart_money_picks_v2.csv')
        if not os.path.exists(stats_path):
            logger.error("Quant results CSV not found.")
            return
        df = pd.read_csv(stats_path)
        
        # 2. Load AI Summary Data
        ai_path = os.path.join(self.data_dir, 'ai_summaries.json')
        ai_data = {}
        if os.path.exists(ai_path):
            with open(ai_path, 'r', encoding='utf-8') as f:
                ai_data = json.load(f)
            
        results = []
        for idx, row in df.iterrows():
            ticker = row['ticker']
            # We only include stocks that have an AI summary
            if ticker not in ai_data:
                continue
            
            summary = ai_data[ticker].get('summary', '')
            
            # Simple sentiment logic for a bonus score refinement
            ai_bonus = 0
            rec = "Hold"
            summary_lower = summary.lower()
            
            if "strong buy" in summary_lower or "excellent" in summary_lower:
                ai_bonus = 15
                rec = "Strong Buy"
            elif "buy" in summary_lower or "positive" in summary_lower:
                ai_bonus = 5
                rec = "Buy"
            elif "sell" in summary_lower or "risky" in summary_lower:
                ai_bonus = -10
                rec = "Sell"
                
            # Composite calculation: 70% Quant, 30% AI refinement
            quant_score = row['composite_score']
            final_score = round(quant_score * 0.7 + ai_bonus, 1)
            
            results.append({
                'ticker': ticker,
                'name': row.get('name', ticker),
                'final_score': final_score,
                'quant_score': round(float(quant_score), 1),
                'ai_recommendation': rec,
                'current_price': round(float(row.get('current_price', 0)), 2),
                'ai_summary': summary,
                'grade': row.get('grade', 'N/A'),
                'updated': ai_data[ticker].get('updated', datetime.now().isoformat())
            })
            
        # 3. Sort and Rank
        results.sort(key=lambda x: x['final_score'], reverse=True)
        top_picks = results[:top_n]
        for i, p in enumerate(top_picks, 1):
            p['rank'] = i
            p['id'] = f"{p['ticker']}_{i}"
        
        # 4. Save structured report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'top_picks': top_picks,
            'summary': f"Synthesized analysis of top {len(top_picks)} market opportunities."
        }
        
        with open(self.output_report, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        # Also save as smart_money_current for the dashboard main view
        with open(self.output_current, 'w', encoding='utf-8') as f:
            json.dump({'picks': top_picks}, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Generated Final Report for {len(top_picks)} stocks")

if __name__ == "__main__":
    FinalReportGenerator().run()
