import time
import requests
import base64
from bs4 import BeautifulSoup

# User-agent to mimic a real browser and avoid bot-blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
}

def scrape_website(url: str):
    """
    Scrapes the given URL using requests+BeautifulSoup.
    Returns HTML, load time, mobile viewport info, and a placeholder screenshot.
    Works on all hosting providers (no browser binaries needed).
    """
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    start_time = time.time()

    try:
        response = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        load_time = time.time() - start_time

        response.raise_for_status()

        html = response.text

        # Parse with BeautifulSoup for quick checks
        soup = BeautifulSoup(html, 'html.parser')

        # Check for viewport meta tag (mobile responsiveness)
        viewport_tag = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'viewport'})
        has_viewport = viewport_tag is not None

        # Generate a screenshot via a free screenshot API (no browser needed)
        screenshot_b64 = _get_screenshot_b64(url)

        # Heuristic: check if the page has a wide fixed-width layout (mobile issue)
        # Look for fixed widths > 600px in inline styles or meta width
        mobile_issue_width = _check_mobile_width(soup)

        return {
            "success": True,
            "html": html,
            "screenshot": screenshot_b64,
            "load_time_seconds": round(load_time, 2),
            "has_viewport": has_viewport,
            "mobile_horizontal_scroll": mobile_issue_width
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "The website took too long to respond (timeout after 20s)."}
    except requests.exceptions.SSLError:
        return {"success": False, "error": "SSL certificate error on the target website."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to the website. Please check the URL."}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": "Website returned an error: {}".format(str(e))}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_screenshot_b64(url: str) -> str:
    """
    Fetches a screenshot using the free screenshotmachine API.
    Falls back to an empty string if the service is unavailable.
    """
    try:
        # Use screenshotmachine's free endpoint (no key required for basic use)
        screenshot_url = "https://mini.s-shot.ru/1280x800/JPEG/60/?{}".format(url)
        resp = requests.get(screenshot_url, timeout=15)
        if resp.status_code == 200 and resp.headers.get('content-type', '').startswith('image'):
            return base64.b64encode(resp.content).decode('utf-8')
    except Exception:
        pass

    # Fallback: try another free screenshot service
    try:
        screenshot_url2 = "https://api.screenshotmachine.com/?url={}&dimension=1280x800&format=jpg&cacheLimit=0".format(url)
        resp2 = requests.get(screenshot_url2, timeout=12)
        if resp2.status_code == 200 and resp2.headers.get('content-type', '').startswith('image'):
            return base64.b64encode(resp2.content).decode('utf-8')
    except Exception:
        pass

    return ""  # Return empty string if screenshot unavailable


def _check_mobile_width(soup: BeautifulSoup) -> bool:
    """
    Heuristic check: Does the page appear to have fixed-width layout
    wider than mobile (suggests horizontal scroll on phones)?
    """
    # Look for inline styles with fixed widths > 600px
    for tag in soup.find_all(style=True):
        style = tag.get('style', '')
        if 'width' in style:
            # Check for large fixed pixel widths
            import re
            widths = re.findall(r'width\s*:\s*(\d+)px', style)
            for w in widths:
                if int(w) > 600:
                    return True

    # No obvious mobile layout issues found
    return False
