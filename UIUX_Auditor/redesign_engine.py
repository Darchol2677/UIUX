from bs4 import BeautifulSoup
import re
import random
from typing import Optional, Dict, Any


def extract_site_content(html: str):
    """Extract meaningful content and styles from the website's HTML."""
    soup = BeautifulSoup(html, 'html.parser')

    primary_color = "#6366f1"
    accent_color = "#ec4899"

    style_content = " ".join([s.get_text() for s in soup.find_all('style')])
    hex_colors = re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', style_content)
    if hex_colors:
        bright_colors = [c for c in hex_colors if c.lower() not in ['#000', '#000000', '#fff', '#ffffff']]
        if len(bright_colors) >= 1: primary_color = bright_colors[0]
        if len(bright_colors) >= 2: accent_color = bright_colors[1]

    for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg', 'head']):
        tag.decompose()

    title = ""
    title_tag = BeautifulSoup(html, 'html.parser').find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)[:80]

    brand = ""
    for sel in ['[class*="logo"]', '[class*="brand"]', '[id*="logo"]', '[id*="brand"]', 'header a', 'nav a']:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t and 2 < len(t) < 40:
                brand = t
                break
    if not brand and title:
        brand = re.split(r'[-|·–—]', title)[0].strip()

    nav_links = []
    nav_found = soup.find('nav') or soup.find('ul', class_=re.compile(r'menu|nav|link|header'))
    if nav_found:
        links = nav_found.find_all('a', href=True)
        for a in links:
            text = a.get_text(strip=True)
            if text and 2 < len(text) < 30 and text not in nav_links:
                nav_links.append(text)
            if len(nav_links) >= 5: break

    headline = ""
    for tag in ['h1', 'h2']:
        el = soup.find(tag)
        if el:
            t = el.get_text(strip=True)
            if t and 10 < len(t) < 150:
                headline = t
                break

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

    cta_buttons = []
    cta_kw = ['get', 'start', 'sign', 'join', 'buy', 'demo', 'download', 'contact', 'try', 'learn', 'explore']
    for btn in soup.find_all(['button', 'a']):
        text = btn.get_text(strip=True)
        if text and any(kw in text.lower() for kw in cta_kw) and len(text) < 30:
            if text not in cta_buttons:
                cta_buttons.append(text)
        if len(cta_buttons) >= 3: break

    features = []
    all_text = soup.get_text().lower()
    is_ecom = any(w in all_text for w in ['price', '$', 'product', 'cart', 'shop', 'order'])

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

    archetype = "Landing page"
    if is_ecom:
        archetype = "E-commerce"
    elif any(w in all_text for w in ["pricing", "saas", "software", "platform", "subscription", "cloud"]):
        archetype = "Business / SaaS"
    elif any(w in all_text for w in ["blog", "article", "news", "reading", "published"]):
        archetype = "Blog"
    elif any(w in all_text for w in ["portfolio", "creative", "design", "art", "projects", "work"]):
        archetype = "Portfolio"

    res_data = {
        "brand": brand or "Digital Co.",
        "title": title,
        "headline": headline or title or "Next-Gen Digital Experience",
        "subheadline": subheadline or "Empowering your workflow with intelligent, beautiful solutions designed for the modern web.",
        "nav_links": list(nav_links or ["Features", "About", "Pricing", "Contact"]),
        "cta_primary": str(cta_buttons[0] if cta_buttons else "Get Started Free →"),
        "cta_secondary": str(cta_buttons[1] if len(cta_buttons) > 1 else "Watch Demo"),
        "features": list(features)[:6],
        "is_ecom": bool(is_ecom),
        "primary_color": str(primary_color),
        "accent_color": str(accent_color),
        "archetype": str(archetype)
    }
    return res_data


