// 制作例の動画: 画面に入ったら無音で再生、外れたら停止(通信量を抑える)
(function(){
  if(!("IntersectionObserver" in window)) return;
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    var v=e.target;
    if(e.isIntersecting){ if(v.preload==="none"){v.preload="auto";} var p=v.play(); if(p&&p.catch)p.catch(function(){}); }
    else { v.pause(); }
  });},{threshold:.5});
  document.querySelectorAll("video[data-autoplay-inview]").forEach(function(v){ io.observe(v); });
})();

// 問い合わせボタンのクリックをGoogleアナリティクスに記録(LINE/メール別)
document.addEventListener("click",function(e){
  var a=e.target.closest&&e.target.closest("a[data-track], a[href^='mailto:'], a[href*='line.me'], a[href*='lin.ee']");
  if(!a||typeof gtag!=="function") return;
  var kind=a.getAttribute("data-track")||(a.href.indexOf("mailto:")===0?"mail":"line");
  gtag("event","generate_lead",{method:kind,page_path:location.pathname});
});
