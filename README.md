# 株式会社SOI 会社サイト

## 現在のデザイン（2026-11-03）

- ユーザーの「ヒロメルと同じように」刷新する依頼に基づき、黒地・太いゴシック体・色面・写真を重ねた構成へ変更。下記の旧配色・旧書体ルールより、この項目を優先する。
- SOIはライムグリーンと紫。共通の見た目は `assets/css/creative-20261103.css`、トップ本文は `src/pages/index.html`、メニューは `src/layout.html`。
- ツイミルはコーラルと紫。見た目は `assets/tsuimiru/creative-20261103.css`、本文は `src/standalone/tsuimiru.html`。既存の4作品をトップ直下で紹介する。
- 共通の文字帯・装飾の停止は `assets/js/creative-20261103.js`。OSの「視差効果を減らす」設定も尊重する。ツイミルの制作サンプル動画はユーザー操作で再生する。
- SOIの下層ページにも書体・配色・ヘッダーを適用。記事本文、制作サンプルの注記、各サービスの相談窓口、予約導線、計測は維持。
- 今後も `src/` と `assets/` を編集し、`python3 build.py --check` で生成HTMLを更新する。

- 公開先: https://soi-co-ltd.com/ （2026-10-19取得・Squarespace Domains。GitHub otaam2509/soi-inc-site の main を GitHub Pages で配信・`CNAME`ファイルで独自ドメイン化。旧URL otaam2509.github.io/soi-inc-site/ は自動で転送）
- 連絡先: info@soi-co-ltd.com
- 構成(2026-10-19 複数ページ化): **本文は `src/`、見た目・動作は `assets/`、組み立て処理は `build.py` を編集**。`python3 build.py --check` で公開用HTMLを書き出し＋点検(リンク切れ・alt・h1・構造化データ)。書き出したファイル(index.html・recruit/・short-drama/・company/・privacy/・404.html・sitemap.xml)もコミットする(GitHub Pagesはそのまま配信)
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
- 採用支援の相談窓口 = 代表 玉手志弥の公式LINE @217ombzj(build.py の LINE_URL・2026-10-20 志弥指示でフォームは作らずLINEへ。面談予約はLINEのあいさつ文から)
- **色(2026-10-19 志弥指示で変更)**: 「くすんで暗い」→ **アースグリーン #3f6f4a 1色＋白**のクリーンな配色に。濃い帯(理念・お問い合わせ以外)は廃止、薄い緑 #f4f8f3 の地＋白い箱。金・海色・紙色は使わない(変数名 --gold 等は互換のため残し、中身は緑)。上の「トンマナ」行の色指定とDesign Systemアーティファクトの色は旧版。書体は従来どおり

## 申込の動線（2026-11-07・11-08更新）

**2026-11-08 志弥指示: サイトのボタンは公式LINEに誘導しない。全ボタン→ /contact/（アンケート）→ 送信後そのまま TimeRex 予約。** 連絡先はメールアドレス必須（LINE表示名欄は撤去・Googleフォームには「未記入」で入る）。公式LINE2本のあいさつは、LINEから来た人向けにそのまま残している。


- 志弥指示: 公式LINEの流入を自動で申込・予約まで進める。問い合わせには「当社を知ったきっかけ」を必須にし、見た媒体へのお礼につなげる。10/20の「フォームは作らない」はこの指示で置き換え。
- 流れ: 公式LINEのあいさつ → `/contact/` → 送信 → きっかけ別のお礼を表示 → 8秒後にTimeRexへ自動移動（採用=721d36be・ツイミル=2b3057e4）。`?service=recruit|tsuimiru` で相談サービスを選択済みにできる。
- 本文 `src/pages/contact.html`、処理 `assets/js/contact-20261107.js`、見た目 `assets/css/contact-20261107.css`。回答の保存先はGoogleフォーム「ツイミル｜動画制作の相談・お見積もり申込」（info@soi-co-ltd.com・編集ID 1tnoPvcnSWH5NBBDL4L439mNybl4OgNc0mFitqpN29dI・Chromeでは u/3）。回答はメール通知でinfo@へ届く。
- 回答の一覧はスプレッドシート「株式会社SOI 問い合わせ一覧」(1L6Sat5bm305IbrfDcKyCP2WOUebt_w8RCF5c7XoJ7h8・info@所有)。Chatwork通知は `../SOI問い合わせ通知/`(Vercel関数)。LINEのあいさつは「玉手志弥」「ツイミル」の両方から /contact/ へ案内。
- **Googleフォームの質問や選択肢を変えたら、`contact-20261107.js` の ENTRY と HTML の value を必ず合わせる**（ずれると送信が記録されない）。no-corsで応答を読めないので、変更後は実際に1件送って回答に届くか確認する。

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
- 書き方の約束（2026-11-03更新）: [CONTENT_GUIDE.md](CONTENT_GUIDE.md) を先に読む。自社の制作物・作業・判断・検証を記事の中心にし、一般論は理解に必要な分だけ添える。根拠が足りない経験談は取材企画として残す。統計・事例・数値成果は出典か実物がない限り書かない。recruit の記事に「AI」「ドラマ」「架空」は書かない(点検でNGになる)
- **採用ページの写真(2026-10-19 志弥指示「取り急ぎAIで」)**: `assets/recruit/*.jpg` は Higgsfield gpt_image_2_5 で生成したイメージ写真(実在の職場・人物ではない)。ページ上は「※写真はイメージです」「撮影のイメージ」と表記(採用ページなので「AI」とは書かない)。実際の撮影写真が手に入ったら差し替える
- **IndexNow**(Bing・ChatGPT検索などへの更新通知): 鍵ファイル=ルートの `<鍵>.txt`(鍵は `.indexnow_key`)。ページを足したら `python3 build.py --indexnow` で全URLを通知

