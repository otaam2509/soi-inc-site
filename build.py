#!/usr/bin/env python3
"""株式会社SOI 会社サイトを組み立てる(標準ライブラリのみ)。

src/layout.html(共通の頭・メニュー・お問い合わせ・フッター)に、
src/pages/*.html(各ページの本文)を差し込んで、公開用のHTMLを書き出す。

  python3 build.py        … 書き出し(index.html, recruit/index.html … sitemap.xml)
  python3 build.py --check … 書き出し後に、リンク切れ・画像の抜けなどを点検する

各ページの先頭には <!--page { ...JSON... } --> を書く。
  path        公開URL("/" や "/recruit/")
  title       <title>(検索結果に出る題名)
  description 検索結果の説明文(全角80〜120字が目安)
  crumb       パンくずの表示名(トップは不要)
  service     そのページのサービス情報(構造化データになる)
  noindex     true なら検索に出さない(404など)
よくある質問は <details class="q"><summary>質問</summary><div class="a">答え</div></details>
と書けば、検索向けのFAQ構造化データ(FAQPage)に自動で変換される。
"""
import datetime
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://soi-co-ltd.com"
VERSION = datetime.date.today().strftime("%Y%m%d")
BOOKING_URL = "https://timerex.net/s/otama2509_3ae3/721d36be"
from urllib.parse import quote


def mailto(service):
    """問い合わせメールの下書き(件名と本文のひな形)。serviceは本文に入れるサービス名"""
    body = f"会社名：\nご担当者名：\n気になっているサービス（{service}）：\n御社サイトのURL：\n"
    return "mailto:info@soi-co-ltd.com?subject=" + quote("企画案の相談") + "&amp;body=" + quote(body)


CONTACT_TEXT_DEFAULT = ("御社のサイトを拝見して、採用のSNS運用やショートドラマの企画案を先にお作りします。"
                        "ここまで費用はかかりません。会社名と気になっているサービスだけお送りください。")

# メニュー(表示名, パス)。ヘッダーとフッターで共通
MENU = [
    ("採用SNS運用", "/recruit/"),
    ("AIショートドラマ", "/short-drama/"),
    ("会社概要", "/company/"),
]

ORG = {
    "@type": "Organization",
    "@id": SITE + "/#org",
    "name": "株式会社SOI",
    "legalName": "株式会社SOI",
    "alternateName": "SOI CO.,LTD",
    "url": SITE + "/",
    "logo": SITE + "/assets/logo.png",
    "image": SITE + "/assets/og.jpg",
    "email": "info@soi-co-ltd.com",
    "description": "東京・品川の映像制作会社。現場で撮影する人材採用のSNS運用と、AIで作る商品のショートドラマを、企画・制作から投稿・運用まで一式で手がける。",
    "address": {
        "@type": "PostalAddress",
        "postalCode": "142-0041",
        "addressRegion": "東京都",
        "addressLocality": "品川区",
        "streetAddress": "戸越5-18-16-2F",
        "addressCountry": "JP",
    },
    "founder": {"@type": "Person", "@id": SITE + "/company/#tamate", "name": "玉手志弥", "alternateName": "Yukiya Tamate",
                "jobTitle": "代表取締役", "url": SITE + "/company/#about"},
    "knowsAbout": ["採用動画", "人材採用のSNS運用", "縦型ショート動画", "AIショートドラマ", "映像制作", "公式LINE運用"],
}


def read_page(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--page\s*(\{.*?\})\s*-->\s*", text, re.S)
    if not m:
        sys.exit(f"{path.name}: 先頭に <!--page {{...}} --> がありません")
    meta = json.loads(m.group(1))
    return meta, text[m.end():]


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def faq_items(content):
    items = []
    for q, a in re.findall(r'<details class="q"><summary>(.*?)</summary><div class="a">(.*?)</div></details>', content, re.S):
        items.append({"@type": "Question", "name": strip_tags(q),
                      "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}})
    return items


def jsonld(meta, content):
    url = SITE + meta["path"]
    org = dict(ORG)
    if meta.get("org_description"):  # 採用ページではAIの語を出さない
        org["description"] = meta["org_description"]
        org["knowsAbout"] = [k for k in org["knowsAbout"] if "AI" not in k]
    if meta["path"] == "/":
        org["hasOfferCatalog"] = {"@type": "OfferCatalog", "name": "サービス", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@id": SITE + "/recruit/#service"}},
            {"@type": "Offer", "itemOffered": {"@id": SITE + "/short-drama/#service"}}]}
    graph = [org, {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "株式会社SOI",
                   "inLanguage": "ja", "publisher": {"@id": SITE + "/#org"}}]
    page = {"@type": meta.get("schema_type", "WebPage"), "@id": url + "#webpage", "url": url, "name": meta["title"],
            "description": meta["description"], "inLanguage": "ja", "isPartOf": {"@id": SITE + "/#website"},
            "about": {"@id": SITE + "/#org"}}
    graph.append(page)
    if meta["path"] != "/":
        crumbs = [{"@type": "ListItem", "position": 1, "name": "トップ", "item": SITE + "/"},
                  {"@type": "ListItem", "position": 2, "name": meta["crumb"], "item": url}]
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
    if meta.get("service"):
        s = dict(meta["service"])
        s.update({"@type": "Service", "@id": url + "#service", "provider": {"@id": SITE + "/#org"}, "areaServed": {"@type": "Country", "name": "日本"},
                  "url": url})
        graph.append(s)
    for v in meta.get("videos", []):
        graph.append(dict(v, **{"@type": "VideoObject", "contentUrl": SITE + v["contentUrl"],
                                "thumbnailUrl": SITE + v["thumbnailUrl"], "inLanguage": "ja"}))
    faqs = faq_items(content)
    if faqs:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": faqs})
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=1) + "\n</script>"


def menu_links(current, footer=False):
    items = list(MENU)
    if footer:
        items = [("トップ", "/")] + items
    out = []
    for name, href in items:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'<a href="{href}"{cur}>{name}</a>')
    return "".join(out)


