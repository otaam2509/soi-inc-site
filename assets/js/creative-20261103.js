(() => {
  const motionButton = document.querySelector('.creative-motion');
  motionButton?.addEventListener('click', () => {
    const paused = document.documentElement.classList.toggle('motion-paused');
    motionButton.setAttribute('aria-pressed', String(paused));
    motionButton.textContent = paused ? '動きを再開する' : '動きを止める';
  });

  const menuButton = document.querySelector('.soi-menu-toggle');
  const menu = document.querySelector('#soi-mobile-menu');
  if (!menuButton || !menu) return;
  function setMenu(open, restoreFocus = false) {
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    menu.hidden = !open;
    if (restoreFocus) menuButton.focus();
  }
  menuButton.addEventListener('click', () => setMenu(menu.hidden));
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !menu.hidden) setMenu(false, true);
  });
  window.matchMedia('(min-width:901px)').addEventListener('change', event => {
    if (event.matches) setMenu(false);
  });
})();
