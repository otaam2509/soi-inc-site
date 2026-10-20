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
import urllib.parse
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SITE = "https://soi-co-ltd.com"
VERSION = datetime.date.today().strftime("%Y%m%d")
# 相談の窓口=代表 玉手志弥の公式LINE(あいさつ文から面談予約へ。2026-10-20 志弥指示でフォームの代わりに)
LINE_URL = "https://line.me/R/ti/p/@217ombzj"


def mailto(service):
    """問い合わせメールの下書き(件名と本文のひな形)。serviceは本文に入れるサービス名"""
    body = f"会社名：\nご担当者名：\n気になっているサービス（{service}）：\n御社サイトのURL：\n"
    return "mailto:info@soi-co-ltd.com?subject=" + quote("企画案の相談") + "&amp;body=" + quote(body)


# 採用動画の「構成例」(写真を使わない縦型動画の見本画面)
MOCKS = """<div class="mocks" aria-label="採用動画の構成例">
  <figure class="mock" style="--bgimg:url(/assets/recruit/v_morning.jpg)"><span class="mk-top">仕事の1日</span><b>朝7:30、<br>現場へ出発。</b><span class="mk-sub">出勤から退勤までを<br>60秒で</span><span class="mk-bar"></span></figure>
  <figure class="mock m2" style="--bgimg:url(/assets/recruit/v_senior.jpg)"><span class="mk-top">先輩の一言</span><b>入る前、<br>いちばん不安<br>だったこと。</b><span class="mk-sub">働く本人の言葉で</span><span class="mk-bar"></span></figure>
  <figure class="mock m3" style="--bgimg:url(/assets/recruit/v_breakroom.jpg)"><span class="mk-top">職場紹介</span><b>休憩室、<br>ちょっと<br>見せます。</b><span class="mk-sub">道具・車両・休憩室</span><span class="mk-bar"></span></figure>
</div>"""

RECRUIT_ORG_DESC = "東京・品川の映像制作会社。当社のカメラマンが職場で撮影する人材採用のSNS運用を、企画から撮影・編集・投稿・応募の受け付けまで一式で手がける。"

CONTACT_TEXT_DEFAULT = ("御社のサイトを拝見して、採用のSNS運用やショートドラマの企画案を先にお作りします。"
                        "ここまで費用はかかりません。会社名と気になっているサービスだけお送りください。")

# メニュー(表示名, パス)。ヘッダーとフッターで共通
MENU = [
    ("採用SNS運用", "/recruit/"),
    ("AIショートドラマ", "/short-drama/"),
    ("コラム", "/column/"),
    ("会社概要", "/company/"),
]

# コラムの分類(キー: 表示名, 関連サービスのパス, 関連サービス名)
CATEGORIES = {
    "recruit": ("採用・求人", "/recruit/", "人材採用のSNS運用"),
    "drama": ("ショートドラマ・動画", "/short-drama/", "AIショートドラマの制作・運用"),
    "general": ("SNS・動画運用", "/", "株式会社SOIのサービス"),
}

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
    if meta.get("org_description"):  # 採用ページ・採用コラムではAIの語を出さない
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
        trail = [("トップ", "/")] + meta.get("parents", []) + [(meta["crumb"], meta["path"])]
        crumbs = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + h} for i, (n, h) in enumerate(trail)]
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
    if meta.get("article"):
        a = meta["article"]
        graph.append({"@type": "BlogPosting", "@id": url + "#article", "headline": meta["h1"], "description": meta["description"],
                      "datePublished": a["date"], "dateModified": a.get("updated", a["date"]), "inLanguage": "ja",
                      "mainEntityOfPage": {"@id": url + "#webpage"}, "image": SITE + "/assets/og.jpg",
                      "author": {"@id": SITE + "/#org"}, "publisher": {"@id": SITE + "/#org"},
                      "articleSection": CATEGORIES[a["category"]][0]})
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
    mid = "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in meta.get("parents", []))
    return ('<ol class="crumbs" aria-label="現在地"><li><a href="/">トップ</a></li>' + mid +
            f'<li aria-current="page">{meta["crumb"]}</li></ol>')


# ---------- コラム(src/column/*.md) ----------

