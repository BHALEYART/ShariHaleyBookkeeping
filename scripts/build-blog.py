#!/usr/bin/env python3
"""Builds the blog: /blog/ (index) and /blog/<slug>/ (one page per post).

Posts live in scripts/blog-posts/*.html. Each file starts with a JSON block
inside <!-- --> (title, description, FAQ, etc.) followed by the article body
as plain HTML. Header and footer are copied from about-us/index.html, so the
blog always matches the rest of the site.

Also refreshes the ?v= cache-busting values for site.css and site.js on EVERY
page, so run it after any CSS/JS change too.

Usage (from the repo root):  python3 scripts/build-blog.py
"""
import glob, hashlib, html, json, os, re, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://sharihaleybookkeeping.com"
NAME = "Shari Haley Bookkeeping"
PHONE, TEL = "386-320-9378", "+13863209378"
EMAIL = "sharihaleybookkeeping@gmail.com"
TEMPLATE = os.path.join(ROOT, "about-us", "index.html")
POSTS_DIR = os.path.join(ROOT, "scripts", "blog-posts")
WPM = 220


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def esc(s):
    return html.escape(s, quote=True)


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def nice_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


# ---------------------------------------------------------------- cache busting
def ver(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


CSS_V, JS_V = ver("assets/css/site.css"), ver("assets/js/site.js")


def bust(s):
    s = re.sub(r"site\.css\?v=[0-9a-f]+", f"site.css?v={CSS_V}", s)
    return re.sub(r"site\.js\?v=[0-9a-f]+", f"site.js?v={JS_V}", s)


# ---------------------------------------------------------------- template parts
T = bust(read(TEMPLATE))
HEAD_ASSETS = T[T.index('<link rel="icon"'):T.index('<script type="application/ld+json">')]
HEADER = T[T.index("<body>") + len("<body>\n"):T.index('<main id="main" tabindex="-1">')]
FOOTER = T[T.index("</main>") + len("</main>\n"):T.index("</body>")]
HEADER = HEADER.replace(' aria-current="page"', "")


def at_depth(chunk, prefix):
    """Template paths are written for depth 1 (../); rewrite for another depth."""
    return re.sub(r'((?:href|src|srcset)=")\.\./', lambda m: m.group(1) + prefix, chunk)


def header_for(prefix, current):
    h = at_depth(HEADER, prefix)
    return h.replace(f'<a href="{prefix}blog/">Blog</a>', f'<a href="{prefix}blog/" aria-current="{current}">Blog</a>')


# ---------------------------------------------------------------- shared schema
PUBLISHER = {
    "@type": "AccountingService", "@id": f"{SITE}/#business", "name": NAME, "url": f"{SITE}/",
    "logo": f"{SITE}/assets/img/logo.png", "telephone": TEL, "email": EMAIL,
    "address": {"@type": "PostalAddress", "addressLocality": "DeLand", "addressRegion": "FL", "addressCountry": "US"},
}
AUTHOR = {
    "@type": "Person", "@id": f"{SITE}/#shari", "name": "Shari Haley",
    "jobTitle": "Bookkeeper and QuickBooks Platinum Certified ProAdvisor", "url": f"{SITE}/about-us/",
    "worksFor": {"@id": f"{SITE}/#business"},
}
WEBSITE = {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": NAME, "inLanguage": "en-US",
           "publisher": {"@id": f"{SITE}/#business"}}


def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def crumb_nav(items, prefix):
    out = []
    for i, (n, u) in enumerate(items):
        if i == len(items) - 1:
            out.append(f'<li><span aria-current="page">{esc(n)}</span></li>')
        else:
            out.append(f'<li><a href="{prefix}{u.lstrip("/")}">{esc(n)}</a></li>')
    return f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol>{"".join(out)}</ol></nav>'


def page(path, prefix, title, desc, graph, body, og_type="website", extra_meta=""):
    url = SITE + path
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    t, d = esc(title), esc(desc)
    return f'''<!doctype html>
<html lang="en-US" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#143630">
<meta name="format-detection" content="telephone=no">
<meta name="geo.region" content="US-FL">
<meta name="geo.placename" content="DeLand">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NAME} — bookkeeping in DeLand, Florida">
<meta property="og:locale" content="en_US">
{extra_meta}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{SITE}/assets/img/og-image.jpg">
<link rel="alternate" type="application/rss+xml" title="{NAME} blog" href="{SITE}/blog/feed.xml">
{at_depth(HEAD_ASSETS, prefix)}<script type="application/ld+json">
{ld}
</script>
</head>
<body>
{header_for(prefix, "page" if path == "/blog/" else "true")}<main id="main" tabindex="-1">
{body}
</main>
{at_depth(FOOTER, prefix)}</body>
</html>
'''


def cta(prefix, audience):
    if audience.startswith("CPA"):
        h, t, b = ("Looking for a bookkeeper to refer clients to?",
                   "Shari works alongside CPAs and tax professionals in DeLand, Volusia County, and Central Florida. Let’s talk about how she can support your clients.",
                   "Start a conversation")
    else:
        h, t, b = ("Want a second set of eyes on your books?",
                   "Start with a free, no-obligation consultation. Shari will review where your books stand and what it would take to get them current and accurate.",
                   "Request my free consultation")
    return f'''<section class="cta-band" aria-labelledby="cta-heading">
  <div class="wrap">
    <h2 id="cta-heading">{h}</h2>
    <p>{t}</p>
    <div class="btn-row">
      <a class="btn btn-coral" href="{prefix}contact/#consultation">{b}</a>
      <a class="btn btn-ghost" href="tel:{TEL}">Call {PHONE}</a>
    </div>
  </div>
</section>'''


def card(p, prefix, heading="h3"):
    return f'''<article class="card post-card">
  <span class="post-tag">{esc(p["audience"])}</span>
  <{heading}><a href="{prefix}blog/{p["slug"]}/">{esc(p["h1"])}</a></{heading}>
  <p>{esc(p["summary"])}</p>
  <span class="post-meta">{p["minutes"]} min read</span>
</article>'''


# ---------------------------------------------------------------- load posts
posts = []
for f in sorted(glob.glob(os.path.join(POSTS_DIR, "*.html"))):
    raw = read(f)
    m = re.match(r"\s*<!--(.*?)-->\s*(.*)\Z", raw, re.S)
    if not m:
        sys.exit(f"{f}: missing <!-- {{json}} --> header")
    meta = json.loads(m.group(1))
    meta["body"] = m.group(2).strip()
    meta.setdefault("updated", meta["date"])
    meta.setdefault("faq", [])
    words = len(strip_tags(meta["body"] + " ".join(a for _, a in meta["faq"])).split())
    meta["minutes"] = max(2, round(words / WPM))
    for k in ("slug", "title", "h1", "short", "description", "summary", "audience", "date"):
        if not meta.get(k):
            sys.exit(f"{f}: missing '{k}'")
    if len(meta["description"]) > 160:
        print(f"warning: {meta['slug']} description is {len(meta['description'])} chars (aim for <= 155)")
    posts.append(meta)

posts.sort(key=lambda p: (p.get("order", 99), p["slug"]))
by_slug = {p["slug"]: p for p in posts}

# ---------------------------------------------------------------- post pages
for p in posts:
    prefix = "../../"
    path = f"/blog/{p['slug']}/"
    trail = [("Home", "/"), ("Blog", "/blog/"), (p["short"], path)]

    faq_html = ""
    if p["faq"]:
        items = "\n".join(f'<details>\n  <summary>{esc(q)}</summary>\n  <div>{a}</div>\n</details>' for q, a in p["faq"])
        faq_html = f'''
      <section class="post-faq faq" aria-labelledby="faq-h">
        <h2 id="faq-h">Quick answers</h2>
{items}
      </section>'''

    rel_slugs = p.get("related") or []
    related = [by_slug[s] for s in rel_slugs if s in by_slug]
    for q in posts:
        if len(related) >= 3:
            break
        if q is not p and q not in related and q["audience"] == p["audience"]:
            related.append(q)
    for q in posts:
        if len(related) >= 3:
            break
        if q is not p and q not in related:
            related.append(q)
    related_html = "\n".join(card(q, prefix) for q in related[:3])

    body = f'''<article class="post" aria-labelledby="post-title">
<header class="page-hero">
  <div class="wrap">
    {crumb_nav(trail, prefix)}
    <span class="eyebrow" style="color:var(--coral-300)">{esc(p["audience"])}</span>
    <h1 id="post-title">{esc(p["h1"])}</h1>
    <p>{esc(p["description"])}</p>
    <p class="post-byline">By <a href="{prefix}about-us/">Shari Haley</a>, QuickBooks Platinum Certified ProAdvisor · <time datetime="{p["updated"]}">{nice_date(p["updated"])}</time> · {p["minutes"]} min read</p>
  </div>
</header>

<div class="section">
  <div class="wrap">
    <div class="prose">
{p["body"]}
{faq_html}
      <p class="post-note">This article is general information, not tax or legal advice. Every business is different, so check with your CPA or tax professional about your situation.</p>
    </div>
  </div>
</div>
</article>

<section class="section section-alt" aria-labelledby="related-h">
  <div class="wrap">
    <h2 id="related-h">Keep reading</h2>
    <div class="grid grid-3">
{related_html}
    </div>
  </div>
</section>

{cta(prefix, p["audience"])}'''

    posting = {
        "@type": "BlogPosting", "@id": f"{SITE}{path}#article", "headline": p["h1"], "description": p["description"],
        "datePublished": p["date"], "dateModified": p["updated"], "inLanguage": "en-US",
        "mainEntityOfPage": f"{SITE}{path}", "url": f"{SITE}{path}", "image": f"{SITE}/assets/img/og-image.jpg",
        "author": {"@id": f"{SITE}/#shari"}, "publisher": {"@id": f"{SITE}/#business"},
        "isPartOf": {"@id": f"{SITE}/blog/#blog"}, "wordCount": len(strip_tags(p["body"]).split()),
        "about": p.get("keywords", []), "audience": {"@type": "Audience", "audienceType": p["audience"]},
    }
    graph = [WEBSITE, PUBLISHER, AUTHOR, posting, crumbs(trail)]
    if p["faq"]:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in p["faq"]]})
    extra = (f'<meta property="article:published_time" content="{p["date"]}">\n'
             f'<meta property="article:modified_time" content="{p["updated"]}">\n'
             f'<meta property="article:author" content="{SITE}/about-us/">\n')
    write(os.path.join(ROOT, "blog", p["slug"], "index.html"),
          page(path, prefix, p["title"], p["description"], graph, body, og_type="article", extra_meta=extra))