THEMES = [
    {
        "name": "Vivid Gradient",
        "body_bg": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
        "nav_bg": "rgba(255,255,255,0.05)",
        "nav_border": "rgba(255,255,255,0.1)",
        "nav_color": "#ffffff",
        "hero_bg": "transparent",
        "h1_color": "#ffffff",
        "h1_accent": "linear-gradient(90deg, #a78bfa, #ec4899)",
        "p_color": "rgba(255,255,255,0.75)",
        "btn_primary_bg": "linear-gradient(135deg, #a78bfa, #ec4899)",
        "btn_primary_color": "#ffffff",
        "btn_secondary_bg": "rgba(255,255,255,0.1)",
        "btn_secondary_color": "#ffffff",
        "card_bg": "rgba(255,255,255,0.05)",
        "card_border": "1px solid rgba(255,255,255,0.1)",
        "card_color": "#ffffff",
        "card_muted": "rgba(255,255,255,0.65)",
        "card_icon_bg": "rgba(167,139,250,0.2)",
        "card_icon_color": "#a78bfa",
        "badge_bg": "rgba(167,139,250,0.2)",
        "badge_color": "#c4b5fd",
        "footer_bg": "rgba(0,0,0,0.3)",
        "footer_color": "rgba(255,255,255,0.5)",
        "font": "Inter",
        "radius": "16px",
        "glass": "blur(20px)",
        "shadow": "0 25px 50px rgba(0,0,0,0.4)",
    },
    {
        "name": "Apple Minimal",
        "body_bg": "#f5f5f7",
        "nav_bg": "rgba(255,255,255,0.85)",
        "nav_border": "rgba(0,0,0,0.08)",
        "nav_color": "#1d1d1f",
        "hero_bg": "transparent",
        "h1_color": "#1d1d1f",
        "h1_accent": "linear-gradient(90deg, #0071e3, #34aadc)",
        "p_color": "#6e6e73",
        "btn_primary_bg": "#0071e3",
        "btn_primary_color": "#ffffff",
        "btn_secondary_bg": "#ffffff",
        "btn_secondary_color": "#1d1d1f",
        "card_bg": "#ffffff",
        "card_border": "1px solid rgba(0,0,0,0.06)",
        "card_color": "#1d1d1f",
        "card_muted": "#6e6e73",
        "card_icon_bg": "rgba(0,113,227,0.08)",
        "card_icon_color": "#0071e3",
        "badge_bg": "rgba(0,113,227,0.08)",
        "badge_color": "#0071e3",
        "footer_bg": "#f5f5f7",
        "footer_color": "#6e6e73",
        "font": "Inter",
        "radius": "18px",
        "glass": "none",
        "shadow": "0 4px 24px rgba(0,0,0,0.06)",
    },
    {
        "name": "Neo-Brutalism",
        "body_bg": "#fde047",
        "nav_bg": "#ffffff",
        "nav_border": "#000000",
        "nav_color": "#000000",
        "hero_bg": "#fde047",
        "h1_color": "#000000",
        "h1_accent": "none",
        "p_color": "#3f3f46",
        "btn_primary_bg": "#000000",
        "btn_primary_color": "#fde047",
        "btn_secondary_bg": "#ffffff",
        "btn_secondary_color": "#000000",
        "card_bg": "#ffffff",
        "card_border": "3px solid #000000",
        "card_color": "#000000",
        "card_muted": "#52525b",
        "card_icon_bg": "#fde047",
        "card_icon_color": "#000000",
        "badge_bg": "#000000",
        "badge_color": "#fde047",
        "footer_bg": "#000000",
        "footer_color": "rgba(255,255,255,0.6)",
        "font": "Outfit",
        "radius": "0px",
        "glass": "none",
        "shadow": "6px 6px 0px #000000",
    },
    {
        "name": "Cyberpunk Neon",
        "body_bg": "#09090b",
        "nav_bg": "rgba(0,242,255,0.04)",
        "nav_border": "rgba(0,242,255,0.15)",
        "nav_color": "#00f2ff",
        "hero_bg": "transparent",
        "h1_color": "#ffffff",
        "h1_accent": "linear-gradient(90deg, #00f2ff, #d946ef)",
        "p_color": "rgba(0,242,255,0.7)",
        "btn_primary_bg": "transparent",
        "btn_primary_color": "#00f2ff",
        "btn_secondary_bg": "rgba(217,70,239,0.12)",
        "btn_secondary_color": "#d946ef",
        "card_bg": "rgba(0,242,255,0.03)",
        "card_border": "1px solid rgba(0,242,255,0.2)",
        "card_color": "#ffffff",
        "card_muted": "rgba(0,242,255,0.6)",
        "card_icon_bg": "rgba(0,242,255,0.1)",
        "card_icon_color": "#00f2ff",
        "badge_bg": "rgba(217,70,239,0.15)",
        "badge_color": "#d946ef",
        "footer_bg": "rgba(0,0,0,0.5)",
        "footer_color": "rgba(0,242,255,0.4)",
        "font": "Courier New",
        "radius": "4px",
        "glass": "blur(16px)",
        "shadow": "0 0 30px rgba(0,242,255,0.15)",
    },
    {
        "name": "Editorial Luxury",
        "body_bg": "#0a0a0a",
        "nav_bg": "transparent",
        "nav_border": "rgba(212,175,55,0.2)",
        "nav_color": "#ffffff",
        "hero_bg": "transparent",
        "h1_color": "#ffffff",
        "h1_accent": "linear-gradient(90deg, #d4af37, #f5d680)",
        "p_color": "#a1a1aa",
        "btn_primary_bg": "#d4af37",
        "btn_primary_color": "#000000",
        "btn_secondary_bg": "transparent",
        "btn_secondary_color": "#d4af37",
        "card_bg": "#111111",
        "card_border": "1px solid rgba(212,175,55,0.15)",
        "card_color": "#ffffff",
        "card_muted": "#a1a1aa",
        "card_icon_bg": "rgba(212,175,55,0.1)",
        "card_icon_color": "#d4af37",
        "badge_bg": "rgba(212,175,55,0.1)",
        "badge_color": "#d4af37",
        "footer_bg": "#050505",
        "footer_color": "#52525b",
        "font": "Georgia",
        "radius": "2px",
        "glass": "none",
        "shadow": "none",
    }
]


