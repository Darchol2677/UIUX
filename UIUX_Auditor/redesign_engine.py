from bs4 import BeautifulSoup
import re

def extract_site_content(html: str):
    """Extract meaningful content and styles from the website's HTML."""
    soup = BeautifulSoup(html, 'html.parser')

    # 1. Color Inference - Look for common colors in style tags or inline styles
    primary_color = "#8b5cf6"  # Default Purple
    accent_color = "#ec4899"   # Default Pink
    
    style_content = " ".join([s.get_text() for s in soup.find_all('style')])
    # Simple regex to find hex colors in CSS
    hex_colors = re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', style_content)
    if hex_colors:
        # Pick a couple of non-dark colors (if possible)
        bright_colors = [c for c in hex_colors if not c.lower() in ['#000', '#000000', '#fff', '#ffffff']]
        if len(bright_colors) >= 1: primary_color = bright_colors[0]
        if len(bright_colors) >= 2: accent_color = bright_colors[1]

    # Clean the soup for text extraction
    for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg', 'head']):
        tag.decompose()

    # 2. Site title
    title = ""
    title_tag = BeautifulSoup(html, 'html.parser').find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)[:80]

    # 3. Logo / brand name: more aggressive search
    brand = ""
    # Check for text like 'BrandName' in common header areas
    for sel in ['[class*="logo"]', '[class*="brand"]', '[id*="logo"]', '[id*="brand"]', 'header a', 'nav a']:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t and 2 < len(t) < 40:
                brand = t
                break
    if not brand and title:
        # Common title patterns like "Brand - Title" or "Brand | Title"
        brand = re.split(r'[-|·–—]', title)[0].strip()

    # 4. Navigation links - grab from any horizontal-ish link list
    nav_links = []
    # Try <nav> then <ul> then any container with multiple links
    nav_found = soup.find('nav') or soup.find('ul', class_=re.compile(r'menu|nav|link|header'))
    if nav_found:
        links = nav_found.find_all('a', href=True)
        for a in links:
            text = a.get_text(strip=True)
            if text and 2 < len(text) < 30 and text not in nav_links:
                nav_links.append(text)
            if len(nav_links) >= 6: break

    # 5. Headline: prefer h1, then h2
    headline = ""
    for tag in ['h1', 'h2']:
        el = soup.find(tag)
        if el:
            t = el.get_text(strip=True)
            if t and 10 < len(t) < 150:
                headline = t
                break

    # 6. Subheadline
    subheadline = ""
    meta_desc_tag = BeautifulSoup(html, 'html.parser').find('meta', attrs={'name': 'description'})
    if meta_desc_tag:
        subheadline = meta_desc_tag.get('content', '').strip()[:220]

    if not subheadline:
        for tag in ['h2', 'h3', 'p']:
            els = soup.find_all(tag)
            for el in els:
                t = el.get_text(strip=True)
                if t and 30 < len(t) < 250 and t != headline:
                    subheadline = t[:220]
                    break
            if subheadline: break

    # 7. CTA Buttons
    cta_buttons = []
    cta_kw = ['get', 'start', 'sign', 'join', 'buy', 'demo', 'download', 'contact', 'try', 'learn', 'explore']
    for btn in soup.find_all(['button', 'a']):
        text = btn.get_text(strip=True)
        if text and any(kw in text.lower() for kw in cta_kw) and len(text) < 30:
            if text not in cta_buttons:
                cta_buttons.append(text)
        if len(cta_buttons) >= 3: break

    # 8. Features & Content Sections
    features = []
    # Identify site context: SaaS, E-com, or Content
    all_text = soup.get_text().lower()
    is_ecom = any(w in all_text for w in ['price', '$', 'product', 'cart', 'shop', 'order'])
    
    # Extract sections
    for h_tag in ['h2', 'h3']:
        for h in soup.find_all(h_tag):
            t_text = h.get_text(strip=True)
            if t_text and 5 < len(t_text) < 100 and t_text != headline:
                desc = ""
                p = h.find_next(['p', 'div'])
                if p:
                    desc = p.get_text(strip=True)[:150]
                features.append({"title": t_text, "desc": desc})
            if len(features) >= 9: break
        if len(features) >= 6: break

    # 9. Archetype Detection (Improved for 5-step framework)
    archetype = "Landing page"
    if is_ecom: 
        archetype = "E-commerce"
    elif any(w in all_text for w in ["pricing", "saas", "software", "platform", "subscription", "cloud"]): 
        archetype = "Business / SaaS"
    elif any(w in all_text for w in ["blog", "article", "news", "reading", "published"]): 
        archetype = "Blog"
    elif any(w in all_text for w in ["portfolio", "creative", "design", "art", "projects", "work"]): 
        archetype = "Portfolio"
    elif any(w in all_text for w in ["help", "support", "document", "kb"]): 
        archetype = "Business / SaaS"
    
    res_data: Dict[str, Any] = {
        "brand": brand or "UI Cloud",
        "title": title,
        "headline": headline or title or "Next-Gen Digital Experience",
        "subheadline": subheadline or "Empowering your workflow with intelligent, beautiful solutions designed for the modern web.",
        "nav_links": list(nav_links or ["Features", "About", "Contact", "Sign In"]),
        "cta_primary": str(cta_buttons[0] if cta_buttons else "Get Started →"),
        "cta_secondary": str(cta_buttons[1] if len(cta_buttons) > 1 else "Learn More"),
        "features": list(features)[:6],
        "is_ecom": bool(is_ecom),
        "primary_color": str(primary_color),
        "accent_color": str(accent_color),
        "archetype": str(archetype)
    }
    return res_data


