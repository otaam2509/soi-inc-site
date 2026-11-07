// /contact/ の申込フォーム。回答はGoogleフォームへ送り、きっかけに合わせたお礼を出して予約画面へ進める。
// 入力項目を変えたら、Googleフォーム側の質問と ENTRY の番号を合わせること。
(function () {
  'use strict';
  var FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSdLMGcgFvHBGszuEwAXt-NO2ouqQD_14MZYSgEeA2KTv1QbDg/formResponse';
  // 申し込みをChatworkへ知らせる受け口(../SOI問い合わせ通知)
  var NOTIFY_URL = 'https://soi-contact-notify.vercel.app/api/notify';
  var ENTRY = {
    source: 'entry.1949914588', detail: 'entry.1366008236', service: 'entry.289968959', email: 'entry.1123148034',
    name: 'entry.2047311551', linename: 'entry.1940385811', company: 'entry.172176752', message: 'entry.752150822', url: 'entry.1015494649'
  };
  var BOOKING = {
    recruit: 'https://timerex.net/s/otama2509_3ae3/721d36be',
    tsuimiru: 'https://timerex.net/s/otama2509_3ae3/2b3057e4',
    line: 'https://timerex.net/s/otama2509_3ae3/2b3057e4',
    undecided: 'https://timerex.net/s/otama2509_3ae3/721d36be'
  };
  var DETAIL_LABEL = {
    'ホリエモンチャンネル': 'ご覧になった感想やご相談のきっかけ', 'YouTube': 'ご覧になった動画やチャンネル', 'Instagram': 'ご覧になった投稿やアカウント', 'TikTok': 'ご覧になった動画やアカウント',
    'X(旧Twitter)': 'ご覧になった投稿やアカウント', 'Google検索・ホームページ': '検索した言葉やご覧になったページ',
    'ChatGPTなどのAI': '使ったAIや聞いた内容', 'ご紹介': 'ご紹介者のお名前', 'メール・DM・お手紙': '届いた内容', 'その他': 'くわしく教えてください'
  };
  var THANKS = {
    'ホリエモンチャンネル': 'ホリエモンチャンネルをご覧いただき、ありがとうございます。',
    'YouTube': 'YouTubeをご覧いただき、ありがとうございます。', 'Instagram': 'Instagramをご覧いただき、ありがとうございます。',
    'TikTok': 'TikTokをご覧いただき、ありがとうございます。', 'X(旧Twitter)': 'Xをご覧いただき、ありがとうございます。',
    'Google検索・ホームページ': 'ホームページをご覧いただき、ありがとうございます。', 'ChatGPTなどのAI': 'SOIを見つけていただき、ありがとうございます。',
    'ご紹介': 'ご紹介でのお問い合わせ、ありがとうございます。', 'メール・DM・お手紙': 'ご連絡をお読みいただき、ありがとうございます。', 'その他': 'SOIを見つけていただき、ありがとうございます。'
  };
  var form = document.getElementById('apply-form');
  if (!form) return;
  var btn = document.querySelector('nav .links a.btn');
  if (btn) btn.setAttribute('href', '#apply');

  function checked(name) { return form.querySelector('input[name="' + name + '"]:checked'); }
  function val(name) { var el = form.elements[name]; return el ? (el.value || '').trim() : ''; }
  function setError(box, on) { var e = box.querySelector('.err'); if (e) e.hidden = !on; box.classList.toggle('has-error', on); }

  var q = new URLSearchParams(location.search);
  var pre = form.querySelector('input[name="service"][data-key="' + q.get('service') + '"]');
  if (pre) pre.checked = true;

  form.addEventListener('change', function (ev) {
    if (ev.target.name === 'source') {
      setError(document.getElementById('f-source'), false);
      document.getElementById('f-detail').hidden = false;
      document.getElementById('detail-label').textContent = DETAIL_LABEL[ev.target.value] || 'くわしく教えてください';
    }
    if (ev.target.name === 'service') setError(document.getElementById('f-service'), false);
  });

  function validate() {
    var checks = [
      ['f-source', !!checked('source')], ['f-service', !!checked('service')], ['f-name', !!val('name')],
      ['f-contact', /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val('email'))], ['f-message', !!val('message')]
    ];
    var first = null;
    checks.forEach(function (c) {
      var box = document.getElementById(c[0]);
      setError(box, !c[1]);
      if (!c[1] && !first) first = box;
    });
    if (first) { first.scrollIntoView({block: 'center'}); return false; }
    return true;
  }

  function showThanks(source, serviceKey) {
    form.hidden = true;
    var box = document.getElementById('apply-thanks');
    var url = BOOKING[serviceKey] || BOOKING.undecided;
    document.getElementById('thanks-title').textContent = THANKS[source] || 'ありがとうございます。';
    document.getElementById('thanks-book').href = url;
    box.hidden = false;
    box.focus();
    box.scrollIntoView({block: 'center'});
    var left = 8, auto = document.getElementById('thanks-auto');
    (function tick() {
      auto.textContent = left + '秒後に、日程を選ぶ画面へ移動します。';
      if (left-- <= 0) { location.href = url; return; }
      setTimeout(tick, 1000);
    })();
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (!validate()) return;
    var submit = form.querySelector('.apply-submit'), fail = document.getElementById('submit-error');
    var sourceInput = checked('source'), serviceInput = checked('service');
    var body = new URLSearchParams();
    body.set(ENTRY.source, sourceInput.value);
    body.set(ENTRY.service, serviceInput.value);
    body.set(ENTRY.name, val('name'));
    body.set(ENTRY.linename, val('linename') || '未記入');
    body.set(ENTRY.message, val('message'));
    ['detail', 'email', 'company', 'url'].forEach(function (k) { if (val(k)) body.set(ENTRY[k], val(k)); });
    var notice = {source: sourceInput.value, service: serviceInput.value};
    ['detail', 'name', 'company', 'email', 'linename', 'message', 'url'].forEach(function (k) { notice[k] = val(k); });
    submit.disabled = true;
    fail.hidden = true;
    submit.textContent = '送信しています…';
    // no-cors なので応答の中身は読めない。通信自体が失敗したときだけ catch に入る。
    fetch(FORM_URL, {method: 'POST', mode: 'no-cors', body: body}).then(function () {
      // 通知の失敗で申し込みを止めない。回答はGoogleフォームに残っている。
      fetch(NOTIFY_URL, {method: 'POST', headers: {'Content-Type': 'text/plain'}, body: JSON.stringify(notice), keepalive: true}).catch(function () {});
      if (typeof window.gtag === 'function') window.gtag('event', 'inquiry_submit', {source: sourceInput.value, service: serviceInput.getAttribute('data-key')});
      showThanks(sourceInput.value, serviceInput.getAttribute('data-key'));
    }).catch(function () {
      submit.disabled = false;
      submit.textContent = '送信して日程を選ぶ';
      fail.hidden = false;
    });
  });
})();