def generate_redesign_html(content: dict, layout_override: Optional[str] = None, style_override: Optional[str] = None) -> str:
    brand = content.get('brand', 'Brand')
    headline = content.get('headline', 'Transform Your Digital Presence')
    subheadline = content.get('subheadline', 'Empowering businesses with modern, intelligent web solutions.')
    nav_links = content.get('nav_links', ['Features', 'About', 'Pricing', 'Contact'])
    features = content.get('features', [])
    cta_primary = content.get('cta_primary', 'Get Started Free →')
    cta_secondary = content.get('cta_secondary', 'Watch Demo')
    arch = content.get('archetype', 'Landing page')

    # Pick theme
    if style_override:
        theme = next((t for t in THEMES if t['name'] == style_override), random.choice(THEMES))
    else:
        theme = random.choice(THEMES)

    t = theme
    font_face = "Inter" if t['font'] == "Inter" else t['font']
    google_font_param = t['font'].replace(' ', '+')
    is_brutalism = t['name'] == 'Neo-Brutalism'
    is_cyber = t['name'] == 'Cyberpunk Neon'
    is_luxury = t['name'] == 'Editorial Luxury'

    nav_html = "".join([f'<a href="#">{l}</a>' for l in nav_links[:5]])

    icons = ["🚀", "⚡", "💎", "🎯", "🔒", "✨"]
    feature_cards = ""
    for i, f in enumerate(features[:6]):
        feature_cards += f"""
        <div class="feat-card">
            <div class="feat-icon">{icons[i % len(icons)]}</div>
            <h3>{f.get('title', 'Feature')}</h3>
            <p>{f.get('desc', 'Delivering excellence at every touchpoint.') or 'Delivering excellence at every touchpoint.'}</p>
        </div>"""

    if not feature_cards:
        default_feats = [
            ("Lightning Fast", "⚡", "Optimized for performance with sub-second load times."),
            ("Secure by Design", "🔒", "Enterprise-grade security protecting your data."),
            ("AI-Powered", "🤖", "Smart automation that grows with your business."),
        ]
        for title, icon, desc in default_feats:
            feature_cards += f"""
            <div class="feat-card">
                <div class="feat-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>"""

    btn_border = "3px solid #000" if is_brutalism else ("1px solid #00f2ff" if is_cyber else "none")
    btn2_border = "3px solid #000" if is_brutalism else ("1px solid #d946ef" if is_cyber else ("1px solid #d4af37" if is_luxury else "none"))
    h1_gradient_css = f"background: {t['h1_accent']}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;" if t['h1_accent'] not in ('none', '') else f"color: {t['h1_color']};"

    badge_label = {"E-commerce": "🛒 E-Commerce", "Business / SaaS": "🚀 SaaS Platform", "Blog": "📝 Blog", "Portfolio": "🎨 Portfolio"}.get(arch, "⭐ Modern Web")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand} — AI Redesign ({t['name']})</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family={google_font_param}:wght@300;400;600;700;800;900&family=Outfit:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: '{font_face}', system-ui, sans-serif;
            background: {t['body_bg']};
            color: {t['h1_color']};
            min-height: 100vh;
            overflow-x: hidden;
        }}

        /* NAV */
        nav {{
            position: sticky; top: 0; z-index: 100;
            display: flex; align-items: center; justify-content: space-between;
            padding: 1.2rem 5%;
            background: {t['nav_bg']};
            border-bottom: 1px solid {t['nav_border']};
            backdrop-filter: {t['glass']};
        }}
        .nav-logo {{
            font-size: 1.4rem; font-weight: 800; color: {t['nav_color']};
            text-decoration: none; letter-spacing: -0.5px;
        }}
        .nav-links {{ display: flex; gap: 2rem; list-style: none; }}
        .nav-links a {{
            color: {t['nav_color']}; text-decoration: none; font-size: 0.95rem;
            font-weight: 500; opacity: 0.8; transition: opacity 0.2s;
        }}
        .nav-links a:hover {{ opacity: 1; }}
        .nav-cta {{
            background: {t['btn_primary_bg']}; color: {t['btn_primary_color']};
            border: {btn_border}; padding: 0.6rem 1.5rem;
            border-radius: {t['radius']}; font-weight: 700; font-size: 0.9rem;
            cursor: pointer; text-decoration: none;
            box-shadow: {t['shadow']};
        }}

        /* HERO */
        .hero {{
            min-height: 92vh;
            display: grid;
            grid-template-columns: 1fr 1fr;
            align-items: center;
            gap: 4rem;
            padding: 5rem 5%;
            position: relative;
        }}
        @media (max-width: 768px) {{
            .hero {{ grid-template-columns: 1fr; text-align: center; }}
            .hero-visual {{ display: none; }}
        }}
        .hero-content {{ display: flex; flex-direction: column; align-items: flex-start; }}
        @media (max-width: 768px) {{ .hero-content {{ align-items: center; }} }}
        .hero-badge {{
            display: inline-flex; align-items: center; gap: 0.5rem;
            background: {t['badge_bg']}; color: {t['badge_color']};
            padding: 0.4rem 1.2rem; border-radius: 50px;
            font-size: 0.85rem; font-weight: 600; margin-bottom: 1.5rem;
            border: 1px solid {t['nav_border']};
        }}
        h1 {{
            font-size: clamp(2.4rem, 4.5vw, 4.5rem);
            font-weight: 900; line-height: 1.1;
            letter-spacing: -2px; margin-bottom: 1.5rem;
            {h1_gradient_css}
        }}
        .hero-content p {{
            font-size: 1.15rem;
            color: {t['p_color']};
            max-width: 520px; line-height: 1.75; margin-bottom: 2.5rem;
        }}
        .hero-btns {{
            display: flex; gap: 1rem; flex-wrap: wrap;
        }}
        /* Browser Mockup */
        .hero-visual {{
            position: relative;
            display: flex; align-items: center; justify-content: center;
        }}
        .browser-mockup {{
            width: 100%; max-width: 520px;
            background: {t['card_bg']};
            border: {t['card_border']};
            border-radius: 16px;
            overflow: hidden;
            box-shadow: {t['shadow']};
            backdrop-filter: {t['glass']};
            animation: float-up 4s ease-in-out infinite;
        }}
        @keyframes float-up {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-12px); }}
        }}
        .browser-bar {{
            background: {t['nav_bg']};
            border-bottom: 1px solid {t['nav_border']};
            padding: 0.75rem 1rem;
            display: flex; align-items: center; gap: 0.5rem;
        }}
        .browser-dot {{
            width: 10px; height: 10px; border-radius: 50%;
        }}
        .browser-url {{
            flex: 1; background: rgba(128,128,128,0.15);
            border-radius: 6px; padding: 0.25rem 0.75rem;
            font-size: 0.75rem; color: {t['p_color']}; margin: 0 0.75rem;
        }}
        .browser-screen {{
            padding: 1.5rem;
            display: flex; flex-direction: column; gap: 0.75rem;
        }}
        .mock-header {{
            height: 12px; border-radius: 4px; width: 60%;
            background: {t['badge_bg']};
        }}
        .mock-line {{
            height: 8px; border-radius: 4px;
            background: rgba(128,128,128,0.15);
        }}
        .mock-cards {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-top: 0.5rem;
        }}
        .mock-card {{
            background: {t['badge_bg']};
            border-radius: 8px; padding: 0.75rem;
            display: flex; flex-direction: column; gap: 0.4rem;
        }}
        .mock-card-icon {{ font-size: 1.1rem; }}
        .mock-card-title {{
            height: 7px; background: rgba(128,128,128,0.3); border-radius: 3px; width: 70%;
        }}
        .mock-btn {{
            width: 40%; height: 28px; border-radius: 6px;
            background: {t['btn_primary_bg']}; margin-top: 0.5rem;
        }}
        /* Floating pills on the mockup */
        .float-pill {{
            position: absolute;
            background: {t['card_bg']};
            border: {t['card_border']};
            backdrop-filter: blur(12px);
            border-radius: 50px;
            padding: 0.5rem 1rem;
            display: flex; align-items: center; gap: 0.5rem;
            font-size: 0.8rem; font-weight: 600; color: {t['card_color']};
            box-shadow: {t['shadow']};
        }}
        .pill-1 {{ top: 10%; left: -15%; animation: float-up 3.5s ease-in-out 0.5s infinite; }}
        .pill-2 {{ bottom: 10%; right: -10%; animation: float-up 4.5s ease-in-out 1s infinite; }}
        .btn-primary {{
            background: {t['btn_primary_bg']}; color: {t['btn_primary_color']};
            border: {btn_border}; padding: 1rem 2.5rem;
            border-radius: {t['radius']}; font-weight: 800; font-size: 1.05rem;
            cursor: pointer; text-decoration: none; display: inline-block;
            box-shadow: {t['shadow']}; transition: transform 0.2s, filter 0.2s;
        }}
        .btn-primary:hover {{ transform: translateY(-3px); filter: brightness(1.1); }}
        .btn-secondary {{
            background: {t['btn_secondary_bg']}; color: {t['btn_secondary_color']};
            border: {btn2_border}; padding: 1rem 2.5rem;
            border-radius: {t['radius']}; font-weight: 700; font-size: 1.05rem;
            cursor: pointer; text-decoration: none; display: inline-block;
            transition: transform 0.2s;
        }}
        .btn-secondary:hover {{ transform: translateY(-3px); }}

        /* STATS */
        .stats {{
            display: flex; justify-content: center; gap: 4rem; flex-wrap: wrap;
            padding: 3rem 5%; border-top: 1px solid {t['nav_border']};
            border-bottom: 1px solid {t['nav_border']};
        }}
        .stat {{ text-align: center; }}
        .stat-num {{
            font-size: 2.5rem; font-weight: 900; color: {t['h1_color']};
            display: block;
        }}
        .stat-label {{ color: {t['p_color']}; font-size: 0.9rem; font-weight: 500; }}

        /* FEATURES */
        .features-section {{
            padding: 6rem 5%;
        }}
        .section-label {{
            text-align: center; margin-bottom: 0.8rem;
            font-size: 0.85rem; font-weight: 700; letter-spacing: 2px;
            text-transform: uppercase; color: {t['badge_color']};
        }}
        .section-title {{
            text-align: center; font-size: clamp(1.8rem, 3.5vw, 2.8rem);
            font-weight: 800; margin-bottom: 1rem; color: {t['h1_color']};
            letter-spacing: -0.5px;
        }}
        .section-sub {{
            text-align: center; color: {t['p_color']};
            max-width: 550px; margin: 0 auto 4rem; line-height: 1.7;
        }}
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
            gap: 1.5rem;
        }}
        .feat-card {{
            background: {t['card_bg']};
            border: {t['card_border']};
            border-radius: {t['radius']};
            padding: 2.2rem;
            backdrop-filter: {t['glass']};
            box-shadow: {t['shadow']};
            transition: transform 0.35s, box-shadow 0.35s;
        }}
        .feat-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 30px 60px rgba(0,0,0,0.25);
        }}
        .feat-icon {{
            width: 52px; height: 52px;
            background: {t['card_icon_bg']};
            border-radius: calc({t['radius']} * 0.75);
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem; margin-bottom: 1.4rem;
        }}
        .feat-card h3 {{
            font-size: 1.15rem; font-weight: 700;
            color: {t['card_color']}; margin-bottom: 0.8rem;
        }}
        .feat-card p {{
            font-size: 0.95rem; color: {t['card_muted']}; line-height: 1.65;
        }}

        /* CTA BANNER */
        .cta-banner {{
            margin: 0 5% 4rem;
            background: {t['btn_primary_bg']};
            border-radius: {t['radius']};
            border: {btn_border};
            padding: 4rem 2rem;
            text-align: center;
            box-shadow: {t['shadow']};
        }}
        .cta-banner h2 {{
            font-size: clamp(1.6rem, 3vw, 2.4rem);
            font-weight: 900; color: {t['btn_primary_color']};
            margin-bottom: 0.8rem;
        }}
        .cta-banner p {{
            color: {t['btn_primary_color']}; opacity: 0.8;
            margin-bottom: 2rem; font-size: 1.05rem;
        }}
        .cta-banner .btn-white {{
            background: {t['btn_secondary_bg']}; color: {t['btn_secondary_color']};
            border: {btn2_border}; padding: 1rem 2.5rem;
            border-radius: {t['radius']}; font-weight: 800; font-size: 1rem;
            cursor: pointer; text-decoration: none; display: inline-block;
        }}

        /* FOOTER */
        footer {{
            background: {t['footer_bg']};
            border-top: 1px solid {t['nav_border']};
            padding: 3rem 5%;
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: wrap; gap: 1rem;
        }}
        .footer-logo {{ font-size: 1.2rem; font-weight: 800; color: {t['h1_color']}; }}
        footer p {{ color: {t['footer_color']}; font-size: 0.85rem; }}
        .footer-links {{ display: flex; gap: 1.5rem; }}
        .footer-links a {{ color: {t['footer_color']}; text-decoration: none; font-size: 0.85rem; }}
    </style>