import random

def get_design_system(style: str, p_color: str, a_color: str):
    systems = {
        "Minimal": {
            "bg": "#ffffff", "surface": "#f8fafc", "text": "#0f172a", "muted": "#64748b",
            "primary": p_color, "accent": a_color, "border": "1px solid #e2e8f0", "radius": "8px",
            "glass": "transparent", "shadow": "0 1px 3px rgba(0,0,0,0.1)", "font": "'Inter', sans-serif"
        },
        "Glassmorphism": {
            "bg": "#0f172a", "surface": "rgba(255,255,255,0.03)", "text": "#f8fafc", "muted": "#94a3b8",
            "primary": p_color, "accent": a_color, "border": "1px solid rgba(255,255,255,0.1)", "radius": "24px",
            "glass": "blur(12px)", "shadow": "0 8px 32px rgba(0,0,0,0.3)", "font": "'Outfit', sans-serif"
        },
        "Dark modern": {
            "bg": "#030712", "surface": "#0f172a", "text": "#f8fafc", "muted": "#6b7280",
            "primary": p_color, "accent": a_color, "border": "1px solid rgba(255,255,255,0.08)", "radius": "16px",
            "glass": "transparent", "shadow": "0 10px 50px rgba(0,0,0,0.5)", "font": "'Plus Jakarta Sans', sans-serif"
        },
        "Vibrant gradient": {
            "bg": "#ffffff", "surface": "#ffffff", "text": "#1e293b", "muted": "#475569",
            "primary": f"linear-gradient(135deg, {p_color}, {a_color})", "accent": a_color,
            "border": "1px solid #f1f5f9", "radius": "30px", "glass": "transparent",
            "shadow": "0 20px 40px rgba(0,0,0,0.05)", "font": "'Outfit', sans-serif"
        },
        "Neumorphism": {
            "bg": "#e0e5ec", "surface": "#e0e5ec", "text": "#44475a", "muted": "#71717a",
            "primary": p_color, "accent": a_color, "border": "none", "radius": "20px",
            "glass": "transparent", "shadow": "9px 9px 16px rgb(163,177,198,0.6), -9px -9px 16px rgba(255,255,255, 0.5)",
            "font": "'Inter', sans-serif"
        }
    }
    return systems.get(style, systems["Dark modern"])

from typing import Optional, Dict, Any

