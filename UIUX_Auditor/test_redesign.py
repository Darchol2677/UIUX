from redesign_engine import extract_site_content, generate_redesign_html

html = '<html><head><title>Test Site</title></head><body><nav><a href="/">Home</a><a href="/about">About</a></nav><h1>Welcome to Test</h1><p>We build amazing things</p><button>Get Started</button></body></html>'
content = extract_site_content(html)
print("BRAND:", content['brand'])
print("HEADLINE:", content['headline'])
print("NAV:", content['nav_links'])
code = generate_redesign_html(content)
print("CODE LENGTH:", len(code))
print("HAS BRAND IN CODE:", content['brand'] in code)
print("HAS HTML:", "<html" in code.lower())
print("FIRST 200:", code[:200])
