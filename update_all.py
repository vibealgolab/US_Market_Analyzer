# vibealgolab.com
# Date: 2026-02-14
# Developed with VibeCoding using Gemini & Antigravity
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Pipeline Update Script
Coordinates the full execution of the US Market Analyzer pipeline.
"""

import os
import sys
import subprocess
import time
import argparse
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Execution sequence and timeouts (seconds)
PIPELINE_SCRIPTS = [
    # Phase 1: Data Collection
    ("analysis/create_us_daily_prices.py", "Gathering Price Data", 600),
    ("analysis/analyze_volume.py", "Volume/Supply-Demand Analysis", 300),
    ("analysis/analyze_13f.py", "Institutional Tracking", 300),
    ("analysis/analyze_etf_flows.py", "ETF Flow Analysis", 300),
    
    # Phase 2: Core Analysis
    ("analysis/smart_money_screener_v2.py", "Ranking & Screening", 600),
    ("analysis/sector_heatmap.py", "Generating Heatmap Data", 300),
    ("analysis/options_flow.py", "Options Flow Analysis", 300),
    ("analysis/insider_tracker.py", "Insider Activity Tracking", 300),
    ("analysis/portfolio_risk.py", "Portfolio Risk Calculation", 120),
    
    # Phase 3: AI Insights Layer
    ("analysis/macro_analyzer.py", "Macro Economy AI Analysis", 300),
    # ("analysis/ai_summary_generator.py", "Stock-level AI Summaries", 900), # Now On-Demand
    ("analysis/final_report_generator.py", "Synthesizing Final Report", 120),
    ("analysis/economic_calendar.py", "Fetching Economic Calendar", 120)
]

STATUS_FILE = os.path.join("data", "pipeline_status.json")

def update_status(desc, progress):
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump({"current_task": desc, "progress": progress, "timestamp": time.time()}, f)
    except: pass

def run_script(name, description, timeout, current_idx, total):
    progress = f"[{current_idx}/{total}]"
    logger.info(f"🚀 {progress} Running: {description} ({name})...")
    update_status(description, progress)
    sys.stdout.flush() # CRITICAL: Ensure logs appear in real-time
    
    start_time = time.time()
    try:
        if not os.path.exists(name):
            logger.error(f"❌ Script not found: {name}")
            return False
            
        # Use unbuffered output for child processes
        result = subprocess.run([sys.executable, "-u", name], timeout=timeout, check=True)
        elapsed = time.time() - start_time
        logger.info(f"✅ Completed {name} in {elapsed:.1f}s")
        return True
    except subprocess.TimeoutExpired:
        logger.error(f"⌛ Timeout: {name} exceeded {timeout}s")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error in {name}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error running {name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="US Market Analyzer Pipeline Orchestrator")
    parser.add_argument('--quick', action='store_true', help='Skip heavy AI summary generation')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], help='Run only a specific phase')
    args = parser.parse_args()
    
    total_start = time.time()
    logger.info("🔥 Starting Full Pipeline Update...")
    
    success_count = 0
    fail_count = 0
    
    # Determine which scripts to run
    phase_map = {
        1: PIPELINE_SCRIPTS[0:4],
        2: PIPELINE_SCRIPTS[4:9],
        3: PIPELINE_SCRIPTS[9:]
    }
    
    to_run = phase_map.get(args.phase, PIPELINE_SCRIPTS)
    total_scripts = len(to_run)
    
    for i, (name, desc, timeout) in enumerate(to_run, 1):
        if args.quick and "summary" in desc.lower():
            logger.info(f"⏭️ Skipping {name} (--quick mode)")
            continue
            
        if run_script(name, desc, timeout, i, total_scripts):
            success_count += 1
        else:
            fail_count += 1
            logger.warning(f"⚠️ Pipeline continued after {name} failure")
        sys.stdout.flush()
            
    total_elapsed = (time.time() - total_start) / 60
    logger.info(f"\n✨ Pipeline Update Finished")
    update_status("Completed", "100%")
    sys.stdout.flush()
    logger.info(f"📈 Results: {success_count} Succeeded, {fail_count} Failed")
    logger.info(f"⏱️ Total Time: {total_elapsed:.1f} minutes")

if __name__ == "__main__":
    main()
