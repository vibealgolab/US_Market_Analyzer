# Gemini 2.0 Flash API Strategy & Constraints

Based on the policy analysis of Google Gemini 2.0 Flash API, we propose the following strategies to ensure the project's stability and cost-efficiency.

## 1. Google Gemini API Policy Summary (As of Feb 2026)

| Category | Free Tier | Pay-As-You-Go |
| :--- | :--- | :--- |
| **Rate Limit (RPM)** | Approx. 10 ~ 15 RPM | Max 150 ~ 300+ RPM |
| **Daily Limit (RPD)** | Approx. 250 ~ 1,000 RPD | Unlimited (Quota based) |
| **Data Privacy** | May be used for Google product improvement | **Not used for model training** |
| **Cost** | Free | $0.15 ~ $0.30 / 1M Input Tokens |

## 2. Current Project Response Strategy

### A. Rate Limit Handling
- **Centralized Management:** `gemini_utils.py` globally controls all requests.
- **Enforced Delay:** A minimum interval of **6 seconds** is set between requests to safely stay within the Free Tier limit (10 RPM).
- **Exponential Backoff:** If a 429 error occurs, the retry mechanism progressively increases the wait time.

### B. Cost & Quota Optimization
- **Local Caching:** Summaries for the same stock ticker are cached in `ai_summaries.json` for 24 hours to prevent unnecessary API calls.
- **Batch Processing Mode:** When running `update_all.py`, the `--quick` option can be used to skip API calls if AI summaries are not strictly required.

### C. Security & Data Privacy
- **De-identification:** Currently, only public data such as macro indicators and news headlines are transmitted, ensuring safety.
- **Pay-As-You-Go Recommendation:** If the project scales or deep analysis of personal portfolio data is introduced, switching to the Pay-As-You-Go tier is mandatory to opt-out of data training.

## 3. Future Roadmap

1. **Phase 1 (Current):** Secure stability within the Free Tier using optimized delay (6s) and automated retry logic.
2. **Phase 2:** Implement an API usage monitoring feature to alert before the daily quota (RPD) is exhausted.
3. **Phase 3:** Transition to a paid model as the user base grows, removing rate limits and enhancing privacy.

---

> [!IMPORTANT]
> The default delay in `gemini_utils.py` has been increased to 6 seconds to ensure stable operation without errors even on the Free Tier.
