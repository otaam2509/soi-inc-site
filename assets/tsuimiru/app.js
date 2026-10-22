(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const stories = {
    product: {category:'PRODUCT & SERVICE',title:'「これ、いいかも」の\nきっかけを。',description:'スペックだけでは伝わらない、使う時間や心地よさ。日常のワンシーンから、その商品を選ぶ理由を描きます。',image:'https://tsuimiru-studio.soiwedding2025.chatgpt.site/assets/grapefruit.png',alt:'グレープフルーツのドリンクを並べた商品表現のイメージ',position:'center',tags:['SNS広告','商品紹介','利用シーン'],dialogTitle:'いつもの午後に、ちいさな楽しみ。',lead:'飲料の紹介を想定した、短い広告の構成例。',sequence:[['目が向く一瞬','グラスに注いだ瞬間の泡、光、果実の色。まずは「おいしそう」を映像で。'],['使う時間を描く','仕事や家事の合間に、ひと息つく午後。暮らしの中での出番を伝えます。'],['魅力をひと言に','実際の商品の特徴を確かめ、覚えてほしい言葉と購入先へつなぎます。']]},
    person: {category:'PEOPLE & PERSONAL BRAND',title:'どんな人かまで、\n好きになる。',description:'何ができるかだけでなく、なぜそれを続けているのか。仕事への想いや人柄を、自然な言葉と場面で伝えます。',image:'https://tsuimiru-studio.soiwedding2025.chatgpt.site/assets/atelier.png',alt:'カップを持つ作り手の人柄を伝える映像のイメージ',position:'68% center',tags:['プロフィール','専門家・クリエイター','活動紹介'],dialogTitle:'その人の「大切にしていること」から。',lead:'作り手のプロフィール紹介を想定した構成例。',sequence:[['その人の言葉から','大切にしていることを、本人の言葉でひと言。活動の背景に興味をつくります。'],['仕事の手つきを映す','実際の作品や仕事の様子を通して、こだわりを具体的に見せます。'],['次の接点へ','プロフィールや活動ページへ案内。もっと知りたい人が進める入口をつくります。']]},
    company: {category:'COMPANY & TEAM',title:'会社の名前に、\n顔が見えてくる。',description:'そこで働く人、日々の工夫、大切にしている姿勢。会社やお店の空気が伝わる場面から、ブランドの信頼を積み重ねます。',image:'https://tsuimiru-studio.soiwedding2025.chatgpt.site/assets/atelier.png',alt:'人と仕事の場を通じて会社の空気を伝える映像のイメージ',position:'32% center',tags:['会社・店舗紹介','ブランドストーリー','仕事の風景'],dialogTitle:'日々の風景に、会社らしさがある。',lead:'小さな工房・お店のブランド紹介を想定した構成例。',sequence:[['いつもの場面を入口に','開店前の準備、道具を整える手元。日常の場面から会社を紹介します。'],['大切にする姿勢を伝える','スタッフの言葉や仕事の様子を使い、こだわりを具体的に描きます。'],['出会いにつなげる','誰に何を届けている会社かを整理し、店舗やサービスの案内へつなげます。']]}
  };
  let activeStory = 'product';
  const tabs = [...document.querySelectorAll('[data-story]')];
  function selectStory(key, focus = false) {
    const story = stories[key];
    if (!story) return;
    activeStory = key;
    tabs.forEach(tab => { const selected = tab.dataset.story === key; tab.setAttribute('aria-selected',String(selected)); tab.tabIndex = selected ? 0 : -1; if(selected && focus) tab.focus(); });
    $('#story-panel').setAttribute('aria-labelledby','tab-' + key);
    $('#story-category').textContent = story.category;
    $('#story-title').replaceChildren(...story.title.split('\n').flatMap((line,index) => index ? [document.createElement('br'),document.createTextNode(line)] : [document.createTextNode(line)]));
    $('#story-description').textContent = story.description;
    const photo = $('#story-photo'); photo.src = story.image; photo.alt = story.alt; photo.style.objectPosition = story.position;
    $('#story-tags').replaceChildren(...story.tags.map(text => {const span = document.createElement('span'); span.textContent = text; return span;}));
  }
  tabs.forEach((tab,index) => {
    tab.addEventListener('click',()=>selectStory(tab.dataset.story));
    tab.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(index+1)%tabs.length;if(event.key==='ArrowLeft')next=(index+tabs.length-1)%tabs.length;if(event.key==='Home')next=0;if(event.key==='End')next=tabs.length-1;if(next!==undefined){event.preventDefault();selectStory(tabs[next].dataset.story,true);}});
  });
  $('#story-detail').addEventListener('click',()=>{
    const story = stories[activeStory];
    $('#dialog-story-title').textContent = story.dialogTitle;
    $('#dialog-story-lead').textContent = story.lead;
    $('#story-sequence').replaceChildren(...story.sequence.map(([title,description],index)=>{const item=document.createElement('li');const number=document.createElement('span');number.className='sequence-number';number.textContent=String(index+1).padStart(2,'0');const content=document.createElement('div');const heading=document.createElement('strong');heading.textContent=title;const body=document.createElement('p');body.textContent=description;content.append(heading,body);item.append(number,content);return item;}));
    $('#story-dialog').showModal();
  });
  document.querySelectorAll('dialog').forEach(dialog=>{dialog.querySelector('.dialog-close').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',event=>{if(event.target===dialog){const bounds=dialog.getBoundingClientRect();if(event.clientX<bounds.left||event.clientX>bounds.right||event.clientY<bounds.top||event.clientY>bounds.bottom)dialog.close();}});dialog.querySelectorAll('[data-close-dialog]').forEach(link=>link.addEventListener('click',()=>dialog.close()));});
  $('[data-open-about]').addEventListener('click',()=>$('#about-dialog').showModal());
  const menuButton=$('.menu-toggle');
  menuButton.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));$('#main-nav').classList.toggle('is-open',open);});
  $('#main-nav').querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{menuButton.setAttribute('aria-expanded','false');$('#main-nav').classList.remove('is-open');}));
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&menuButton.getAttribute('aria-expanded')==='true'){menuButton.setAttribute('aria-expanded','false');$('#main-nav').classList.remove('is-open');menuButton.focus();}});
  const sampleVideos = [...document.querySelectorAll('.work-card video')];
  sampleVideos.forEach(video => video.addEventListener('play', () => sampleVideos.forEach(other => { if(other !== video) other.pause(); })));
  let lineUrl = null;
  try {const candidate=new URL(window.TSUIMIRU_CONFIG?.lineUrl || '');if(candidate.protocol==='https:' && (candidate.hostname==='lin.ee'||candidate.hostname==='line.me'||candidate.hostname==='page.line.me'))lineUrl=candidate.href;}catch{}
  document.querySelectorAll('[data-line-link]').forEach(link=>{if(lineUrl){link.href=lineUrl;link.target='_blank';link.rel='noopener noreferrer';}else{link.addEventListener('click',event=>{event.preventDefault();$('#contact-dialog').showModal();});}});
  if(lineUrl)$('[data-line-help]').textContent='LINEで、ご都合のよい時間にお送りください。';
})();
