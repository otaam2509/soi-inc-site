(() => {
  const root = document.querySelector('.journal-archive');
  if (!root) return;
  const form = root.querySelector('.journal-tools');
  const input = root.querySelector('#journal-search');
  const buttons = [...root.querySelectorAll('.journal-filters button')];
  const cards = [...root.querySelectorAll('.journal-card')];
  const result = root.querySelector('#journal-result-count');
  const empty = root.querySelector('.journal-empty');
  const clear = root.querySelector('.journal-clear');
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ja').trim();
  const texts = cards.map(card => normalize(card.dataset.search));
  let category = 'all';

  function filter() {
    const terms = normalize(input.value).split(/\s+/).filter(Boolean);
    let count = 0;
    cards.forEach((card, index) => {
      const visible = (category === 'all' || card.dataset.category === category)
        && terms.every(term => texts[index].includes(term));
      card.hidden = !visible;
      if (visible) count += 1;
    });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === category)));
    result.textContent = category === 'all' && terms.length === 0
      ? `全${count}記事` : `${cards.length}記事中 ${count}記事を表示`;
    empty.hidden = count !== 0;
    clear.hidden = input.value.length === 0;
  }

  buttons.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.category;
    filter();
  }));
  input.addEventListener('input', filter);
  form.addEventListener('submit', event => { event.preventDefault(); filter(); });
  clear.addEventListener('click', () => { input.value = ''; filter(); input.focus(); });
  empty.querySelector('button').addEventListener('click', () => {
    category = 'all';
    input.value = '';
    filter();
    buttons[0].focus();
  });
  form.hidden = false;
})();