def crumbs_html(meta):
    if meta["path"] == "/" or meta.get("noindex"):
        return ""
    return ('<ol class="crumbs" aria-label="現在地"><li><a href="/">トップ</a></li>'
            f'<li aria-current="page">{meta["crumb"]}</li></ol>')


def out_path(meta, src):
    if src.stem == "404":
        return ROOT / "404.html"
    p = meta["path"].strip("/")
    return ROOT / (p + "/index.html" if p else "index.html")


def build():
    layout = (ROOT / "src/layout.html").read_text(encoding="utf-8")
    pages = []
    for src in sorted((ROOT / "src/pages").glob("*.html")):
        meta, content = read_page(src)
        content = content.replace("{{crumbs}}", crumbs_html(meta))
        html_out = layout
        repl = {
            "title": meta["title"],
            "og_title": meta.get("og_title", meta["title"]),
            "description": meta["description"],
            "url": SITE + meta["path"],
            "site": SITE,
            "og_type": "website",
            "robots": "noindex" if meta.get("noindex") else "index,follow,max-image-preview:large",
            "version": VERSION,
            "jsonld": "" if meta.get("noindex") else jsonld(meta, content),
            "nav": menu_links(meta["path"]),
            "footnav": menu_links(meta["path"], footer=True),
            "mailto": mailto(meta.get("mail_service", "人材採用のSNS運用／AIショートドラマ")),
            "contact_text": meta.get("contact_text", CONTACT_TEXT_DEFAULT),
            "booking_url": BOOKING_URL,
            "content": content.strip(),
        }
        for k, v in repl.items():
            html_out = html_out.replace("{{" + k + "}}", v)
        dst = out_path(meta, src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(html_out, encoding="utf-8")
        meta["_lastmod"] = datetime.date.fromtimestamp(src.stat().st_mtime).isoformat()
        pages.append((meta, dst))
        print("書き出し:", dst.relative_to(ROOT))

    # サイトマップ(検索エンジン向けのページ一覧)
    urls = "".join(f"  <url><loc>{SITE}{m['path']}</loc><lastmod>{m['_lastmod']}</lastmod></url>\n"
                   for m, _ in pages if not m.get("noindex"))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + urls + "</urlset>\n", encoding="utf-8")
    print("書き出し: sitemap.xml")
    return pages


def check(pages):
    """リンク切れ・画像の抜け・題名と説明の長さを点検する。"""
    ng = 0
    for meta, dst in pages:
        text = dst.read_text(encoding="utf-8")
        name = dst.relative_to(ROOT)
        for ref in re.findall(r'(?:href|src|poster)="(/[^"#?]*)', text):
            target = ROOT / ref.lstrip("/")
            if ref.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                print(f"NG {name}: 見つからない {ref}"); ng += 1
        for img in re.findall(r"<img [^>]*>", text):
            if 'alt="' not in img:
                print(f"NG {name}: altのない画像 {img[:60]}"); ng += 1
        if text.count("<h1") != 1:
            print(f"NG {name}: h1が{text.count('<h1')}個"); ng += 1
        d = len(meta["description"])
        if not meta.get("noindex") and not 60 <= d <= 130:
            print(f"注意 {name}: 説明文が{d}字(60〜130字が目安)")
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
            json.loads(block)
    print("点検:", "問題なし" if ng == 0 else f"NG {ng}件")
    return ng


if __name__ == "__main__":
    built = build()
    if "--check" in sys.argv:
        sys.exit(1 if check(built) else 0)