# ---------------------------------------------------------------- blog index
prefix = "../"
groups = {}
for p in posts:
    groups.setdefault(p["audience"], []).append(p)
sections = []
for i, (aud, items) in enumerate(groups.items()):
    hid = f"group-{i}"
    cls = "section section-alt" if i % 2 else "section"
    cards = "\n".join(card(p, prefix) for p in items)
    sections.append(f'''<section class="{cls}" aria-labelledby="{hid}">
  <div class="wrap">
    <h2 id="{hid}">{"For CPAs and tax professionals" if aud.startswith("CPA") else "For " + esc(aud.lower())}</h2>
    <div class="grid grid-3">
{cards}
    </div>
  </div>
</section>''')

index_body = f'''<section class="page-hero" aria-labelledby="blog-heading">
  <div class="wrap">
    {crumb_nav([("Home", "/"), ("Blog", "/blog/")], prefix)}
    <h1 id="blog-heading">Bookkeeping answers for small business owners</h1>
    <p>Plain-English answers to the questions business owners in DeLand and Volusia County ask most, from a QuickBooks Platinum Certified ProAdvisor with 25+ years of experience. Plus resources for the CPAs and tax professionals who work with them.</p>
  </div>
</section>

{chr(10).join(sections)}

{cta(prefix, "Business owners")}'''

