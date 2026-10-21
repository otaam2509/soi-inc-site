# 株式会社SOI 会社サイト

- 公開先: https://soi-co-ltd.com/ （2026-10-19取得・Squarespace Domains。GitHub otaam2509/soi-inc-site の main を GitHub Pages で配信・`CNAME`ファイルで独自ドメイン化。旧URL otaam2509.github.io/soi-inc-site/ は自動で転送）
- 連絡先: info@soi-co-ltd.com
- 構成(2026-10-19 複数ページ化): **編集するのは `src/` だけ**。`python3 build.py --check` で公開用HTMLを書き出し＋点検(リンク切れ・alt・h1・構造化データ)。書き出したファイル(index.html・recruit/・short-drama/・company/・privacy/・404.html・sitemap.xml)もコミットする(GitHub Pagesはそのまま配信)
  - `src/layout.html` = 全ページ共通(head・メニュー・お問い合わせ帯・フッター) / `src/pages/*.html` = 各ページ本文。先頭の `<!--page {...}-->` に題名・説明文・パス等
  - `assets/css/site.css` = 見た目(色は冒頭 :root だけ触る) / `assets/js/site.js` = 動画の自動再生
  - FAQは `<details class="q"><summary>質問</summary><div class="a">答え</div></details>` で書けば、検索向けFAQ構造化データに自動変換
  - `llms.txt` = AI検索向けの会社要約(事実が変わったら手で直す) / `robots.txt` / `sitemap.xml`(自動)
  - ローカル確認: `python3 -m http.server 8794` → http://localhost:8794/
- 方針: ウェディング要素は載せない。実績・お客様の声・数値成果は実物が確認できるまで載せない
- 素材: 制作例の動画・カット・工程画像は `../AIショートドラマLP/` から複製（架空の商品のサンプル。「架空」表記は外さない）。代表写真・ロゴは旧Next.js版（~/soi-corporate/public/）から
- 金額はサイトに書かない(2026-09-28志弥指示)。費用は相談時に説明
- 事業は「人材採用のSNS運用」(実写・当社カメラマンが撮影)と「AIショートドラマ」の2つ(2026-10-13志弥指示)。採用の欄には「AI」「ドラマ」「架空」と書かない
- トンマナ: SOI公式HP(soiwedding.com テーマ soi-wedding)と同じ色・書体に統一(2026-10-13)。紙色#f7f3ee/墨#141b22/海#2f6b74・#173a41/金#c2a878、見出し=Noto Serif JP 500、英字ラベル=Cormorant Garamond、本文=Noto Sans JP 300、角丸4px。色を足すときは index.html 冒頭の :root だけを触る
- MVV(#philosophy): 経営方針「玉手の根本」「玉手の理念」から企業向けに言い換えた案(2026-10-13・志弥確認待ち)。Mission=その会社にしかない物語を、伝わる映像にして、届け続ける。/Vision=出会うべき人と、ちゃんと出会える世の中へ。/Value=現場で本物を撮る・見えないところほど丁寧に・続けられる形にする
- 後半の型(2026-10-13 志弥「後半ほどトンマナが弱い」→修正): 地色は 紙→墨青(理念)→紙→砂(採用)→紙→砂(作り方)→紙→砂(代表)→紙→墨青の帯(問い合わせ)→濃色フッター と交互。箱は枠線でなく影(--shadow/--shadow-s)、表は見出し列を砂色(.tbl)。新しい欄を足すときもこの交互と影を守る
- トンマナの正本(2026-10-14): https://claude.ai/artifact/WsZggfk4zjNnpFFCTMg5dt (Design System。色・書体・言葉・形・写真・部品見本)。金は3段=gold(濃い地の上と差し線)/gold-deep #927642(白・紙の上の大きな数字)/gold-text #6f5a32(紙・砂の上の小さな文字)。紙色の上にgoldの文字は置かない(2.1:1で読めない)

- 採用ページ(/recruit/)は本文・構造化データ・メール下書きにも「AI」「ドラマ」「架空」を出さない(build.pyの org_description / mail_service で切替)。お問い合わせ帯の文はページごとに front matter の contact_text
- 相談の窓口 = 代表 玉手志弥の公式LINE @217ombzj(build.py の LINE_URL・2026-10-20 志弥指示でフォームは作らずLINEへ。面談予約はLINEのあいさつ文から)
- **色(2026-10-19 志弥指示で変更)**: 「くすんで暗い」→ **アースグリーン #3f6f4a 1色＋白**のクリーンな配色に。濃い帯(理念・お問い合わせ以外)は廃止、薄い緑 #f4f8f3 の地＋白い箱。金・海色・紙色は使わない(変数名 --gold 等は互換のため残し、中身は緑)。上の「トンマナ」行の色指定とDesign Systemアーティファクトの色は旧版。書体は従来どおり

## コラム(記事)の足し方(2026-10-19〜)

1. `src/column/英数字のファイル名.md` を作る(ファイル名がURLになる → /column/ファイル名/)
2. 先頭に設定を書く:
   ```
   ---
   title: 記事の題名(検索結果に出る)
   description: 80〜120字の要約(検索結果・一覧に出る)
   date: 2026-10-19
   category: recruit   ← recruit=採用・求人 / drama=ショートドラマ・動画 / general=SNS・動画運用
   updated: (書き直したら日付)
   draft: true          ← 書きかけは true で非公開
   ---
   ```
3. 本文: `## 見出し`(目次に自動で出る) / `### 小見出し` / `- 箇条書き` / `1. 番号` / `**太字**` / `[文字](URL)`
4. 「SOIの考え方」の囲み: 行頭を `> ` にする。1行目を `> **SOIの考え方**` にすると見出しになる
5. `python3 build.py --check` → 一覧・トップ・サービスページの新着欄・sitemap・llms.txt に自動で載る
- 書き方の約束: 一般論＋「SOIの考え方」(自社の実際のやり方)。統計・事例・数値成果は出典か実物がない限り書かない。recruit の記事に「AI」「ドラマ」「架空」は書かない(点検でNGになる)
- **採用ページの写真(2026-10-19 志弥指示「取り急ぎAIで」)**: `assets/recruit/*.jpg` は Higgsfield gpt_image_2_5 で生成したイメージ写真(実在の職場・人物ではない)。ページ上は「※写真はイメージです」「撮影のイメージ」と表記(採用ページなので「AI」とは書かない)。実際の撮影写真が手に入ったら差し替える
- **IndexNow**(Bing・ChatGPT検索などへの更新通知): 鍵ファイル=ルートの `<鍵>.txt`(鍵は `.indexnow_key`)。ページを足したら `python3 build.py --indexnow` で全URLを通知
