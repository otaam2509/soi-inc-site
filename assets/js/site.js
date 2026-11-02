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