</head>
<body>

    <!-- NAVIGATION -->
    <nav>
        <a class="nav-logo" href="#">{brand}</a>
        <ul class="nav-links">
            {nav_html}
        </ul>
        <a class="nav-cta" href="#">{cta_primary}</a>
    </nav>

    <!-- HERO -->
    <section class="hero">
        <div class="hero-content">
            <div class="hero-badge">{badge_label}</div>
            <h1>{headline}</h1>
            <p>{subheadline}</p>
            <div class="hero-btns">
                <a class="btn-primary" href="#">{cta_primary}</a>
                <a class="btn-secondary" href="#">{cta_secondary}</a>
            </div>
        </div>
        <div class="hero-visual">
            <div class="float-pill pill-1">⚡ 2.5x Faster</div>
            <div class="browser-mockup">
                <div class="browser-bar">
                    <div class="browser-dot" style="background:#ff5f57;"></div>
                    <div class="browser-dot" style="background:#febc2e;"></div>
                    <div class="browser-dot" style="background:#28c840;"></div>
                    <div class="browser-url">{brand.lower().replace(' ','')}  .com</div>
                </div>
                <div class="browser-screen">
                    <div class="mock-header"></div>
                    <div class="mock-line" style="width:90%"></div>
                    <div class="mock-line" style="width:75%"></div>
                    <div class="mock-cards">
                        <div class="mock-card"><div class="mock-card-icon">🚀</div><div class="mock-card-title"></div></div>
                        <div class="mock-card"><div class="mock-card-icon">⚡</div><div class="mock-card-title"></div></div>
                        <div class="mock-card"><div class="mock-card-icon">💎</div><div class="mock-card-title"></div></div>
                        <div class="mock-card"><div class="mock-card-icon">🎯</div><div class="mock-card-title"></div></div>
                    </div>
                    <div class="mock-btn"></div>
                </div>
            </div>
            <div class="float-pill pill-2">★ 4.9 Rated</div>
        </div>
    </section>

    <!-- STATS -->
    <div class="stats">
        <div class="stat"><span class="stat-num">10K+</span><span class="stat-label">Happy Users</span></div>
        <div class="stat"><span class="stat-num">99.9%</span><span class="stat-label">Uptime SLA</span></div>
        <div class="stat"><span class="stat-num">4.9★</span><span class="stat-label">User Rating</span></div>
        <div class="stat"><span class="stat-num">2.5x</span><span class="stat-label">Faster Results</span></div>
    </div>

    <!-- FEATURES -->
    <section class="features-section">
        <p class="section-label">✦ Why Choose Us</p>
        <h2 class="section-title">Everything You Need to Succeed</h2>
        <p class="section-sub">Powerful tools built for modern businesses. Designed for clarity, built for scale.</p>
        <div class="features-grid">
            {feature_cards}
        </div>
    </section>

    <!-- CTA SECTION -->
    <section class="cta-banner">
        <h2>Ready to Transform Your Website?</h2>
        <p>Join thousands of businesses already winning with better design and strategy.</p>
        <a class="btn-white" href="#">{cta_primary}</a>
    </section>

    <!-- FOOTER -->
    <footer>
        <span class="footer-logo">{brand}</span>
        <p>© 2025 {brand}. All rights reserved.</p>
        <div class="footer-links">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Contact</a>
        </div>
    </footer>

</body>
</html>"""


def generate_bonus_redesigns(content: dict, count: int = 3):
    """Generate multiple unique redesign options."""
    options = []
    used_themes = set()

    theme_names = [t['name'] for t in THEMES]
    shuffled = theme_names[:]
    random.shuffle(shuffled)

    for style in shuffled[:count]:
        if style not in used_themes:
            used_themes.add(style)
            html = generate_redesign_html(content, style_override=style)
            options.append({
                "layout": "Modern Layout",
                "style": style,
                "html": html
            })
    return options
