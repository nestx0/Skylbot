(() => {
  'use strict';
  const toggle = document.getElementById('menu-toggle');
  const mobile = document.getElementById('mobile-nav');
  const setMenu = open => {
    if (!toggle || !mobile) return;
    mobile.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
  };
  toggle?.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  mobile?.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });
  window.addEventListener('resize', () => { if (window.innerWidth > 780) setMenu(false); });

  const notice = document.getElementById('notice');
  let noticeTimer;
  const notify = message => {
    if (!notice) return;
    notice.textContent = message;
    notice.hidden = false;
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => { notice.hidden = true; }, 3300);
  };
  document.querySelectorAll('[data-invite-disabled]').forEach(a => a.addEventListener('click', () => notify('Falta configurar el ID de la aplicación de Discord para activar la invitación.')));
  document.addEventListener('click', async e => {
    const button = e.target.closest('[data-copy]');
    if (!button) return;
    const command = button.dataset.copy;
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw Error('Clipboard unavailable');
      await navigator.clipboard.writeText(command);
      const old = button.textContent;
      button.textContent = 'Copiado';
      notify('Copiado: ' + command);
      setTimeout(() => { button.textContent = old; }, 1600);
    } catch { notify('Puedes copiar este comando: ' + command); }
  });

  /* Searchable reference: all entries exist as real HTML, even without JavaScript. */
  const items = [...document.querySelectorAll('[data-command-item]')];
  const query = document.getElementById('command-search');
  const filters = [...document.querySelectorAll('[data-command-category]')];
  const count = document.getElementById('command-count');
  const empty = document.getElementById('no-command-results');
  const params = new URLSearchParams(window.location.search);
  const available = filters.map(button => button.dataset.commandCategory);
  let activeCategory = available.includes(params.get('categoria')) ? params.get('categoria') : 'Todos';
  const normalize = text => String(text).toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const applyFilter = () => {
    const phrase = normalize(query?.value || '').trim();
    let shown = 0;
    items.forEach(item => {
      const match = (activeCategory === 'Todos' || item.dataset.category === activeCategory) && (!phrase || normalize(item.textContent).includes(phrase));
      item.hidden = !match;
      if (match) shown++;
    });
    if (count) count.textContent = `${shown} ${shown === 1 ? 'comando' : 'comandos'}`;
    if (empty) empty.hidden = shown !== 0;
    filters.forEach(b => {
      const selected = b.dataset.commandCategory === activeCategory;
      b.classList.toggle('is-active', selected);
      b.setAttribute('aria-pressed', String(selected));
    });
  };
  filters.forEach(b => b.addEventListener('click', () => {
    activeCategory = b.dataset.commandCategory;
    const url = new URL(window.location.href);
    if (activeCategory === 'Todos') url.searchParams.delete('categoria');
    else url.searchParams.set('categoria', activeCategory);
    window.history.replaceState(null, '', url);
    applyFilter();
  }));
  query?.addEventListener('input', applyFilter);
  if (items.length) applyFilter();

  /* Purposeful local sandbox for commands present in the Python bot.
     No network access, no real Discord events, no account data. */
  const feed = document.getElementById('demo-transcript');
  const gameControls = document.getElementById('demo-game-controls');
  const pptControls = document.getElementById('demo-choice-controls');
  if (!feed || !gameControls) return;
  let balance = 3500;
  let pendingPpt = false;
  let inventory = [];
  let game = null;
  const random = max => Math.floor(Math.random() * max);
  const reset = () => {
    balance = 3500;
    game = null;
    pendingPpt = false;
    inventory = [];
    if (pptControls) pptControls.hidden = true;
    gameControls.hidden = true;
    feed.replaceChildren();
    addMessage('Skylbot', 'Demostración reiniciada. Elige un comando para empezar.', true);
  };
  function addMessage(author, message, isBot = false, box = false) {
    const article = document.createElement('div');
    article.className = 'discord-message';
    const avatar = document.createElement('span');
    avatar.className = 'chat-avatar ' + (isBot ? 'bot-avatar' : '');
    avatar.textContent = isBot ? 'S' : 'T';
    const textWrap = document.createElement('div');
    const heading = document.createElement('div');
    heading.className = 'chat-author' + (isBot ? '' : ' user-author');
    heading.append(document.createTextNode(author));
    if (isBot) {
      const badge = document.createElement('span');
      badge.className = 'app-tag';
      badge.textContent = 'BOT';
      heading.append(badge);
    }
    const content = document.createElement(box ? 'div' : 'p');
    if (box) content.className = 'reply-box';
    content.textContent = message;
    textWrap.append(heading, content);
    article.append(avatar, textWrap);
    feed.append(article);
    feed.scrollTop = feed.scrollHeight;
  }
  function makeDeck() {
    const deck = [];
    for (const suit of ['♠', '♥', '♦', '♣']) for (const value of ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']) deck.push({suit, value});
    for (let i = deck.length - 1; i > 0; i--) {
      const j = random(i + 1);
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
  }
  const handValue = hand => {
    let total = 0;
    let aces = 0;
    for (const card of hand) {
      if (card.value === 'A') { total += 11; aces++; }
      else total += ['K', 'Q', 'J'].includes(card.value) ? 10 : Number(card.value);
    }
    while (total > 21 && aces) { total -= 10; aces--; }
    return total;
  };
  const showCards = hand => hand.map(({value, suit}) => `${value}${suit}`).join('  ');
  function startBlackjack() {
    if (game) { addMessage('Skylbot', 'Termina primero la partida actual.', true); return; }
    if (balance < 100) { addMessage('Skylbot', 'Necesitas 100 puntos. Usa *work para obtener más.', true); return; }
    balance -= 100;
    const deck = makeDeck();
    game = { deck, player: [deck.pop(), deck.pop()], dealer: [deck.pop(), deck.pop()] };
    addMessage('Skylbot', `Blackjack · apuesta de 100 puntos\nTus cartas: ${showCards(game.player)} (${handValue(game.player)})\nBanca: ${game.dealer[0].value}${game.dealer[0].suit}  ?\nElige «Pedir carta» o «Plantarse».`, true, true);
    gameControls.hidden = false;
    if (handValue(game.player) === 21) finishBlackjack('blackjack');
  }
  function finishBlackjack(reason) {
    if (!game) return;
    const {deck, player, dealer} = game;
    if (reason !== 'bust' && reason !== 'blackjack') while (handValue(dealer) < 17) dealer.push(deck.pop());
    const playerValue = handValue(player);
    const dealerValue = handValue(dealer);
    const win = reason === 'blackjack' || (playerValue <= 21 && (dealerValue > 21 || playerValue > dealerValue));
    const tie = playerValue <= 21 && playerValue === dealerValue && reason !== 'blackjack';
    const payoff = win ? 200 : tie ? 100 : 0;
    balance += payoff;
    game = null;
    gameControls.hidden = true;
    addMessage('Skylbot', `Resultado · ${win ? '¡Has ganado!' : tie ? 'Empate' : 'Has perdido'}\nTu mano: ${showCards(player)} (${playerValue})\nBanca: ${showCards(dealer)} (${dealerValue})\nSaldo de prueba: ${balance} puntos.`, true, true);
  }
  document.querySelectorAll('[data-demo-command]').forEach(button => button.addEventListener('click', () => {
    const command = button.dataset.demoCommand;
    const shownCommand = command === 'blackjack' ? '*blackjack 100' : command === 'ppt' ? '*ppt 100' : command.startsWith('roulette-') ? `*roulette 100 ${command.slice(9)}` : `*${command}`;
    addMessage('Tú', shownCommand);
    if (command === 'guide') addMessage('Skylbot', 'Comandos disponibles en esta demo:\n*guide  ·  *balance  ·  *work  ·  *blackjack 100\nPara la lista completa del bot, visita la página Comandos.', true, true);
    if (command === 'balance') addMessage('Skylbot', `Tu saldo de prueba es de ${balance} puntos.`, true);
    if (command === 'work') {
      const reward = 350 + random(151);
      balance += reward;
      addMessage('Skylbot', `Has ganado ${reward} puntos. Tu saldo de prueba es de ${balance}.`, true);
    }
    if (command === 'blackjack') startBlackjack();
    if (command.startsWith('roulette-')) {
      if (game || pendingPpt) { addMessage('Skylbot', 'Termina la partida actual antes de empezar otra.', true); return; }
      if (balance < 100) { addMessage('Skylbot', 'Saldo insuficiente para apostar 100.', true); return; }
      const bet = command.slice('roulette-'.length);
      const n = random(37);
      const reds = new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]);
      const color = n === 0 ? 'green' : reds.has(n) ? 'red' : 'black';
      const win = bet === color;
      balance += win ? 100 : -100;
      addMessage('Skylbot', `Ruleta · ${n} (${color}). ${win ? '¡Ganaste 100 puntos!' : 'Perdiste 100 puntos.'} Saldo: ${balance}.`, true, true);
    }
    if (command === 'ppt') {
      if (game || pendingPpt) { addMessage('Skylbot', 'Termina primero la partida actual.', true); return; }
      if (balance < 100) { addMessage('Skylbot', 'Saldo insuficiente para apostar 100.', true); return; }
      balance -= 100;
      pendingPpt = true;
      if (pptControls) pptControls.hidden = false;
      addMessage('Skylbot', 'Piedra, papel o tijera · apuesta de 100 puntos. Elige tu jugada.', true);
    }
    if (command === 'pull') {
      if (balance < 3000) { addMessage('Skylbot', 'Necesitas 3000 bolívares para obtener un personaje.', true); return; }
      balance -= 3000;
      // Se replica el reparto de rarezas de vicio/gacha.py (aleatorio entero 0-100).
      const rarityRoll = random(101);
      const rarity = rarityRoll <= 60 ? 'Common' : rarityRoll <= 85 ? 'Uncommon' : rarityRoll <= 95 ? 'Rare' : 'Epic';
      const examples = { Common: ['Apple Cat','Blub Cat','Miguel','Smiling Cat'], Uncommon: ['Maxwell','Big Floppa','Tiny Cat'], Rare: ['Beluga Cat','Suspicious Cat'], Epic: ['Counter-Terrorist Cat', 'Floppa Whatsapp', 'Juan', 'Obscure Cat'] };
      const name = examples[rarity][random(examples[rarity].length)];
      const previous = inventory.find(item => item.name === name);
      if (previous) previous.level++;
      else inventory.push({name, rarity, level: 1});
      addMessage('Skylbot', `Gacha · ${name} (${rarity}). ${previous ? 'Repetido: subió de nivel.' : 'Nuevo en tu colección.'} Saldo: ${balance}.`, true, true);
    }
    if (command === 'inventory') {
      addMessage('Skylbot', inventory.length ? inventory.map((x,i) => `${i+1}. ${x.name} · ${x.rarity} · nivel ${x.level}`).join('\n') : 'Tu colección de prueba está vacía. Usa *pull para conseguir un personaje.', true, true);
    }
  }));
  document.getElementById('demo-hit')?.addEventListener('click', () => {
    if (!game) return;
    game.player.push(game.deck.pop());
    const value = handValue(game.player);
    addMessage('Skylbot', `Has pedido carta: ${showCards(game.player)} (${value}).`, true);
    if (value >= 21) finishBlackjack(value > 21 ? 'bust' : 'stand');
  });
  document.getElementById('demo-stand')?.addEventListener('click', () => finishBlackjack('stand'));
  document.querySelectorAll('[data-ppt-choice]').forEach(button => button.addEventListener('click', () => {
    if (!pendingPpt) return;
    const mine = button.dataset.pptChoice;
    const options = ['Rock','Paper','Scissors'];
    const other = options[random(options.length)];
    const win = {Rock:'Scissors', Paper:'Rock', Scissors:'Paper'}[mine] === other;
    const draw = mine === other;
    balance += draw ? 100 : win ? 200 : 0;
    pendingPpt = false;
    if (pptControls) pptControls.hidden = true;
    addMessage('Tú', `Elección: ${mine}`);
    addMessage('Skylbot', `Piedra, papel o tijera: tú ${mine}, bot ${other}. ${draw ? 'Empate, apuesta devuelta.' : win ? '¡Ganaste!' : 'Has perdido.'} Saldo: ${balance}.`, true, true);
  }));
  document.getElementById('reset-demo')?.addEventListener('click', reset);
})();