## ツイミル専用LP（2026-10-22）

- 公開URL: https://soi-co-ltd.com/tsuimiru/
- 本文: `src/standalone/tsuimiru.html`。独自デザインの完結したHTMLを格納し、`build.py` が `tsuimiru/index.html` を書き出してサイトマップ・点検に含める。
- CSS/JS・画像・動画: `assets/tsuimiru/`。ツイミルの相談先は公式LINE（https://lin.ee/SC6LK06）→申込フォーム（https://forms.gle/fdM71sJyKk7cqgmX9）→30分のTimeRex予約（https://timerex.net/s/otama2509_3ae3/2b3057e4）→Google Meet。予約確認・前日のリマインドはメール。会社サイト共通のLINEとは別に管理する。
- 画像・動画はSOI側で配信（2026-11-02）。元のSites配信には依存しない。会社ドメイン版とSites版のHTMLは独立しているため、このURLを主導線とし、修正はこのリポジトリに反映する。
- 左端の動画はユーザー指定「確認用_B案.MP4」から作成した `wedding-story-b.mp4`（55秒）。他3本も会社名を除いた制作サンプル。ウェディング業務の営業ページではなく、動画表現の制作サンプルとして掲載。
- 共通メニュー・会社トップ・ `/short-drama/` から導線を設置。会社トップにはロゴ・制作サンプル動画を埋め込んだ紹介セクションを設置。LP末尾に運営会社とプライバシーポリシーへのリンク。
- 検索向け設定: LPのタイトル・説明・H1にサービス名とAI動画制作を明示。canonicalはSOIドメイン版、WebPage/Service/BreadcrumbList構造化データを設定。更新時はfront matterの `updated` を変更し、sitemapの実際の更新日を保つ。


## SEO調査レポートへの対応（2026-11-02）

- `/recruit/` は「SNS採用代行」、`/recruit/video/` は「採用動画制作」、`/recruit/kaigo/` は介護施設向けの撮影・SNS支援を説明。RPO全般をSOIの提供サービスとして表記しない。
- 比較検討向けに `recruit-sns-agency`、`care-rpo-or-sns`、`short-drama-production-company` の3記事を追加。コラム一覧のテーマ別入口と関連リンクから案内。
- 全記事に「執筆・編集：株式会社SOI」と編集方針へのリンクを表示。代表紹介を添えるが、本人の執筆・監修は確認できる場合のみ明記する。
- ツイミル、ショートドラマページと該当カテゴリの記事はツイミルの公式LINEへ案内する。採用支援のLINEと混同しない。
- GA4は既存プロパティを利用し、ツイミルにも同じ計測を追加。`assets/js/measurement.js` の `contact_click` は窓口リンクのクリック、`select_content` は記事・サービスへの移動。メッセージ本文やリンクのクエリ文字列をイベントに送らない。
- 旧 `generate_lead` のクリック計測は廃止。`contact_click` を受信済み問い合わせと数えない。実際のDM・LINE・メールの相談、商談、契約は受信記録で別集計する。GA4上の既存 `generate_lead` 履歴との単純な前後比較はしない。
- スクリプト・CSSのキャッシュ更新用番号は内容のハッシュを使い、同日の再公開にも対応。
- 検索順位・AI引用・問い合わせ数は保証しない。実績や被リンクは確認済みの掲載許可・関係先に基づいて増やす。