def generate_redesign_html(content: dict, layout_override: Optional[str] = None, style_override: Optional[str] = None) -> str:
    brand = content['brand']
    headline = content['headline']
    subheadline = content['subheadline']
    nav_links = content['nav_links']
    features = content['features']
    p_color = content['primary_color']
    a_color = content['accent_color']
    arch = content.get('archetype', 'Landing page')

    # Step 2 & 4: Select Layout and Style
    layouts = ["Modern SaaS layout", "Creative portfolio layout", "E-commerce layout", "Minimal blog layout", "Split screen layout", "Sidebar navigation layout"]
    styles = ["Minimal", "Glassmorphism", "Dark modern", "Vibrant gradient", "Neumorphism"]
    
    # Intelligently pick layout if possible, otherwise random
    if layout_override:
        layout = layout_override
    elif arch == "E-commerce": layout = "E-commerce layout"
    elif arch == "Blog": layout = "Minimal blog layout"
    elif arch == "Portfolio": layout = "Creative portfolio layout"
    elif arch == "Business / SaaS": layout = random.choice(["Modern SaaS layout", "Sidebar navigation layout"])
    else: layout = random.choice(layouts)
    
    style = style_override if style_override else random.choice(styles)
    ds = get_design_system(style, p_color, a_color)

    nav_html = "".join(f'<li><a href="#">{l}</a></li>' for l in nav_links[:5])
    features_html = ""
    icons = ["✨", "🚀", "💎", "⚡", "🔒", "🎨"]
    for i, f in enumerate(features[:6]):
        features_html += f"""
        <div class="card">
            <div class="icon">{icons[i % len(icons)]}</div>
            <h3>{f['title']}</h3>
            <p>{f['desc'] or 'Precision-engineered experience.'}</p>
        </div>"""

    # Base CSS with Variables
    base_css = f"""
    :root {{
        --bg: {ds['bg']};
        --surface: {ds['surface']};
        --text: {ds['text']};
        --muted: {ds['muted']};
        --primary: {ds['primary']};
        --accent: {ds['accent']};
        --border: {ds['border']};
        --radius: {ds['radius']};
        --glass: {ds['glass']};
        --shadow: {ds['shadow']};
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: {ds['font']}; background: var(--bg); color: var(--text); line-height: 1.6; }}
    a {{ color: inherit; text-decoration: none; transition: 0.3s; }}
    .btn {{ padding: 0.8rem 2rem; border-radius: var(--radius); font-weight: 700; cursor: pointer; display: inline-block; }}
    .btn-p {{ background: var(--primary); color: white; border: none; }}
    .card {{ background: var(--surface); padding: 2rem; border-radius: var(--radius); border: var(--border); backdrop-filter: var(--glass); box-shadow: var(--shadow); }}
    """

    # Layout Specific CSS and HTML
    layout_content = ""
    if layout == "Sidebar navigation layout":
        base_css += """
        .app-container { display: flex; min-height: 100vh; }
        .sidebar { width: 280px; background: var(--surface); border-right: var(--border); padding: 2rem; }
        .main-content { flex: 1; padding: 4rem; }
        .nav-vertical { list-style: none; margin-top: 3rem; }
        .nav-vertical li { margin-bottom: 1.5rem; }
        """
        layout_content = f"""
        <div class="app-container">
            <aside class="sidebar">
                <h2 class="logo">{brand}</h2>
                <ul class="nav-vertical">{nav_html}</ul>
            </aside>
            <main class="main-content">
                <h1>{headline}</h1>
                <p>{subheadline}</p>
                <div class="grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; margin-top: 4rem;">
                    {features_html}
                </div>
            </main>
        </div>"""
    elif layout == "Creative portfolio layout":
        base_css += """
        .portfolio-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 4rem; padding: 10% 5%; }
        .big-text { font-size: 8vw; line-height: 0.9; letter-spacing: -4px; font-weight: 800; text-transform: uppercase; }
        """
        layout_content = f"""
        <nav style="padding: 2rem 5%; display: flex; justify-content: space-between;"><h2 class="logo">{brand}</h2><div>Menu</div></nav>
        <header style="padding: 5% 5%;">
            <h1 class="big-text">{headline}</h1>
        </header>
        <div class="portfolio-grid">
            <div class="card" style="height: 600px; display: flex; align-items: flex-end;"><h2>{features[0]['title'] if features else 'Core Project'}</h2></div>
            <div style="display: flex; flex-direction: column; gap: 2rem;">{features_html}</div>
        </div>"""
    elif layout == "E-commerce layout":
        base_css += """
        .shop-grid { display: grid; grid-template-columns: 250px 1fr; gap: 2rem; padding: 5%; }
        .product-card { background: var(--surface); border: var(--border); padding: 1rem; border-radius: var(--radius); }
        .product-img { height: 200px; background: rgba(0,0,0,0.05); margin-bottom: 1rem; border-radius: calc(var(--radius) / 2); }
        """
        products_html = "".join([f'<div class="product-card"><div class="product-img"></div><h4>{f["title"]}</h4><p>${random.randint(49, 999)}</p></div>' for f in features])
        layout_content = f"""
        <nav style="display: flex; justify-content: space-between; padding: 2rem 5%; border-bottom: var(--border);">
            <h2 class="logo">{brand}</h2><ul style="display:flex; list-style:none; gap:2rem;">{nav_html}</ul>
        </nav>
        <div class="shop-grid">
            <aside><h3>Categories</h3><ul style="list-style:none; margin-top:1rem; opacity:0.7;"><li>All Products</li><li>New Arrivals</li><li>Best Sellers</li></ul></aside>
            <main>
                <h1>{headline}</h1>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 2rem;">{products_html}</div>
            </main>
        </div>"""
    elif layout == "Minimal blog layout":
        base_css += """
        .blog-container { max-width: 800px; margin: 0 auto; padding: 10% 2rem; }
        .post-meta { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: var(--accent); margin-bottom: 1rem; }
        .post-card { margin-bottom: 5rem; border-bottom: var(--border); padding-bottom: 5rem; }
        """
        posts_html = "".join([f'<article class="post-card"><div class="post-meta">Published Oct 2026</div><h2>{f["title"]}</h2><p style="margin: 1.5rem 0; opacity: 0.8;">{f["desc"]}</p><a href="#" style="font-weight:700; color:var(--primary);">Read More →</a></article>' for f in features])
        layout_content = f"""
        <nav style="text-align: center; padding: 3rem; border-bottom: var(--border);"><h2 class="logo">{brand}</h2></nav>
        <div class="blog-container">
            <header style="margin-bottom: 6rem; text-align: center;"><h1>{headline}</h1><p style="margin-top:1rem; opacity:0.6;">{subheadline}</p></header>
            {posts_html}
        </div>"""
    else: # Default SaaS Layout
        base_css += """
        nav { display: flex; justify-content: space-between; padding: 1.5rem 10%; align-items: center; border-bottom: var(--border); }
        .hero { text-align: center; padding: 10rem 10%; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; padding: 0 10% 10rem; }
        """
        layout_content = f"""
        <nav><h2 class="logo">{brand}</h2><ul style="display:flex; list-style:none; gap:2rem;">{nav_html}</ul></nav>
        <header class="hero">
            <h1>{headline}</h1>
            <p style="max-width: 800px; margin: 2rem auto;">{subheadline}</p>
            <a href="#" class="btn btn-p">{content['cta_primary']}</a>
        </header>
        <div class="grid">{features_html}</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand} | Redesign</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700&family=Inter:wght@400;700&family=Outfit:wght@400;700&display=swap" rel="stylesheet">
    <style>{base_css}</style>
</head>
<body>
    {layout_content}
</body>
</html>"""

def generate_bonus_redesigns(content: dict, count: int = 3):
    """Generate multiple unique redesign options."""
    layouts = ["Modern SaaS layout", "Creative portfolio layout", "E-commerce layout", "Minimal blog layout", "Split screen layout", "Sidebar navigation layout"]
    styles = ["Minimal", "Glassmorphism", "Dark modern", "Vibrant gradient", "Neumorphism"]
    
    options = []
    used_combinations = set()
    
    while len(options) < count:
        l = random.choice(layouts)
        s = random.choice(styles)
        if (l, s) not in used_combinations:
            used_combinations.add((l, s))
            html = generate_redesign_html(content, layout_override=l, style_override=s)
            options.append({
                "layout": l,
                "style": s,
                "html": html
            })
    return options
