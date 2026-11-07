// Measure an intent to contact separately from an inquiry actually received.
// Do not send message text, email addresses, or link query strings to Analytics.
(function () {
  'use strict';
  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href]');
    if (!link || typeof window.gtag !== 'function') return;
    var url;
    try { url = new URL(link.href, location.href); } catch (_) { return; }
    var method = null;
    if (url.protocol === 'mailto:') method = 'mail';
    else if (url.hostname === 'lin.ee' || url.hostname === 'line.me') method = 'line';
    else if (url.origin === location.origin && url.pathname === '/contact/' && location.pathname !== '/contact/') method = 'form';
    else if (url.hostname === 'ig.me' && url.pathname === '/m/tsuimiru_aimovie') method = 'instagram_dm';
    else if (link.hasAttribute('data-track') && link.getAttribute('data-track') === 'instagram_profile') method = 'instagram_profile';
    if (method) {
      var contact = {method: method, page_path: location.pathname};
      var service = link.getAttribute('data-contact-service');
      if (service === 'recruit' || service === 'tsuimiru') contact.service = service;
      window.gtag('event', 'contact_click', contact);
      return;
    }
    if (url.origin !== location.origin || url.pathname === location.pathname) return;
    var type = /^\/column\/.+/.test(url.pathname) ? 'article' : /^\/(recruit|short-drama|tsuimiru)\//.test(url.pathname) ? 'service' : null;
    if (type) window.gtag('event', 'select_content', {content_type: type, item_id: url.pathname, source_path: location.pathname});
  });
})();
