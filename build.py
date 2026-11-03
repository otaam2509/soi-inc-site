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
import hashlib
import json
import re
import sys
from pathlib import Path
import urllib.parse
import xml.etree.ElementTree as ET
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SITE = "https://soi-co-ltd.com"
# Invalidate cached styles/scripts even when multiple releases occur on the same day.
VERSION = hashlib.sha256(b"".join(p.read_bytes() for p in sorted((ROOT / "assets").rglob("*"))
                                 if p.suffix in {".css", ".js"})).hexdigest()[:12]
# 相談の窓口=代表 玉手志弥の公式LINE(あいさつ文から面談予約へ。2026-10-20 志弥指示でフォームの代わりに)
LINE_URL = "https://lin.ee/TMkuCTn"  # LINE公式マネージャー「友だち追加用URL」(2026-10-20取得)
GA_ID = "G-GR6X7ZXK0D"  # Googleアナリティクス(2026-10-20作成・info@soi-co-ltd.com)


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
    ("ツイミル", "/tsuimiru/"),
    ("コラム", "/column/"),
    ("会社概要", "/company/"),
]

# コラムの分類(キー: 表示名, 関連サービスのパス, 関連サービス名)
CATEGORIES = {
    "recruit": ("採用・求人", "/recruit/", "人材採用のSNS運用"),
    "drama": ("ショートドラマ・動画", "/tsuimiru/", "AI動画制作・ショートドラマ「ツイミル」"),
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
    "foundingDate": "2024-09-12",
    "identifier": {"@type": "PropertyValue", "propertyID": "法人番号", "value": "6010703007351"},
    "areaServed": {"@type": "Country", "name": "日本"},
    "description": "東京・品川の映像制作会社。現場で撮影する人材採用のSNS運用と、AIで作る商品のショートドラマを、企画・制作から投稿・運用まで一式で手がける。",
    "address": {
        "@type": "PostalAddress",
        "postalCode": "142-0041",
        "addressRegion": "東京都",
        "addressLocality": "品川区",
        "streetAddress": "戸越5-18-16-2F",
        "addressCountry": "JP",
    },
    "founder": {"@type": "Person", "@id": SITE + "/company/#about", "name": "玉手志弥", "alternateName": "Yukiya Tamate",
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
    if meta.get("article_list"):
        page["mainEntity"] = {"@type": "ItemList", "numberOfItems": len(meta["article_list"]),
                              "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                                   "url": SITE + a["path"], "name": a["title"]}
                                                  for i, a in enumerate(meta["article_list"])]}
    graph.append(page)
    if meta["path"] == "/company/":
        graph.append({"@type": "Person", "@id": SITE + "/company/#about", "name": "玉手志弥",
                      "alternateName": "Yukiya Tamate", "jobTitle": "代表取締役・フォトグラファー",
                      "url": SITE + "/company/#about", "image": SITE + "/assets/president.jpg",
                      "worksFor": {"@id": SITE + "/#org"}})
    if meta["path"] != "/":
        trail = [("トップ", "/")] + meta.get("parents", []) + [(meta["crumb"], meta["path"])]
        crumbs = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + h} for i, (n, h) in enumerate(trail)]
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
    if meta.get("article"):
        a = meta["article"]
        graph.append({"@type": "BlogPosting", "@id": url + "#article", "headline": meta["h1"], "description": meta["description"],
                      "datePublished": a["date"], "dateModified": a.get("updated", a["date"]), "inLanguage": "ja",
                      "mainEntityOfPage": {"@id": url + "#webpage"}, "image": SITE + "/assets/og.jpg",
                      "author": {"@type": "Organization", "@id": SITE + "/#org", "name": "株式会社SOI", "url": SITE + "/company/#editorial-policy"}, "publisher": {"@id": SITE + "/#org"},
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
    table = []

    def flush_table():
        if not table:
            return
        rows = [[c.strip() for c in row.strip('|').split('|')] for row in table]
        if len(rows) >= 2 and all(re.fullmatch(r':?-{3,}:?', c) for c in rows[1]):
            head = ''.join(f'<th scope="col">{inline_md(c)}</th>' for c in rows[0])
            body = ''.join('<tr>' + ''.join(f'<td>{inline_md(c)}</td>' for c in row) + '</tr>' for row in rows[2:])
            out.append(f'<div class="article-table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
        else:
            out.append('<p>' + '<br>'.join(inline_md(row) for row in table) + '</p>')
        table.clear()

    def flush():
        nonlocal buf, lst
        if buf:
            out.append("<p>" + "<br>".join(inline_md(x) for x in buf) + "</p>"); buf = []
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline_md(i)}</li>" for i in items) + f"</{tag}>"); lst = None

    quote = []
    for line in md.splitlines() + [""]:
        if line.startswith('|') and line.endswith('|'):
            flush(); table.append(line); continue
        flush_table()
        if line.startswith(">"):
            flush(); quote.append(line[1:].strip()); continue
        if quote:
            title = quote[0].strip("*") if quote[0].startswith("**") else "SOIの考え方"
            body = quote[1:] if quote[0].startswith("**") else quote
            out.append(f'<aside class="soi-view"><b>{inline_md(title)}</b>' +
                       "".join(f"<p>{inline_md(x)}</p>" for x in body if x) + "</aside>")
            quote = []
        picture = re.fullmatch(r'!\[([^\]]+)\]\((/[^\s)]+)\)', line)
        if picture:
            flush()
            alt, src = picture.groups()
            out.append(f'<figure class="article-image"><img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}" loading="lazy"></figure>')
        elif line.startswith("## "):
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
    related_slugs = {
        "recruit": ["recruit-sns-agency", "care-rpo-or-sns", "recruit-video-basics", "recruit-measure-results"],
        "drama": ["short-drama-production-company", "drama-script-structure", "drama-ai-quality-check", "drama-not-ai-looking"],
        "general": ["sns-hook-first-seconds", "sns-keep-posting-ledger", "sns-metrics-saves"],
    }
    pool = [x for x in arts if x["category"] == a["category"] and x["slug"] != a["slug"]]
    ordered = [x for slug in related_slugs[a["category"]] for x in pool if x["slug"] == slug]
    related = (ordered + [x for x in pool if x not in ordered])[:3]
    rel = f'<section class="tint-sand"><div class="wrap"><div class="kicker"><span class="en">Column</span>あわせて読みたい</div>{article_cards(related)}</div></section>' if related else ""
    toc = ""
    if len(a["toc"]) >= 2:
        toc = ('<div class="toc" role="navigation" aria-label="目次"><b>目次</b><ul>' +
               "".join(f'<li><a href="#s{i + 1}">{inline_md(t)}</a></li>' for i, t in enumerate(a["toc"])) + "</ul></div>")
    upd = f'<span>更新 <time datetime="{a["updated"]}">{a["updated"].replace("-", ".")}</time></span>' if a.get("updated") else ""
    if a["category"] == "drama":
        cta_title = "この考え方を、あなたの商品・サービスなら。"
        cta_text = "企画が決まっていなくても大丈夫です。制作サンプルを見て、公式LINEから申込フォームへお進みください。フォーム回答後、そのまま30分のオンライン相談を予約できます。"
        cta_links = '<a class="cta" href="/tsuimiru/#works">ツイミルの制作サンプルを見る</a><a class="cta ghost" href="https://lin.ee/SC6LK06" target="_blank" rel="noopener noreferrer" data-track="line">公式LINEで相談・見積もり</a>'
        quick = '<a href="/tsuimiru/">ツイミルのサービス内容・制作サンプル →</a>'
    elif a["category"] == "recruit":
        cta_title = "御社の職場なら、何を撮るか。"
        cta_text = "会社名と募集職種をもとに、採用動画の企画案を無料でお作りします。投稿や応募窓口まで相談できます。"
        cta_links = f'<a class="cta" href="/recruit/">SNS採用代行の範囲を見る</a><a class="cta ghost" href="{LINE_URL}" data-track="line">LINEで企画案を相談する</a>'
        quick = '<a href="/recruit/video/">採用動画の制作内容・流れを見る →</a>'
    else:
        cta_title = "動画を、誰に何のために届けるか。"
        cta_text = "職場を伝える採用動画と、商品・サービスの魅力を伝える映像。目的に近いサービスをご覧ください。"
        cta_links = '<a class="cta" href="/recruit/">採用動画・SNS運用を相談する</a><a class="cta ghost" href="/tsuimiru/">ツイミルの動画制作を相談する</a>'
        quick = '<a href="/recruit/">採用動画・SNS運用</a><span aria-hidden="true"> ／ </span><a href="/tsuimiru/">ツイミルの動画制作</a>'
    author = ('<aside class="article-author" aria-label="記事の制作・運営情報"><p class="author-label">執筆・編集：株式会社SOI</p>'
              '<p>東京都品川区の映像制作会社。現場での撮影・編集と、企業の動画発信に関する考え方をまとめています。</p>'
              '<p>代表：玉手志弥（フォトグラファー）。<a href="/company/#about">代表紹介</a>・<a href="/company/#editorial-policy">記事の編集方針</a></p></aside>')
    video = ''
    if a.get('video_src'):
        video = (f'<figure class="article-video"><video controls playsinline preload="none" '
                 f'poster="{html.escape(a["video_poster"], quote=True)}" aria-label="{html.escape(a["video_title"], quote=True)}">'
                 f'<source src="{html.escape(a["video_src"], quote=True)}" type="video/mp4"></video>'
                 f'<figcaption>{html.escape(a["video_caption"])}</figcaption></figure>')
    content = f"""<header class="page-hero"><div class="wrap">
    {{{{crumbs}}}}
    <div class="post-meta"><span class="cat">{cat}</span><span>公開 <time datetime="{a['date']}">{a['date'].replace('-', '.')}</time></span>{upd}</div>
    <h1>{html.escape(a['title'])}</h1><p class="lead">{html.escape(a['description'])}</p>
    <p class="article-credit">執筆・編集：<a href="/company/#editorial-policy">株式会社SOI</a></p>
    <div class="article-service-link">{quick}</div>
</div></header>
<section class="article-reading"><div class="wrap"><article class="prose post-body">{toc}{video}{a['body']}</article>
  <div class="post-cta"><b>{cta_title}</b><span>{cta_text}</span><div class="ctas">{cta_links}</div></div>
  {author}<a class="journal-back" href="/column/">← コラム一覧に戻る</a>
</div></section>{rel}"""
    meta = {"path": a["path"], "crumb": a["title"], "parents": [("コラム", "/column/")], "h1": a["title"], "body_class": "soi-site soi-article",
            "title": a["title"] + "｜株式会社SOI コラム", "description": a["description"],
            "article": {"date": a["date"], "updated": a.get("updated") or a["date"], "category": a["category"]}}
    if a.get('video_src'):
        meta['videos'] = [{"name": a['video_title'], "description": a['video_caption'],
                           "contentUrl": a['video_src'], "thumbnailUrl": a['video_poster'],
                           "uploadDate": a['video_uploaded'], "duration": a['video_duration'] }]
    if a["category"] == "recruit":
        meta.update({"org_description": RECRUIT_ORG_DESC, "mail_service": "人材採用のSNS運用",
                     "contact_text": "御社のサイトや求人を拝見して、採用動画の企画案を先にお作りします。ここまで費用はかかりません。会社名と、募集している職種だけお送りください。"})
    elif a["category"] == "drama":
        meta.update({"mail_service": "AIショートドラマ", "contact_channel": "tsuimiru_line"})
    return meta, content, a["src"]


JOURNAL_COVERS = {
    "ai-image-video-hibiwa": ("5枚から、\nひとつの物語。", "film"),
    "line-contact-measurement": ("クリックと、\n問い合わせ。", "measure"),
    "recruit-sns-agency": ("採用の発信、\nどこまで任せる？", "photo"),
    "care-rpo-or-sns": ("採用代行？\n採用SNS？", "split"),
    "short-drama-production-company": ("作品だけで、\n選ばない。", "frames"),
    "recruit-video-basics": ("職場の空気を、\n映す。", "photo"),
    "recruit-sns-start": ("撮る前に、\n決めること。", "steps"),
    "recruit-video-interview-style": ("その人の言葉で、\n職場を伝える。", "quote"),
    "recruit-job-posting-3points": ("求人票の、\nその先へ。", "steps"),
    "recruit-line-application": ("応募のあとの、\n最初の一言。", "quote"),
    "recruit-interview-noshow": ("面接までを、\nつなぐ。", "steps"),
    "recruit-retention-3timings": ("入社のあとも、\n声をかける。", "quote"),
    "recruit-indeed-vs-sns": ("探す人と、\nまだ探さない人。", "split"),
    "recruit-measure-results": ("採用の効果、\n何で測る？", "measure"),
    "short-drama-scene": ("商品のある、\nひとつの場面。", "frames"),
    "drama-script-structure": ("説明より、\n物語を。", "frames"),
    "drama-ai-quality-check": ("1カットずつ、\n確かめる。", "frames"),
    "drama-not-ai-looking": ("つくるのは、\n信頼感。", "split"),
    "drama-expression-check": ("言い切る前に、\n立ち止まる。", "quote"),
    "drama-analyze-winners": ("伸びた理由を、\n分解する。", "steps"),
    "sns-clip-one-topic": ("1本に、\nひとつの話。", "frames"),
    "sns-editing-review": ("仕上がりは、\n見返しで変わる。", "frames"),
    "sns-telop-keywords": ("全部より、\n要点を。", "quote"),
    "sns-metrics-saves": ("その数字は、\n何を表す？", "measure"),
    "sns-hook-first-seconds": ("最初の数秒に、\n見る理由を。", "frames"),
    "sns-keep-posting-ledger": ("続けるための、\n型と記録。", "steps"),
    "photo-natural-expression": ("ポーズより、\n会話から。", "photo"),
}


def journal_card(a):
    label, motif = JOURNAL_COVERS.get(a["slug"], (a["title"], "frames"))
    title = html.escape(a["title"])
    cat = CATEGORIES[a["category"]][0]
    cover_label = html.escape(label).replace("\n", "<br>")
    media = '<span class="cover-shape"><i></i><i></i><i></i></span>'
    if motif == "film":
        media = '<img src="/assets/work/hibiwa/storyboard.jpg" alt="架空ブランドHIBIWAの動画制作サンプル" width="1350" height="480" loading="lazy"><small class="cover-disclosure">架空ブランドの制作サンプル</small>'
    elif motif == "photo":
        media = '<img src="/assets/recruit/care_filming.jpg" alt="職場での動画撮影を表したイメージ" width="1400" height="940" loading="lazy"><small class="cover-disclosure">写真はイメージです</small>'
    visual = f'<div class="journal-cover cover-{a["category"]} motif-{motif}">{media}<span class="cover-label" aria-hidden="true">{cover_label}</span></div>'
    search = html.escape(a["title"] + " " + a["description"] + " " + cat, quote=True)
    return (f'<article class="journal-card" data-category="{a["category"]}" data-search="{search}">'
            f'<a href="{a["path"]}" aria-labelledby="title-{a["slug"]}">{visual}'
            f'<div class="journal-card-copy"><div class="journal-meta"><span>{cat}</span><time datetime="{a["date"]}">{a["date"].replace("-", ".")}</time></div>'
            f'<h3 id="title-{a["slug"]}">{title}</h3><p>{html.escape(a["description"])}</p>'
            '<span class="journal-read" aria-hidden="true">記事を読む <span>↗</span></span></div></a></article>')


def column_index(arts):
    meta = {"path": "/column/", "crumb": "コラム", "schema_type": "CollectionPage", "updated": max((a.get('updated') or a['date'] for a in arts), default='2026-11-03'),
            "body_class": "soi-site soi-journal", "article_list": arts, "contact_channel": "service_choice",
            "contact_heading": "読んだ、その先を。",
            "contact_text": "記事の考え方を、御社の採用や商品づくりにどう活かすか。目的に近い窓口からご相談ください。",
            "title": "コラム｜採用動画・SNS運用・ショートドラマの考え方｜株式会社SOI",
            "description": "SOIの採用動画・SNS運用・ショートドラマ制作について、自社の制作工程や運用の見直し、依頼前に確認したい内容を紹介します。"}
    filters = ''.join(f'<button type="button" data-category="{key}" aria-pressed="false">{"動画制作" if key == "drama" else name}<span>{sum(a["category"] == key for a in arts):02d}</span></button>'
                      for key, (name, _, _) in CATEGORIES.items())
    cards = ''.join(journal_card(a) for a in arts)
    content = f"""<header class="journal-hero"><div class="wrap">
  {{{{crumbs}}}}
  <div class="journal-masthead"><span>SOI JOURNAL</span><span>採用・映像・運用のコラム</span></div>
  <div class="journal-intro"><h1>伝える、<br class="journal-mobile-break">その先へ<span>。</span></h1><p>何を撮るか。どう届けるか。<br>制作の裏側から、運用の見直しまで。<br>SOIの記録と考え方。</p></div>
  <div class="journal-feature-heading"><h2>SOIの取り組みから</h2><a href="#articles">すべての記事を見る <span aria-hidden="true">↓</span></a></div>
  <div class="journal-features">
    <a class="journal-feature feature-film" href="/column/ai-image-video-hibiwa/" aria-labelledby="feature-film-title">
      <div class="feature-image"><img src="/assets/work/hibiwa/storyboard.jpg" alt="HIBIWAの制作サンプルを構成する、指輪のある日常の5場面" width="1350" height="480" fetchpriority="high"><span>架空ブランドの制作サンプル</span></div>
      <div class="feature-copy"><div class="journal-meta"><span>制作ノート / ツイミル</span><span>01</span></div><h2 id="feature-film-title">5枚の画像を、<br>19.2秒の物語に。</h2><p>指輪ブランド「HIBIWA」のサンプルでたどる、画像・言葉・動きの組み立て方。</p><span class="feature-arrow" aria-hidden="true">↗</span></div>
    </a>
    <a class="journal-feature feature-measure" href="/column/line-contact-measurement/" aria-labelledby="feature-measure-title">
      <div class="journal-meta"><span>運用ノート / SOI</span><span>02</span></div>
      <div class="measure-visual" aria-hidden="true"><span>クリック</span><b>≠</b><span>問い合わせ</span></div>
      <div><h2 id="feature-measure-title">「相談」を、<br>正しく数える。</h2><p>LINEボタンのクリックと、実際の問い合わせ。自社サイトの計測を見直した記録。</p></div><span class="feature-arrow" aria-hidden="true">↗</span>
    </a>
  </div>
</div></header>
<section class="journal-archive" id="articles" aria-labelledby="archive-title"><div class="wrap">
  <div class="archive-heading"><div><span class="journal-overline">ALL ARTICLES</span><h2 id="archive-title">記事を探す<span>。</span></h2></div><span class="archive-total">{len(arts):02d}<small>ARTICLES</small></span></div>
  <form class="journal-tools" role="search" aria-label="コラムを探す" hidden>
    <div class="journal-filters" role="group" aria-label="記事のテーマ"><button type="button" data-category="all" aria-pressed="true">すべて<span>{len(arts):02d}</span></button>{filters}</div>
    <div class="journal-search"><label for="journal-search">キーワード検索</label><div><input id="journal-search" type="search" placeholder="例：採用動画、LINE、台本" autocomplete="off"><button type="button" class="journal-clear" aria-label="検索文字を消す" hidden>×</button></div></div>
  </form>
  <div class="journal-results"><p id="journal-result-count" role="status" aria-live="polite" aria-atomic="true">全{len(arts)}記事</p><span>新着順</span></div>
  <div class="journal-grid">{cards}</div>
  <div class="journal-empty" hidden><h3>該当する記事がありません。</h3><p>別のキーワードやテーマでお探しください。</p><button type="button">条件をリセットして、すべて見る →</button></div>
  <div class="journal-policy"><span>SOI JOURNAL</span><p>自社で取り組んだことと、制作・運用の考え方を発信します。<br>サンプルと実績を分け、確認できた事実をもとに。</p><a href="/company/#editorial-policy">記事の編集方針 <span aria-hidden="true">↗</span></a></div>
</div></section>"""
    return meta, content, max((a["src"] for a in arts), key=lambda p: p.stat().st_mtime) if arts else ROOT / "build.py"


def out_path(meta, src):
    if src.name == "404.html":
        return ROOT / "404.html"
    p = meta["path"].strip("/")
    return ROOT / (p + "/index.html" if p else "index.html")


def build():
    # File mtimes change when cloning. Keep actual content-update dates in the sitemap.
    previous_dates = {}
    sitemap_path = ROOT / "sitemap.xml"
    if sitemap_path.exists():
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for entry in ET.parse(sitemap_path).findall("s:url", ns):
            previous_dates[entry.findtext("s:loc", namespaces=ns)] = entry.findtext("s:lastmod", namespaces=ns)
    layout = (ROOT / "src/layout.html").read_text(encoding="utf-8")
    arts = read_articles()
    items = []
    for src in sorted((ROOT / "src/pages").glob("*.html")):
        meta, content = read_page(src)
        items.append((meta, content, src))
    # 専用ブランドのLPは、共通レイアウトを使わず独自のデザインで公開する。
    for src in sorted((ROOT / "src/standalone").glob("*.html")):
        meta, content = read_page(src)
        meta["standalone"] = True
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
        use_tsuimiru_line = meta.get("contact_channel") == "tsuimiru_line" or meta["path"] == "/short-drama/"
        if meta.get("contact_channel") == "service_choice":
            contact_heading = meta.get("contact_heading", "目的に合う窓口へ、ご相談ください")
            contact_text = meta.get("contact_text", CONTACT_TEXT_DEFAULT)
            contact_actions = f'<a class="contact-choice" href="{LINE_URL}" data-track="line" data-contact-service="recruit"><small>SNS採用代行・採用動画制作</small><strong>採用について相談する <span aria-hidden="true">↗</span></strong></a><a class="contact-choice choice-film" data-contact-service="tsuimiru" href="https://lin.ee/SC6LK06" target="_blank" rel="noopener noreferrer" data-track="line"><small>商品・サービスの動画制作</small><strong>ツイミルに相談する <span aria-hidden="true">↗</span></strong></a>'
            contact_note = f'採用のご相談は代表の玉手が対応。ツイミルはLINEの申込フォームからオンライン相談へ。<br>メールでのご相談：<a href="{mailto("採用支援／動画制作")}">info@soi-co-ltd.com</a>'
        elif use_tsuimiru_line:
            contact_heading = "動画制作の相談・お見積もりは、公式LINEへ"
            contact_text = "友だち追加後、申込フォームにわかる範囲でご入力ください。企画や予算が未定でも大丈夫です。フォーム回答後、そのまま30分のオンライン相談を予約できます。"
            contact_actions = '<a class="cta cta-line" href="https://lin.ee/SC6LK06" target="_blank" rel="noopener noreferrer" data-track="line">公式LINEで相談・見積もり</a><a class="cta ghost" href="/tsuimiru/#works">制作サンプルを見る</a>'
            contact_note = '必須項目は、お名前・LINE表示名・相談内容の3つです。フォーム送信だけで発注・料金は発生しません。'
        else:
            contact_heading = "無料で、企画案をお作りします"
            contact_text = meta.get("contact_text", CONTACT_TEXT_DEFAULT)
            contact_actions = f'<a class="cta cta-line" href="{LINE_URL}" data-track="line">{{{{icon:chat}}}}公式LINEで相談する</a><a class="cta ghost" href="{mailto(meta.get("mail_service", "人材採用のSNS運用／AIショートドラマ"))}" data-track="mail">メールで相談する</a>'
            contact_note = 'LINEは代表の玉手が直接お返事します。オンライン面談（30分〜）のご予約もLINEからどうぞ。<br>メールの場合は info@soi-co-ltd.com へ'
        html_out = content if meta.get("standalone") else layout
        repl = {
            "site_verification": '<meta name="msvalidate.01" content="2CEEE1AB3468FF6B339F1006A1F6DBF5">' if meta['path'] == '/' else '',
            "title": meta["title"],
            "body_class": html.escape(meta.get("body_class", "soi-site"), quote=True),
            "og_title": meta.get("og_title", meta["title"]),
            "description": meta["description"],
            "url": SITE + meta["path"],
            "site": SITE,
            "og_type": "article" if meta.get("article") else "website",
            "robots": "noindex" if meta.get("noindex") else "index,follow,max-image-preview:large",
            "version": VERSION,
            "jsonld": "" if meta.get("noindex") else jsonld(meta, content),
            "nav": menu_links(meta["path"]),
            "footnav": menu_links(meta["path"], footer=True),
            "mailto": mailto(meta.get("mail_service", "人材採用のSNS運用／AIショートドラマ")),
            "contact_text": contact_text,
            "contact_heading": contact_heading,
            "contact_actions": contact_actions,
            "contact_note": contact_note,
            "line_url": LINE_URL,
            "ga_id": GA_ID,
            "content": content.strip(),
        }
        for k, v in repl.items():
            html_out = html_out.replace("{{" + k + "}}", v)
        html_out = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: f'<svg class="ic" aria-hidden="true"><use href="/assets/icons.svg#{m.group(1)}"/></svg>', html_out)
        dst = out_path(meta, src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(html_out, encoding="utf-8")
        article = meta.get("article", {})
        meta["_lastmod"] = (meta.get("updated") or article.get("updated") or article.get("date")
                            or previous_dates.get(SITE + meta["path"])
                            or datetime.date.fromtimestamp(src.stat().st_mtime).isoformat())
        datetime.date.fromisoformat(meta["_lastmod"])
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


def indexnow(pages):
    """IndexNow(Bing・ChatGPT検索など)に全URLの更新を通知する"""
    import urllib.request
    key = (ROOT / ".indexnow_key").read_text().strip()
    urls = [SITE + m["path"] for m, _ in pages if not m.get("noindex")]
    body = json.dumps({"host": "soi-co-ltd.com", "key": key, "keyLocation": f"{SITE}/{key}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, f"{len(urls)}件")


if __name__ == "__main__":
    built = build()
    if "--indexnow" in sys.argv:
        indexnow(built)
    if "--check" in sys.argv:
        sys.exit(1 if check(built) else 0)
