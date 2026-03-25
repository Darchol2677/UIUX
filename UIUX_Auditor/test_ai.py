import os
from ai_engine import analyze_with_ai

try:
    print("Testing ai_engine directly...")
    res = analyze_with_ai("<html><body><p>Test</p></body></html>", {"allIssues": ["test"]})
    print("Result key_issues:")
    print(res.get("key_issues"))
    print("Result recommendations:")
    print(res.get("recommendations"))
except Exception as e:
    print("Direct error:", e)