def inline_md(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[(.+?)\]\((\S+?)\)", r'<a href="\2">\1</a>', t)
    return t


def md_to_html(md):
    """記事用の小さなMarkdown変換。## 見出し / ### 小見出し / - 箇条書き / 1. 番号 / > 囲み / 空行で段落"""
    out, toc, buf, lst = [], [], [], None

    def flush():
        nonlocal buf, lst
        if buf:
            out.append("<p>" + "<br>".join(inline_md(x) for x in buf) + "</p>"); buf = []
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline_md(i)}</li>" for i in items) + f"</{tag}>"); lst = None

    quote = []
    for line in md.splitlines() + [""]:
        if line.startswith(">"):
            flush(); quote.append(line[1:].strip()); continue
        if quote:
            title = quote[0].strip("*") if quote[0].startswith("**") else "SOIの考え方"
            body = quote[1:] if quote[0].startswith("**") else quote
            out.append(f'<aside class="soi-view"><b>{inline_md(title)}</b>' +
                       "".join(f"<p>{inline_md(x)}</p>" for x in body if x) + "</aside>")
            quote = []
        if line.startswith("## "):
            flush(); n = len(toc) + 1; toc.append(line[3:].strip())
            out.append(f'<h2 id="s{n}">{inline_md(line[3:].strip())}</h2>')
        elif line.startswith("### "):
            flush(); out.append(f"<h3>{inline_md(line[4:].strip())}</h3>")
        elif re.match(r"- ", line):
            if buf: flush()
            if not lst or lst[0] != "ul": flush(); lst = ("ul", [])
            lst[1].append(line[2:].strip())
        elif re.match(r"\d+\. ", line):
            if buf: flush()
            if not lst or lst[0] != "ol": flush(); lst = ("ol", [])
            lst[1].append(re.sub(r"^\d+\. ", "", line).strip())
        elif not line.strip():
            flush()
        else:
            if lst: flush()
            buf.append(line.strip())
    flush()
    return "\n".join(out), toc


def read_articles():
    arts = []
    for src in sorted((ROOT / "src/column").glob("*.md")):
        text = src.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if not m:
            sys.exit(f"{src.name}: 先頭に --- で囲んだ設定がありません")
        fm = dict(re.match(r"(\w+):\s*(.*)", l).groups() for l in m.group(1).splitlines() if l.strip())
        if fm.get("draft") == "true":
            continue
        body, toc = md_to_html(text[m.end():])
        fm["slug"] = src.stem
        fm["path"] = f"/column/{src.stem}/"
        fm["body"], fm["toc"], fm["src"] = body, toc, src
        if fm["category"] not in CATEGORIES:
            sys.exit(f"{src.name}: category は {list(CATEGORIES)} のどれか")
        arts.append(fm)
    arts.sort(key=lambda a: a["date"], reverse=True)
    return arts


def article_cards(arts):
    if not arts:
        return '<p class="sub">記事は準備中です。</p>'
    cards = []
    for a in arts:
        cat = CATEGORIES[a["category"]][0]
        cards.append(f'<a class="post" href="{a["path"]}"><span class="meta"><span class="cat">{cat}</span>'
                     f'<time datetime="{a["date"]}">{a["date"].replace("-", ".")}</time></span>'
                     f'<b>{html.escape(a["title"])}</b><span class="ex">{html.escape(a["description"])}</span></a>')
    return '<div class="posts">' + "".join(cards) + "</div>"


def article_page(a, arts):
    cat, svc_path, svc_name = CATEGORIES[a["category"]]
    toc = ""
    if len(a["toc"]) >= 2:
        toc = ('<div class="toc" role="navigation" aria-label="目次"><b>目次</b><ul>' +
               "".join(f'<li><a href="#s{i + 1}">{inline_md(t)}</a></li>' for i, t in enumerate(a["toc"])) + "</ul></div>")
    upd = f'<span>更新 <time datetime="{a["updated"]}">{a["updated"].replace("-", ".")}</time></span>' if a.get("updated") else ""
    related = [x for x in arts if x["category"] == a["category"] and x["slug"] != a["slug"]][:3]
    rel = f'<section class="tint-sand"><div class="wrap"><div class="kicker"><span class="en">Column</span>あわせて読みたい</div>{article_cards(related)}</div></section>' if related else ""
    content = f"""<header class="page-hero">
  <div class="wrap">
    {{{{crumbs}}}}
    <div class="post-meta"><span class="cat">{cat}</span><span>公開 <time datetime="{a["date"]}">{a["date"].replace("-", ".")}</time></span>{upd}</div>
    <h1>{html.escape(a["title"])}</h1>
    <p class="lead">{html.escape(a["description"])}</p>
  </div>
</header>

<section><div class="wrap">
  <article class="prose post-body">
{toc}
{a["body"]}
  </article>
  <div class="post-cta"><b>{svc_name}について</b><span>この記事の内容を、御社の場合にあてはめた企画案を無料でお作りします。</span>
    <div class="ctas"><a class="cta" href="{svc_path}">{svc_name}を見る</a><a class="cta ghost" href="#contact">無料で相談する</a></div></div>
  <p class="byline">文・株式会社SOI（東京・品川の映像制作会社）</p>
</div></section>
{rel}"""
    meta = {"path": a["path"], "crumb": a["title"], "parents": [("コラム", "/column/")], "h1": a["title"],
            "title": a["title"] + "｜株式会社SOI コラム", "description": a["description"],
            "article": {"date": a["date"], "updated": a.get("updated") or a["date"], "category": a["category"]}}
    if a["category"] == "recruit":
        meta.update({"org_description": RECRUIT_ORG_DESC, "mail_service": "人材採用のSNS運用",
                     "contact_text": "御社のサイトや求人を拝見して、採用動画の企画案を先にお作りします。ここまで費用はかかりません。会社名と、募集している職種だけお送りください。"})
    elif a["category"] == "drama":
        meta.update({"mail_service": "AIショートドラマ"})
    return meta, content, a["src"]


