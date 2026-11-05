/* Skylbot — navegación, catálogo y demostración local de Discord.
   Referencias de estructura: main.py, other_commands.py, juegos/* y vicio/*.
   No contacta con la API de Skylbot ni usa sus tokens. */
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
  mobile?.addEventListener('click', event => {
    if (event.target.closest('a')) setMenu(false);
  });
  window.addEventListener('resize', () => {
    if (window.innerWidth > 780) setMenu(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') setMenu(false);
  });

  const notice = document.getElementById('notice');
  let noticeTimer;
  const notify = message => {
    if (!notice) return;
    notice.textContent = message;
    notice.hidden = false;
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => { notice.hidden = true; }, 3300);
  };
  document.querySelectorAll('[data-invite-disabled]').forEach(link => {
    link.addEventListener('click', () => notify('La invitación estará disponible al configurar el ID de la aplicación Discord.'));
  });
  document.addEventListener('click', async event => {
    const button = event.target.closest('[data-copy]');
    if (!button) return;
    const value = button.dataset.copy;
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(value);
      const before = button.textContent;
      button.textContent = tr('Copiado');
      notify(`Copiado: ${value}`);
      setTimeout(() => { button.textContent = before; }, 1400);
    } catch { notify(`Copia manualmente: ${value}`); }
  });

  const tr = value => window.SkylbotI18n?.tr(value) ?? value;
  const language = () => window.SkylbotI18n?.locale ?? 'es';
  const items = [...document.querySelectorAll('[data-command-item]')];
  const search = document.getElementById('command-search');
  const filters = [...document.querySelectorAll('[data-command-category]')];
  const count = document.getElementById('command-count');
  const empty = document.getElementById('no-command-results');
  const params = new URLSearchParams(location.search);
  const available = filters.map(item => item.dataset.commandCategory);
  let category = available.includes(params.get('categoria')) ? params.get('categoria') : 'Todos';
  const normalize = value => String(value).toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  function applyFilter() {
    const phrase = normalize(search?.value || '').trim();
    let shown = 0;
    for (const item of items) {
      const matches = (category === 'Todos' || item.dataset.category === category) && (!phrase || normalize(item.textContent).includes(phrase));
      item.hidden = !matches;
      if (matches) shown++;
    }
    if (count) count.textContent = `${shown} ${language()==='zh'?'条指令':language()==='en'?(shown===1?'command':'commands'):(shown===1?'comando':'comandos')}`;
    if (empty) empty.hidden = shown !== 0;
    filters.forEach(button => {
      const selected = button.dataset.commandCategory === category;
      button.classList.toggle('is-active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
  }
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.commandCategory;
    const url = new URL(location.href);
    if (category === 'Todos') url.searchParams.delete('categoria');
    else url.searchParams.set('categoria', category);
    history.replaceState(null, '', url);
    applyFilter();
  }));
  search?.addEventListener('input', applyFilter);
  if (items.length) applyFilter();
  document.addEventListener('skylbot:languagechange', () => { if(items.length) applyFilter(); });

  const feed = document.getElementById('demo-transcript');
  const controls = document.getElementById('demo-game-controls');
  const legacyChoice = document.getElementById('demo-choice-controls');
  if (!feed || !controls) return;

  // La URL del script sirve para localizar assets propios aun si la web vive en /Skylbot/web/.
  // Ningún enlace de HTML/CSS/JS depende de la raíz / del dominio.
  const SCRIPT_URL = document.currentScript?.src || new URL('assets/js/main.js', document.baseURI).href;
  const WEB_ROOT = new URL('../../', SCRIPT_URL);
  const localAsset = path => new URL(`assets/discord/${path}`, WEB_ROOT).href;
  // Reutilización literal de recursos de Skylbot, sin copiarlos ni alterarlos.
  // Si se ejecuta web/scripts/sync-assets.py, se usarán las copias locales.
  const RAW = 'https://raw.githubusercontent.com/nestx0/Skylbot/main/assets/';
  const assets = {
    dealer: 'Duala_dealer.webp',
    roulette_red: 'roulette/roulette_red.webp',
    roulette_black: 'roulette/roulette_black.webp',
    roulette_green: 'roulette/roulette_green.webp'
  };
  const cardPool = {
    Common: [
      {name:'Apple Cat',file:'characters/apple_cat.webp',desc:'Just chilling, he likes apples',stats:{HP:10,ATK:2,DEF:3,SPE:1,LCK:4}},
      {name:'Blub Cat',file:'characters/blub_cat.webp',desc:'Doesn\'t care what you think',stats:{HP:10,ATK:2,DEF:3,SPE:4,LCK:1}},
      {name:'Smiling Cat',file:'characters/smile_cat.webp',desc:'Just happy to be out there',stats:{HP:11,ATK:1,DEF:4,SPE:2,LCK:3}},
      {name:'Miguel',file:'characters/miguel.webp',desc:'My pana Miguel',stats:{HP:9,ATK:4,DEF:2,SPE:2,LCK:2}}
    ],
    Uncommon: [
      {name:'Maxwell',file:'characters/maxwell_cat.webp',desc:'Please do not bend',stats:{HP:14,ATK:3,DEF:7,SPE:2,LCK:1}},
      {name:'Big Floppa',file:'characters/big_floppa.webp',desc:'The OG big cat of the internet',stats:{HP:17,ATK:5,DEF:5,SPE:4,LCK:1}},
      {name:'Tiny Cat',file:'characters/tiny_cat.webp',desc:'Not smaller than a microbio tho',stats:{HP:13,ATK:3,DEF:1,SPE:10,LCK:1}}
    ],
    Rare: [
      {name:'Beluga Cat',file:'characters/beluga_cat.webp',desc:'Lord of Discord',stats:{HP:22,ATK:5,DEF:6,SPE:4,LCK:11}},
      {name:'Suspicious Cat',file:'characters/sus_cat.webp',desc:'He is sceptical about everything',stats:{HP:20,ATK:10,DEF:6,SPE:7,LCK:3}}
    ],
    Epic: [
      {name:'Counter-Terrorist Cat',file:'characters/cs_cat.webp',desc:'His skills came from playing CS2 all day long',stats:{HP:35,ATK:10,DEF:15,SPE:8,LCK:10}},
      {name:'Floppa Whatsapp',file:'characters/floppa_whatsapp.webp',desc:'Evolved version of Floppa',stats:{HP:35,ATK:15,DEF:8,SPE:15,LCK:4}},
      {name:'Juan',file:'characters/juan.webp',desc:'Juan',stats:{HP:38,ATK:7,DEF:22,SPE:10,LCK:1}},
      {name:'Obscure Cat',file:'characters/obscure_cat.webp',desc:'It knows your deepest secrets',stats:{HP:35,ATK:24,DEF:10,SPE:10,LCK:2}}
    ]
  };
  const embedColors = {Common:'#747f8d',Uncommon:'#248046',Rare:'#f0a434',Epic:'#9b59b6'};
  const random = max => Math.floor(Math.random() * max);
  let balance = 3500;
  let game = null;
  let pptActive = false;
  let inventory = [];
  let invPage = 0;

  const node = (tag, className, value) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (value !== undefined) el.textContent = value;
    return el;
  };
  const appendText = (parent, tag, className, content) => parent.appendChild(node(tag,className,content));

  function imageFromRepo(path, className, alt) {
    const image = document.createElement('img');
    image.className = className;
    image.alt = alt;
    image.loading = 'lazy';
    image.decoding = 'async';
    const fallback = RAW + path;
    image.src = localAsset(path);
    image.onerror = () => {
      if (image.dataset.remote) {
        image.replaceWith(node('span','discord-image-fallback','Imagen de Skylbot no disponible temporalmente'));
        return;
      }
      image.dataset.remote = '1';
      image.src = fallback;
    };
    return image;
  }

  function embedCard({title,description='',fields=[],color='#5865f2',thumbnail=null,image=null,footer=null}) {
    const outer = node('div','discord-embed');
    outer.style.setProperty('--embed-color',color);
    const body = node('div','discord-embed-content');
    if (title) appendText(body,'div','discord-embed-title',title);
    if (description) appendText(body,'p','discord-embed-description',description);
    if (fields.length) {
      const fieldGrid = node('div','discord-embed-fields');
      for (const f of fields) {
        const div = node('div',`discord-embed-field${f.inline===false?' full':''}`);
        appendText(div,'strong','discord-embed-field-title',f.name);
        appendText(div,'span','discord-embed-field-value',String(f.value));
        fieldGrid.appendChild(div);
      }
      body.appendChild(fieldGrid);
    }
    if (thumbnail) body.appendChild(imageFromRepo(thumbnail,'discord-embed-thumbnail',title||'Miniatura del juego'));
    if (image) body.appendChild(imageFromRepo(image,'discord-embed-image',title||'Personaje de Skylbot'));
    if (footer) appendText(body,'div','discord-embed-footer',footer);
    outer.appendChild(body);
    return outer;
  }
  function updateMessageEmbed(article, embed, buttons = null) {
    const wrap = article.querySelector('.discord-message-content');
    if (!wrap) return;
    wrap.querySelectorAll('.discord-embed, .discord-button-row').forEach(element => element.remove());
    wrap.appendChild(embedCard(embed));
    if (buttons) wrap.appendChild(buttonRow(buttons));
    feed.scrollTop = feed.scrollHeight;
  }
  function buttonRow(buttons) {
    const row = node('div','discord-button-row');
    for (const {label,emoji='',style='primary',onClick,disabled=false} of buttons) {
      const button=node('button',`discord-action discord-action-${style}`,`${emoji ? emoji+' ' : ''}${label}`);
      button.type='button';
      button.disabled=disabled;
      button.addEventListener('click',onClick);
      row.appendChild(button);
    }
    return row;
  }

  function message(author, content='', {isBot=false,embed=null,buttons=null}={}) {
    const article = node('article','discord-message');
    const avatar = isBot ? document.createElement('img') : node('span','chat-avatar','T');
    if (isBot) {
      avatar.className='chat-avatar bot-avatar';
      avatar.src=new URL('assets/img/skylbot-avatar.webp', WEB_ROOT).href;
      avatar.width=38; avatar.height=38; avatar.alt='Avatar de Skylbot';
    }
    const wrap=node('div','discord-message-content');
    const header=node('div',`chat-author${isBot?'':' user-author'}`,author);
    if(isBot) header.appendChild(node('span','app-tag','BOT'));
    wrap.appendChild(header);
    if(content) appendText(wrap,'p','discord-message-text',content);
    if(embed) wrap.appendChild(embedCard(embed));
    if(buttons) wrap.appendChild(buttonRow(buttons));
    article.append(avatar,wrap);
    feed.appendChild(article);
    feed.scrollTop=feed.scrollHeight;
    return article;
  }
  const bot=(content,opts={})=>message('Skylbot',content,{isBot:true,...opts});
  const player=command=>message(tr('Tú'),command);

  // Baraja, as de 11/1 y puntuación de Python juegos/blackjack/game.py.
  const deck = () => {
    const result=[];
    for (const suit of ['♥️','♦️','♣️','♠️']) for (const value of ['2','3','4','5','6','7','8','9','10','J','Q','K','A']) result.push({suit,value});
    for(let i=result.length-1;i>0;i--){const j=random(i+1);[result[i],result[j]]=[result[j],result[i]];}
    return result;
  };
  const points = hand => {
    let value=0,aces=0;
    hand.forEach(card => {
      if(card.value==='A'){value+=11;aces++;}
      else if(['J','Q','K'].includes(card.value)) value+=10;
      else value+=Number(card.value);
    });
    while(value>21 && aces>0){value-=10;aces--;}
    return value;
  };
  const cards = hand => hand.map(card=>card.value+card.suit).join(' ');
  function blackjackEmbed(finished=false){
    const playerPoints=points(game.player);
    const dealerPoints=points(game.dealer);
    return {
      title:'🃏 Blackjack 🃏',color:finished?'#344a80':'#2ecc71',thumbnail:assets.dealer,
      fields:[
        {name:'Your Hand',value:`${cards(game.player)} (${playerPoints})`,inline:false},
        {name:"Dealer's Hand",value:finished?`${cards(game.dealer)} (${dealerPoints})`:`${cards(game.dealer.slice(0,1))} ? (${game.dealer[0].value})`,inline:false}
      ],
      footer:finished?(game.win?'You Won! 🃏':'You Lost! 🃏'):'Try Hitting'
    };
  }
  function endBlackjack({hitBust=false}={}) {
    if(!game)return;
    if(!hitBust) while(points(game.dealer)<17)game.dealer.push(game.deck.pop());
    const yours=points(game.player), theirs=points(game.dealer);
    game.win=!hitBust && yours<=21 && (theirs>21 || yours>=theirs);
    // El bot devuelve la apuesta duplicada en caso de victoria al plantarse.
    balance+=game.win?200:0;
    updateMessageEmbed(game.message,blackjackEmbed(true));
    game=null;
  }
  function startBlackjack(){
    if(game || pptActive){bot('Finish the current game first.');return;}
    if(balance<100){bot('❌ Not enough balance.');return;}
    balance-=100;
    const pack=deck();
    game={deck:pack,player:[pack.pop(),pack.pop()],dealer:[pack.pop(),pack.pop()],win:false,message:null};
    const viewButtons=[
      {label:'Hit',style:'success',onClick:()=>{
        if(!game)return;
        game.player.push(game.deck.pop());
        if(points(game.player)>21) endBlackjack({hitBust:true});
        else if(points(game.player)===21) endBlackjack();
        else updateMessageEmbed(game.message,blackjackEmbed(),viewButtons);
      }},
      {label:'Stand',style:'danger',onClick:()=>endBlackjack()}
    ];
    game.message=bot('',{embed:blackjackEmbed(),buttons:viewButtons});
    if(points(game.player)===21)endBlackjack();
  }

  // Python roulette.py: los colores se corresponden con la tabla original.
  const REDS=new Set([1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]);
  function roulette(choice){
    if(game||pptActive){bot('Finish the current game first.');return;}
    if(balance<100){bot('❌ Not enough balance.');return;}
    const result=random(37);
    const color=result===0?'green':REDS.has(result)?'red':'black';
    const won=color===choice;
    const payout=won?200:0;
    balance=balance-100+payout;
    const symbol={red:'🔴',black:'⚫',green:'🟢'}[color];
    bot('',{embed:{
      title:'Roulette',description:`Number: ${result} ${symbol}\n${won?'You won '+payout+' bolivares!':'Better luck next time!'}`,
      color:{red:'#e74c3c',black:'#2b2d31',green:'#2ecc71'}[color],
      fields:[{name:'Bet',value:'100 bolivares'},{name:'Balance',value:`${balance} bolivares`}],
      thumbnail:assets[`roulette_${color}`]
    }});
  }

  // Python ppt.py: empate recupera la apuesta, victoria devuelve el doble.
  const pptOptions={Rock:'🪨',Paper:'📄',Scissors:'✂️'};
  const winAgainst={Rock:'Scissors',Paper:'Rock',Scissors:'Paper'};
  function startPpt(){
    if(game||pptActive){bot('Finish the current game first.');return;}
    if(balance<100){bot('❌ Not enough balance.');return;}
    balance-=100;
    pptActive=true;
    const choices=Object.keys(pptOptions).map(option=>({
      label:option,emoji:pptOptions[option],style:'primary',onClick:()=>{
        if(!pptActive)return;
        const opponent=Object.keys(pptOptions)[random(3)];
        const draw=option===opponent;
        const win=winAgainst[option]===opponent;
        const payout=draw?100:win?200:0;
        balance+=payout;
        pptActive=false;
        updateMessageEmbed(msg,{
          title:'Rock, Paper, Scissors — Results',
          description:`You: ${pptOptions[option]} ${option}\nBot: ${pptOptions[opponent]} ${opponent}\n\n${draw?'Draw! Your bet has been refunded':win?'You won!':'You lost!'} — you receive ${payout} bolivars.`,
          color:draw?'#5865f2':win?'#2ecc71':'#5865f2'
        });
      }
    }));
    const msg=bot('',{embed:{title:'Rock, Paper, Scissors',description:'Choose your move · Bet: 100 bolivars',color:'#5865f2'},buttons:choices});
  }

  const sellBase={Common:500,Uncommon:2000,Rare:7000,Epic:15000};
  const sellValue=char=>Math.round(sellBase[char.rarity]*char.level/0.8);
  function gacha(){
    if(balance<3000){bot('To pull a character, you need 3000 bolivares');return;}
    balance-=3000;
    const roll=random(101);
    const rarity=roll<=60?'Common':roll<=85?'Uncommon':roll<=95?'Rare':'Epic';
    const list=cardPool[rarity];
    const chosen=list[random(list.length)];
    let char=inventory.find(x=>x.name===chosen.name);
    if(char){char.level++;bot(`♻️ Repeated! You already had a ${char.name}. It leveled up to ${char.level}! ⬆️`);}
    else{char={...chosen,rarity,level:1,stats:{...chosen.stats}};inventory.push(char);bot(`✨ Congrats! You got a new ${char.name} (${char.rarity}) 🙀`);}
    bot('',{embed:{title:char.name,description:`${char.name}\n${char.desc}\n${char.rarity}`,color:embedColors[char.rarity],image:char.file}});
  }
  function inventoryEmbed(char){
    const fields=[{name:'Rarity',value:char.rarity},{name:'Sell Value',value:String(sellValue(char))},
      ...Object.entries(char.stats).map(([name,value])=>({name,value:String(value)})),{name:'LVL',value:String(char.level)}];
    return {title:`🎒 Inventory: ${char.name}`,description:char.desc,color:'#f1c40f',image:char.file,fields,footer:`Page ${invPage+1} out of ${inventory.length}`};
  }
  function showInventory(){
    if(!inventory.length){bot('No inventory to show');return;}
    invPage=Math.min(invPage,inventory.length-1);
    const msg=bot('',{embed:inventoryEmbed(inventory[invPage])});
    function render(){
      const prev={label:'◀ Previous',style:'primary',disabled:invPage===0,onClick:()=>{if(invPage>0){invPage--;render();}}};
      const next={label:'Next ▶',style:'primary',disabled:invPage>=inventory.length-1,onClick:()=>{if(invPage<inventory.length-1){invPage++;render();}}};
      updateMessageEmbed(msg,inventoryEmbed(inventory[invPage]),[prev,next]);
    }
    render();
  }
  function guide(){
    const groups=[
      [tr('Utilidades'),['guide','ping','poll','joke']],
      [tr('Economía'),['work','pay','balance','leaderboard','mine','buyRole']],
      [tr('Juegos'),['blackjack','jackblack','roulette','ppt']],
      [tr('Colección'),['lootbox','inventory','boss','combat','setDefender','pull','sell','train']],
      [tr('IA'),['ai','clear']],
      [tr('Plantas'),['shop','plantinv','water','sellplant']]
    ];
    const description=groups.map(([name,list])=>`${name}\n${list.map(command=>`• ${command}`).join('  ')}`).join('\n\n');
    bot('',{embed:{title:'Commands',description,color:'#2ecc71'}});
  }
  function resetDemo(){
    balance=3500;inventory=[];game=null;pptActive=false;invPage=0;
    feed.replaceChildren();controls.hidden=true;if(legacyChoice)legacyChoice.hidden=true;
    bot(tr('Demo reiniciada. Elige un comando para probar Skylbot.'));
  }
  const commands={guide,balance:()=>bot(`Your current balance is ${balance}${balance===0?', you\'re broke':''}`),
    work:()=>{const reward=350+random(151);balance+=reward;bot(`You've earned ${reward}, your balance is ${balance}`);},
    blackjack:startBlackjack,'roulette-red':()=>roulette('red'),'roulette-black':()=>roulette('black'),
    ppt:startPpt,pull:gacha,inventory:showInventory};
  const display={blackjack:'*blackjack 100','roulette-red':'*roulette 100 red','roulette-black':'*roulette 100 black',ppt:'*ppt 100'};
  document.querySelectorAll('[data-demo-command]').forEach(button=>{
    button.addEventListener('click',()=>{
      const key=button.dataset.demoCommand;
      if(!(key in commands))return;
      player(display[key]||'*'+key);
      commands[key]();
    });
  });
  // Los controles antiguos permanecen ocultos; los botones ahora aparecen donde Discord los muestra: en el mensaje.
  controls.hidden=true;if(legacyChoice)legacyChoice.hidden=true;
  document.getElementById('reset-demo')?.addEventListener('click',resetDemo);
})();
