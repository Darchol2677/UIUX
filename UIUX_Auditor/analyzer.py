from bs4 import BeautifulSoup
import re
import urllib.request
import json
import time

def _infer_archetype(soup):
    text = (soup.title.string if soup.title else "").lower()
    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc:
        text += " " + meta_desc.get("content", "").lower()

    keywords = {
        "Medical": ["health", "doctor", "clinic", "hospital", "patient", "medical"],
        "E-commerce": ["shop", "buy", "store", "product", "cart", "price"],
        "Tech/SaaS": ["software", "ai", "cloud", "saas", "platform", "app", "tech"],
        "Creative/Portfolio": ["portfolio", "agency", "design", "creative", "photography"],
        "Educational": ["learn", "course", "study", "university", "school", "education"],
        "Corporate": ["solutions", "services", "company", "business", "consulting"]
    }

    for arch, keys in keywords.items():
        if any(k in text for k in keys):
            return arch
    return "Generic Modern"

def _infer_tone(archetype):
    tones = {
        "Medical": "Trustworthy, Clean, Compassionate",
        "Tech/SaaS": "Futuristic, Efficient, High-Energy",
        "Educational": "Intellectual, Clear, Encouraging",
        "Creative/Portfolio": "Bold, Artistic, Unique",
        "Corporate": "Professional, Reliable, Solid",
        "E-commerce": "Urgent, Persuasive, Friendly"
    }
    return tones.get(archetype, "Professional, Modern")

def fetch_lighthouse(url):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&category=performance&category=accessibility&category=best-practices&category=seo&strategy=mobile"
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode())
            categories = data.get("lighthouseResult", {}).get("categories", {})
            return {
                "performance": (categories.get("performance", {}).get("score") or 0) * 100,
                "seo": (categories.get("seo", {}).get("score") or 0) * 100,
                "accessibility": (categories.get("accessibility", {}).get("score") or 0) * 100,
                "best_practices": (categories.get("best-practices", {}).get("score") or 0) * 100
            }
    except Exception as e:
        print(f"Lighthouse API Error: {e}")
        return None

LIGHTHOUSE_CACHE = {}

def get_stable_lighthouse_scores(url, runs=2):
    global LIGHTHOUSE_CACHE
    if url in LIGHTHOUSE_CACHE:
        return LIGHTHOUSE_CACHE[url]
        
    totals = {"performance": 0, "seo": 0, "accessibility": 0, "best_practices": 0}
    successes = 0
    for _ in range(runs):
        res = fetch_lighthouse(url)
        if res:
            for k in totals: totals[k] += res[k]
            successes += 1
        if successes < runs:
            time.sleep(1.0)
            
    if successes == 0:
        return {"performance": 65, "seo": 65, "accessibility": 65, "best_practices": 65} # Baseline fallback if API fails
        
    final_res = {k: int(v / successes) for k, v in totals.items()}
    LIGHTHOUSE_CACHE[url] = final_res
    return final_res

def analyze_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    issues = []
    
    archetype = _infer_archetype(soup)
    brand_tone = _infer_tone(archetype)
    
    h1_tags = soup.find_all('h1')
    images = soup.find_all('img')
    navs = soup.find_all('nav')
    scripts = soup.find_all('script')
    links = soup.find_all('a')
    
    missing_nav = len(navs) == 0
    missing_h1 = len(h1_tags) == 0
    
    img_without_alt = [img for img in images if not img.get('alt', '').strip()]
    missing_alts = len(img_without_alt)
    if missing_alts > 0:
        issues.append(f"Found {missing_alts} images missing 'alt' text.")
    if missing_h1:
        issues.append("No <h1> tag found. Poor heading structure.")
        
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    has_viewport = bool(viewport_meta)
        
    cta_keywords = ['sign up', 'register', 'contact', 'buy', 'subscribe', 'get started', 'book', 'demo']
    found_ctas = sum(1 for el in soup.find_all(['button', 'a']) if any(k in el.text.lower() for k in cta_keywords))
    missing_cta = found_ctas == 0
    
    if len(h1_tags) > 1:
        issues.append(f"Found {len(h1_tags)} <h1> tags (should only be one).")
        
    return {
        "issues": issues,
        "missing_nav": missing_nav,
        "missing_h1": missing_h1,
        "missing_alts": missing_alts,
        "missing_cta": missing_cta,
        "has_viewport": has_viewport,
        "metrics": {
            "image_count": len(images),
            "script_count": len(scripts),
            "link_count": len(links),
            "heading_count": len(soup.find_all(re.compile('^h[1-6]$')))
        },
        "archetype": archetype,
        "brand_tone": brand_tone
    }

def calculate_scores(scraper_data, html_analysis, url):
    lh = get_stable_lighthouse_scores(url, runs=2)
    
    ui_ux_base = (lh['accessibility'] + lh['best_practices']) / 2.0
    seo_base = lh['seo']
    perf_base = lh['performance']
    mobile_base = lh['performance'] # Baseline mobile
    
    issues = html_analysis['issues'].copy()
    
    if not html_analysis.get('has_viewport', True):
        mobile_base -= 40
        issues.append("Missing viewport meta tag for mobile responsiveness.")

    ui_deduct = 0
    seo_deduct = 0
    
    if html_analysis.get('missing_nav'):
        ui_deduct += 25  # Heavier penalty for missing Nav
        issues.append("Missing navigation bar (<nav> HTML5 element).")
        
    if html_analysis.get('missing_h1'):
        seo_deduct += 20
        ui_deduct += 10
        
    if html_analysis.get('missing_alts') > 0:
        seo_deduct += min(30, html_analysis['missing_alts'] * 8)
        
    if html_analysis.get('missing_cta'):
        ui_deduct += 30 # Heavier penalty for missing CTA
        issues.append("No Call-To-Action (CTA) buttons found.")
        
    final_ui_ux = max(0, min(100, ui_ux_base - ui_deduct))
    final_seo   = max(0, min(100, seo_base - seo_deduct))
    final_perf  = max(0, min(100, perf_base))
    final_mob   = max(0, min(100, mobile_base))
    
    # Standardized Hackathon Weighting:
    # UI/UX: 35%, Performance: 30%, SEO: 20%, Mobile: 15%
    final_score = (0.35 * final_ui_ux) + (0.30 * final_perf) + (0.20 * final_seo) + (0.15 * final_mob)
    
    return {
        "UI/UX Score": round(final_ui_ux),
        "SEO Score": round(final_seo),
        "Performance Score": round(final_perf),
        "Mobile Score": round(final_mob),
        "Final Score": round(final_score),
        "allIssues": issues,
        "metrics": html_analysis.get("metrics", {}),
        "archetype": html_analysis.get("archetype", "Generic Modern"),
        "brand_tone": html_analysis.get("brand_tone", "Professional, Modern")
    }

def clean_html_for_prompt(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'svg', 'img', 'noscript', 'iframe', 'video']):
        tag.decompose()
        
    text = soup.get_text(separator=' ', strip=True)
    return text[:4000]
