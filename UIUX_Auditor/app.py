import os
# Skip load_dotenv if it's missing or causes prefix errors
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from flask import Flask, request, jsonify, render_template, session
from scraper import scrape_website
from analyzer import analyze_html, calculate_scores, clean_html_for_prompt
from ai_engine import analyze_with_ai, chat_with_expert
from redesign_engine import extract_site_content, generate_redesign_html, generate_bonus_redesigns

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

@app.route('/')
def index():
    return render_template('index.html')

import json
import os

CACHE_FILE = 'audit_cache.json'
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

# No typing imports needed to avoid 3.5- errors

REPORT_CACHE = load_cache()

@app.route('/api/audit', methods=['POST'])
def audit():
    global REPORT_CACHE
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    if url in REPORT_CACHE:
        print("Returning cached audit for: {}".format(url))
        return jsonify(REPORT_CACHE[url])

    print("Starting fresh audit for: {}".format(url))

    try:
        # 1. Scrape the site
        scrape_result = scrape_website(url)
        if not scrape_result['success']:
            return jsonify({"error": "Failed to scrape the website", "details": scrape_result.get('error')}), 500

        html_content = scrape_result['html']

        # 2. Heuristic & Lighthouse Analysis
        analysis_raw = analyze_html(html_content)
        scores = calculate_scores(scrape_result, analysis_raw, url)

        # 3. Always generate a content-aware redesign from real scraped HTML
        site_content = extract_site_content(html_content)
        local_redesign_html = generate_redesign_html(site_content)

        # 4. Clean text for AI prompt
        text_for_ai = clean_html_for_prompt(html_content)

        # 5. AI Analysis (Used for scoring, issues, and content refinement)
        ai_result = analyze_with_ai(text_for_ai, scores)
        
        # Merge AI-suggested content into site_content if available
        if ai_result.get("headlines_suggested"):
            site_content['headline'] = ai_result['headlines_suggested']
        if ai_result.get("subheadlines_suggested"):
            site_content['subheadline'] = ai_result['subheadlines_suggested']

        # Regenerate main redesign with AI-enhanced content
        final_redesign = generate_redesign_html(site_content)

        report = {
            "url": url,
            "scores": {
                "UI/UX Score": scores["UI/UX Score"],
                "SEO Score": scores["SEO Score"],
                "Performance Score": scores["Performance Score"],
                "Mobile Score": scores["Mobile Score"],
                "Final Score": scores["Final Score"]
            },
            "issues": scores["allIssues"] + ai_result.get("issues", []),
            "recommendations": ai_result.get("recommendations", []),
            "executive_summary": ai_result.get("executive_summary", ""),
            "generated_code": final_redesign,
            "bonus_redesigns": generate_bonus_redesigns(site_content, count=3),
            "metrics": scores["metrics"],
            "screenshot": scrape_result.get("screenshot"),
            "html_source": html_content
        }

        # Cache the resulting report identically based on URL into persistent storage
        REPORT_CACHE[url] = report
        save_cache(REPORT_CACHE)

        return jsonify(report)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Global in-memory list for chat history (as requested)
chat_history = []

@app.route('/api/chat', methods=['POST'])
@app.route('/chat', methods=['POST'])
def chat():
    global chat_history
    try:
        data = request.json
        message = data.get('message')
        audit_context = data.get('audit_context')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Pass history to AI engine
        reply = chat_with_expert(message, audit_context, chat_history)

        # Append new interaction to history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": reply})
        
        # Manage context window (keep last 10 messages)
        chat_history = chat_history[-10:]
        
        return jsonify({"reply": reply})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"reply": "Internal Backend Error: " + str(e)}), 200

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "URL required", 400
    
    # URL Normalization for better matching
    def normalize(u):
        return u.rstrip('/')
    
    target_url = normalize(url)
    
    # Try to find target_url in cache (or normalized versions)
    html = ""
    for cache_url in REPORT_CACHE:
        if normalize(cache_url) == target_url:
            html = REPORT_CACHE[cache_url].get('html_source', '')
            break
            
    if html:
        # Inject <base> tag to fix relative assets
        base_tag = '<base href="{}">'.format(url)
        if '<head>' in html:
            html = html.replace('<head>', '<head>' + base_tag)
        else:
            html = base_tag + html
        return html

    # If not in cache (unexpected for this app flow), just return a message or scrape
    return "Please run an audit first to view the preview.", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