def column_index(arts):
    meta = {"path": "/column/", "crumb": "コラム", "schema_type": "CollectionPage",
            "title": "コラム｜採用動画・SNS運用・ショートドラマの考え方｜株式会社SOI",
            "description": "採用動画やSNS運用、商品を物語で見せるショートドラマについて、一般的な基本と、映像制作の現場で私たちが大切にしている考え方をまとめています。"}
    groups = "".join(
        f'<h2 class="cat-h">{name}</h2>' + article_cards([a for a in arts if a["category"] == key])
        for key, (name, _, _) in CATEGORIES.items() if any(a["category"] == key for a in arts))
    content = f"""<header class="page-hero">
  <div class="wrap">
    {{{{crumbs}}}}
    <span class="eyebrow">コラム</span>
    <h1>採用と動画の、基本と考え方</h1>
    <p class="lead">採用動画やSNS運用、商品を物語で見せる動画について、一般的な基本と、映像制作の現場で私たちが大切にしている考え方をまとめています。</p>
  </div>
</header>

<section><div class="wrap">
  <h2 class="cat-h">新着</h2>
  {article_cards(arts[:6])}
  {groups}
</div></section>"""
    return meta, content, max((a["src"] for a in arts), key=lambda p: p.stat().st_mtime) if arts else ROOT / "build.py"


def out_path(meta, src):
    if src.name == "404.html":
        return ROOT / "404.html"
    p = meta["path"].strip("/")
    return ROOT / (p + "/index.html" if p else "index.html")


def build():
    layout = (ROOT / "src/layout.html").read_text(encoding="utf-8")
    arts = read_articles()
    items = []
    for src in sorted((ROOT / "src/pages").glob("*.html")):
        meta, content = read_page(src)
        items.append((meta, content, src))
    items.append(column_index(arts))
    items += [article_page(a, arts) for a in arts]
    pages = []
    for meta, content, src in items:
        content = content.replace("{{crumbs}}", crumbs_html(meta))
        content = content.replace("{{latest_columns}}", article_cards(arts[:3]))
        content = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: f'<svg class="ic" aria-hidden="true"><use href="/assets/icons.svg#{m.group(1)}"/></svg>', content)
        content = content.replace("{{mocks}}", MOCKS)
        for key in CATEGORIES:
            content = content.replace("{{columns:" + key + "}}", article_cards([a for a in arts if a["category"] == key][:3]))
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
            "line_url": LINE_URL,
            "content": content.strip(),
        }
        for k, v in repl.items():
            html_out = html_out.replace("{{" + k + "}}", v)
        html_out = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: f'<svg class="ic" aria-hidden="true"><use href="/assets/icons.svg#{m.group(1)}"/></svg>', html_out)
        dst = out_path(meta, src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(html_out, encoding="utf-8")
        meta["_lastmod"] = datetime.date.fromtimestamp(src.stat().st_mtime).isoformat()
        pages.append((meta, dst))
        print("書き出し:", dst.relative_to(ROOT))

    # AI検索向けの要約(src/llms.txt + コラム一覧)
    llms = (ROOT / "src/llms.txt").read_text(encoding="utf-8").rstrip() + "\n\n## コラム\n\n"
    llms += "".join(f"- [{a['title']}]({SITE}{a['path']}): {a['description']}\n" for a in arts)
    (ROOT / "llms.txt").write_text(llms, encoding="utf-8")
    print("書き出し: llms.txt")

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
        if meta.get("article"):  # コラム: 金額・割合・社外秘の語が混ざっていないか
            body = re.sub(r"<script.*?</script>|<nav.*?</nav>|<footer.*?</footer>|<section id=\"contact\".*?</section>", "", text, flags=re.S)
            body = re.sub(r"<[^>]+>", "", body)
            for pat in (r"\d[\d,]*\s*(?:万円|円)", r"\d+(?:\.\d+)?\s*[%％]", r"\d[\d,]*\s*(?:再生|件の|通の)",
                        r"ウェディング|前撮り|結婚式|新郎|新婦|石井|腸活|腸妊活|ヒロメル|水道職人|liveroa|Liberoa"):
                for m in re.finditer(pat, body):
                    print(f"NG {name}: 公開NGの可能性「{m.group(0)}」… {body[max(0, m.start() - 25):m.end() + 10]!r}"); ng += 1
        if meta.get("org_description"):  # 採用まわりのページに禁止語が出ていないか(メニュー・フッターは除く)
            body = re.sub(r'<nav.*?</nav>|<div class="fnav".*?</div>', "", text, flags=re.S)
            body = urllib.parse.unquote(body)
            for w in ("AI", "ドラマ", "架空"):
                if w in body:
                    i = body.index(w)
                    print(f"NG {name}: 採用ページに「{w}」… {body[max(0, i - 30):i + 10]!r}"); ng += 1
    print("点検:", "問題なし" if ng == 0 else f"NG {ng}件")
    return ng


if __name__ == "__main__":
    built = build()
    if "--check" in sys.argv:
        sys.exit(1 if check(built) else 0)