blog_node = {"@type": "Blog", "@id": f"{SITE}/blog/#blog", "url": f"{SITE}/blog/", "name": f"{NAME} blog",
             "description": "Bookkeeping, QuickBooks, and tax-season answers for small businesses in DeLand and Volusia County, Florida.",
             "publisher": {"@id": f"{SITE}/#business"}, "inLanguage": "en-US",
             "blogPost": [{"@type": "BlogPosting", "headline": p["h1"], "url": f"{SITE}/blog/{p['slug']}/",
                           "datePublished": p["date"], "dateModified": p["updated"], "author": {"@id": f"{SITE}/#shari"}} for p in posts]}
write(os.path.join(ROOT, "blog", "index.html"),
      page("/blog/", prefix, "Bookkeeping Blog | Shari Haley Bookkeeping, DeLand FL",
           "Answers to common small business bookkeeping, QuickBooks, and tax-season questions from a DeLand, FL QuickBooks Platinum ProAdvisor. Plus resources for CPAs.",
           [WEBSITE, PUBLISHER, AUTHOR, blog_node, crumbs([("Home", "/"), ("Blog", "/blog/")])], index_body))

# ---------------------------------------------------------------- RSS feed
items = "\n".join(f'''  <item>
    <title>{esc(p["h1"])}</title>
    <link>{SITE}/blog/{p["slug"]}/</link>
    <guid>{SITE}/blog/{p["slug"]}/</guid>
    <pubDate>{date.fromisoformat(p["date"]).strftime("%a, %d %b %Y")} 12:00:00 -0500</pubDate>
    <description>{esc(p["description"])}</description>
  </item>''' for p in posts)
write(os.path.join(ROOT, "blog", "feed.xml"), f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{NAME} blog</title>
  <link>{SITE}/blog/</link>
  <description>Bookkeeping, QuickBooks, and tax-season answers for small businesses in DeLand and Volusia County, Florida.</description>
  <language>en-us</language>
{items}
</channel>
</rss>
''')

# ---------------------------------------------------------------- sitemap
sm = read(os.path.join(ROOT, "sitemap.xml"))
sm = re.sub(r"\s*<url>\s*<loc>https://sharihaleybookkeeping\.com/blog/[^<]*</loc>.*?</url>", "", sm, flags=re.S)
latest = max(p["updated"] for p in posts)
entries = [f"  <url>\n    <loc>{SITE}/blog/</loc>\n    <lastmod>{latest}</lastmod>\n  </url>"]
entries += [f"  <url>\n    <loc>{SITE}/blog/{p['slug']}/</loc>\n    <lastmod>{p['updated']}</lastmod>\n  </url>" for p in posts]
sm = sm.replace("</urlset>", "\n".join(entries) + "\n</urlset>")
write(os.path.join(ROOT, "sitemap.xml"), sm)

# ---------------------------------------------------------------- cache-bust every page
for f in glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "*", "index.html")):
    s = read(f)
    b = bust(s)
    if b != s:
        write(f, b)

print(f"Built {len(posts)} posts + blog index, feed, sitemap (css v={CSS_V}, js v={JS_V}).")
