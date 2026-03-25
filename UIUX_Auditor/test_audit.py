import requests

url = "http://127.0.0.1:5000/api/audit"
data = {"url": "https://www.google.com"}

try:
    print("Testing API...")
    res = requests.post(url, json=data)
    print("Status Code:", res.status_code)
    
    if res.status_code == 200:
        json_resp = res.json()
        print("Final Score:", json_resp.get("scores", {}).get("Final Score"))
        print("Grade:", json_resp.get("scores", {}).get("Grade"))
        print("Health:", json_resp.get("scores", {}).get("Health"))
        print("Accessibility:", json_resp.get("scores", {}).get("Accessibility Score"))
        print("Best Practices:", json_resp.get("scores", {}).get("Best Practices Score"))
        print("\nUI/UX Breakdown:", json_resp.get("ui_ux_breakdown"))
        print("\nBusiness Impact:", json_resp.get("business_impact"))
        
        issues = json_resp.get("key_issues", [])
        print("\nKey Issues:", "Found", len(issues))
        if len(issues) > 0:
            print("  First issue title:", issues[0].get("title"))
            
        recs = json_resp.get("recommendations", [])
        print("\nRecommendations:", "Found", len(recs))
        if len(recs) > 0:
            print("  First rec title:", recs[0].get("title"))
            
    else:
        print("Error content:", res.text)
except Exception as e:
    print("Request failed:", e)
