import os
from analyzer import fetch_lighthouse, get_stable_lighthouse_scores

# Test 1: Fallback behavior without key
print("--- Test 1: Fetching Lighthouse without API Key (Expect 429 after many uses, but handles fallback gracefully) ---")
# Ensure key is not set for test
if "GOOGLE_PAGESPEED_API_KEY" in os.environ:
    del os.environ["GOOGLE_PAGESPEED_API_KEY"]

scores = get_stable_lighthouse_scores("https://example.com", runs=1)
print("Scores returned: {}".format(scores))
if scores and "performance" in scores:
    print("Test 1 Passed: Received scores (either real or fallback).")
else:
    print("Test 1 Failed: Did not receive expected score structure.")

print("\n--- Test 2: Fallback handling when fetch fails ---")
# Mock fetch to always return None (simulating 429)
original_fetch = fetch_lighthouse

def mock_failing_fetch(url):
    return None

import analyzer
analyzer.fetch_lighthouse = mock_failing_fetch

# Clear cache to force a new run
analyzer.LIGHTHOUSE_CACHE = {}

scores_fallback = get_stable_lighthouse_scores("https://example.com", runs=1)
print("Fallback Scores returned: {}".format(scores_fallback))
if scores_fallback == {"performance": 65, "seo": 65, "accessibility": 65, "best_practices": 65}:
    print("Test 2 Passed: Correctly returned baseline fallback values.")
else:
    print("Test 2 Failed: Did not return expected baseline fallback values.")

# Restore original
analyzer.fetch_lighthouse = original_fetch
