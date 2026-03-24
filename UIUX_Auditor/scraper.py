import time
from playwright.sync_api import sync_playwright

def scrape_website(url: str):
    """
    Scrapes the given URL and returns HTML, load time, and mobile viewport info.
    """
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    start_time = time.time()
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        
        # Desktop context
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            }
        )
        page = context.new_page()
        
        try:
            # We use domcontentloaded for a fast measure, but wait for networkidle if we need all resources
            # We'll use load state to measure full performance roughly
            page.goto(url, wait_until='load', timeout=30000)
            load_time = time.time() - start_time
            
            # Fetch HTML
            html = page.content()
            
            # Check viewport tag presence via Playwright evaluate (or we can do it via BS4 later)
            has_viewport = page.evaluate('() => !!document.querySelector("meta[name=viewport]")')
            
            # Capture Screenshot as Base64
            import base64
            screenshot_bytes = page.screenshot(type='jpeg', quality=60)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

            # Check Mobile context
            mobile_context = browser.new_context(
                viewport={'width': 375, 'height': 667},
                is_mobile=True,
                has_touch=True,
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15'
            )
            mobile_page = mobile_context.new_page()
            try:
                mobile_page.goto(url, wait_until='domcontentloaded', timeout=15000)
                # Check if page width exceeds mobile viewport width (sideways scroll issue)
                scroll_width = mobile_page.evaluate("""() => {
                    return Math.max(
                        document.body.scrollWidth, document.documentElement.scrollWidth,
                        document.body.offsetWidth, document.documentElement.offsetWidth,
                        document.body.clientWidth, document.documentElement.clientWidth
                    );
                }""")
                mobile_issue_width = scroll_width > 375
            except Exception as e:
                mobile_issue_width = False
                
            browser.close()
            
            return {
                "success": True,
                "html": html,
                "screenshot": screenshot_b64,
                "load_time_seconds": round(load_time, 2),
                "has_viewport": has_viewport,
                "mobile_horizontal_scroll": mobile_issue_width
            }
        except Exception as e:
            browser.close()
            return {"success": False, "error": str(e)}
