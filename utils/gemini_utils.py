# [vibealgolab.com] 2026-02-15 | VibeCoding with Gemini & Antigravity

import os
import time
import json
import logging
import requests
import random
import hashlib
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables early for module-level constants
load_dotenv()

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
QUOTA_FILE = os.path.join(DATA_DIR, 'quota_states.json') # Changed filename for 2.0
CACHE_FILE = os.path.join(DATA_DIR, 'gemini_cache.json')

class QuotaShield:
    """Advanced Multi-Key Quota Manager (Quota Shield 2.0)"""
    def __init__(self):
        self.keys = self._load_keys()
        self._ensure_dir()
        self.rpm_limit = 10
        self.rpd_limit = 1000
        self.states = self._load_states()

    def _load_keys(self) -> List[str]:
        raw_keys = os.getenv('GOOGLE_API_KEY', '')
        if not raw_keys:
            return []
        keys = [k.strip() for k in raw_keys.split(',') if k.strip()]
        logger.info(f"🔑 Load-balancing initialized with {len(keys)} API keys.")
        return keys

    def _ensure_dir(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def _load_states(self) -> Dict[str, Any]:
        if os.path.exists(QUOTA_FILE):
            try:
                with open(QUOTA_FILE, 'r') as f:
                    return json.load(f)
            except: pass
        
        # Initialize states for each key index
        return {str(i): {
            "requests_this_minute": 0,
            "last_request_time": 0,
            "total_requests_today": 0,
            "last_reset_date": time.strftime("%Y-%m-%d")
        } for i in range(len(self.keys))}

    def _save_states(self):
        try:
            with open(QUOTA_FILE, 'w') as f:
                json.dump(self.states, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save shield states: {e}")

    def get_available_key(self) -> Optional[tuple[str, int]]:
        """Returns (api_key, key_index) if an available key is found"""
        self.states = self._load_states()
        now = time.time()
        today = time.strftime("%Y-%m-%d")

        # Try keys in random order for better distribution across processes
        indices = list(range(len(self.keys)))
        random.shuffle(indices)

        for i in indices:
            state = self.states.get(str(i))
            if not state: continue

            # Reset logic
            if state.get("last_reset_date") != today:
                state.update({"total_requests_today": 0, "last_reset_date": today})
            
            if now - state.get("last_request_time", 0) > 60:
                state["requests_this_minute"] = 0

            # Check limits
            if state["total_requests_today"] >= self.rpd_limit:
                continue
            
            # Minute spread check (6s between same key for 10RPM limit)
            if now - state.get("last_request_time", 0) < 6.0:
                continue

            if state["requests_this_minute"] >= self.rpm_limit:
                continue

            return self.keys[i], i

        return None

    def record_attempt(self, index: int, status_code: int = 0):
        self.states = self._load_states()
        if str(index) in self.states:
            now = time.time()
            self.states[str(index)]["last_request_time"] = now
            # If it's a 429, block this key for a short bit
            if status_code == 429:
                self.states[str(index)]["requests_this_minute"] = self.rpm_limit 
            self._save_states()

    def record_success(self, index: int):
        self.states = self._load_states()
        if str(index) in self.states:
            st = self.states[str(index)]
            st["requests_this_minute"] += 1
            st["total_requests_today"] += 1
            st["last_request_time"] = time.time()
            self._save_states()

shield = QuotaShield()

def get_cached_response(prompt: str) -> Optional[str]:
    """Permanent-style cache for Gemini responses (24h)"""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            entry = cache.get(prompt_hash)
            if entry:
                # Cache valid for 48 hours for general analysis
                if time.time() - entry.get('timestamp', 0) < 172800:
                    return entry.get('response')
    except: pass
    return None

def save_to_cache(prompt: str, response: str):
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except: pass
    
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    cache[prompt_hash] = {'timestamp': time.time(), 'response': response}
    try:
        # Limit cache size to prevent massive JSON files
        if len(cache) > 2000:
            # Pop oldest 100 entries
            sorted_keys = sorted(cache.keys(), key=lambda k: cache[k].get('timestamp', 0))
            for k in sorted_keys[:100]: cache.pop(k)
            
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save gemini cache: {e}")

def call_gemini(prompt: str, temperature: float = 0.5, max_tokens: int = 1000) -> str:
    # 1. Permanent Cache Check
    cached = get_cached_response(prompt)
    if cached:
        logger.info(f"🚀 [v2.0] Serving from Cache: {prompt[:50]}...")
        return cached

    # 2. Key Selection & Quota Check
    for retry in range(20): # Increased retry cycle for heavy rotation
        keyinfo = shield.get_available_key()
        if keyinfo:
            api_key, key_idx = keyinfo
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            
            try:
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
                }
                resp = requests.post(url, json=payload, timeout=30)
                
                if resp.status_code == 200:
                    shield.record_success(key_idx)
                    text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    save_to_cache(prompt, text)
                    return text
                
                elif resp.status_code == 429:
                    shield.record_attempt(key_idx, status_code=429)
                    
                    # Extract retry info if available
                    wait_time = 15
                    try:
                        error_details = resp.json().get('error', {}).get('details', [])
                        for detail in error_details:
                            if 'retryDelay' in detail:
                                # Convert 1.23s string to float
                                wait_time = float(detail['retryDelay'].replace('s', '')) + 2
                    except: pass
                    
                    logger.warning(f"⚠️ Key {key_idx} toggled 429. Google recommends {wait_time}s wait. Rotating...")
                    time.sleep(wait_time / 2) # Partial wait before trying next key
                    continue 

                else:
                    shield.record_attempt(key_idx, status_code=resp.status_code)
                    logger.error(f"❌ API Error {resp.status_code}: {resp.text[:100]}")
                    return f"Error: {resp.status_code}"
            except Exception as e:
                logger.error(f"Key {key_idx} exception: {e}")
                time.sleep(5)
        else:
            # All keys busy internally
            wait = 10 + random.uniform(2, 8)
            logger.info(f"⏳ Internal shield cooling down. Sleeping {wait:.1f}s...")
            time.sleep(wait)
            
    return "Error: Quota Shield 2.0 failed after exhaustive rotation."
