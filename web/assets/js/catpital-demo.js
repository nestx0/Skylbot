/* Catpital · demostración local. No usa red, cuentas ni API de Catpital.
   Nombres y precios iniciales: apps/server/prisma/seed/markets.json.
   Se limita a operaciones spot para no simular incorrectamente el motor de riesgo real. */
(() => {
  'use strict';
  const root = document.querySelector('[data-catpital-demo]');
  if (!root) return;
  const $ = id => root.querySelector(`#${id}`);
  const tr = source => window.SkylbotI18n?.tr(source) ?? source;
  const L = (es,en,zh) => (window.SkylbotI18n?.locale==='en'?en:window.SkylbotI18n?.locale==='zh'?zh:es);
  const numberLocale = () => ({es:'es-ES',en:'en-US',zh:'zh-CN'}[window.SkylbotI18n?.locale] || 'es-ES');
  const config = {
    MEOW: {name:'Miau Tecnologías', emoji:'🐱', base:100, tick:0.01, fee:0.0006, volatility:0.012, digits:2},
    FIH: {name:'Pescaditos Secos Holding', emoji:'🐟', base:42, tick:0.01, fee:0.001, volatility:0.017, digits:2}
  };
  const markets = Object.keys(config);
  const initialCash = 10000;
  const money = value => new Intl.NumberFormat(numberLocale(), {minimumFractionDigits:2, maximumFractionDigits:2}).format(value);
  const format = (value, digits=2) => new Intl.NumberFormat(numberLocale(), {minimumFractionDigits:digits, maximumFractionDigits:digits}).format(value);
  const qtyText = value => new Intl.NumberFormat(numberLocale(), {maximumFractionDigits:6}).format(value);
  let cash, holdings, series, selected, side, rngSeed, feedback = '';

  function random() { // Reproducible al reiniciar, no representa precios reales.
    rngSeed = (Math.imul(1664525, rngSeed) + 1013904223) >>> 0;
    return rngSeed / 4294967296;
  }
  function move(code, prior) {
    const m = config[code];
    const change = (random() - .5) * 2 * m.volatility;
    return Math.max(m.tick, Math.round((prior * (1 + change))/m.tick)*m.tick);
  }
  function resetState() {
    cash = initialCash; holdings = Object.fromEntries(markets.map(code => [code,{qty:0,cost:0}]));
    rngSeed = 41672026;
    series = Object.fromEntries(markets.map(code => {
      const points = [config[code].base];
      for (let i=0;i<42;i++) points.push(move(code, points.at(-1)));
      return [code, points];
    }));
    selected = 'MEOW'; side = 'buy'; feedback = '';
    $('cat-amount').value='500';
    render();
  }
  const priceOf = code => series[code].at(-1);
  function total() { return cash + markets.reduce((sum, code) => sum + holdings[code].qty * priceOf(code), 0); }
  function amounts() {
    const amount = Number($('cat-amount').value);
    const m=config[selected], price=priceOf(selected);
    const valid=Number.isFinite(amount) && amount>=10 && amount<=1e8;
    return {amount,price,fee:amount*m.fee,units:amount/price,valid};
  }
  function updateFeedback(text, error=false) {
    feedback=text;
    const el=$('cat-order-status'); el.textContent=text;
    el.classList.toggle('is-error',error); el.classList.toggle('is-success',!error&&!!text);
  }
  function render() {
    const market=config[selected], price=priceOf(selected);
    $('cat-market-name').textContent=tr(market.name);
    $('cat-price').textContent=format(price,market.digits);
    const change=100*(price/market.base-1);
    const badge=$('cat-change');badge.textContent=`${change>=0?'+':''}${format(change,2)} %`;
    badge.classList.toggle('cat-up',change>=0);badge.classList.toggle('cat-down',change<0);
    $('cat-cash').textContent=`${money(cash)} MC`;
    root.querySelectorAll('[data-cat-market]').forEach(btn=>{
      const active=btn.dataset.catMarket===selected;btn.classList.toggle('is-active',active);btn.setAttribute('aria-pressed',String(active));
    });
    root.querySelectorAll('[data-cat-side]').forEach(btn=>{
      const active=btn.dataset.catSide===side;btn.classList.toggle('is-active',active);btn.setAttribute('aria-pressed',String(active));
    });
    const a=amounts();
    $('cat-order-price').textContent=`${format(a.price,market.digits)} MC`;
    $('cat-order-units').textContent=a.valid ? qtyText(a.units) : '—';
    $('cat-order-fee').textContent=a.valid ? `${money(a.fee)} MC` : '—';
    const submit=$('cat-order-submit');
    submit.textContent=`${tr(side==='buy'?'Comprar':'Vender')} ${selected}`;
    submit.classList.toggle('cat-buy-button',side==='buy');
    submit.classList.toggle('cat-sell-button',side==='sell');
    submit.disabled=!a.valid;
    const totalEl=$('cat-portfolio-value');totalEl.textContent=`${money(total())} MC`;
    renderHoldings();drawChart();
  }
  function renderHoldings() {
    const out=$('cat-holdings');out.replaceChildren();
    const entries=markets.filter(code=>holdings[code].qty>1e-8);
    if(!entries.length){const el=document.createElement('p');el.className='cat-empty-portfolio';el.textContent=tr('Aún no tienes posiciones. Elige un mercado y simula una compra.');out.append(el);return;}
    const columns=document.createElement('div');columns.className='cat-position-rows';
    for(const code of entries){
      const h=holdings[code],now=priceOf(code),positionValue=h.qty*now, pnl=positionValue-h.cost;
      const row=document.createElement('div');row.className='cat-position-row';
      const name=document.createElement('strong');name.textContent=`${config[code].emoji} ${code}`;
      const info=document.createElement('span');info.textContent=`${qtyText(h.qty)} ${L('uds.','units','单位')} · ${money(positionValue)} MC`;
      const delta=document.createElement('span');delta.className=pnl>=0?'cat-up':'cat-down';delta.textContent=`${pnl>=0?'+':''}${money(pnl)} MC`;
      row.append(name,info,delta);columns.append(row);
    }
    out.append(columns);
  }
  function drawChart(){
    const canvas=$('cat-chart');if(!canvas)return;
    const ctx=canvas.getContext('2d');if(!ctx)return;
    const rect=canvas.getBoundingClientRect();
    const w=Math.max(280,rect.width || 500),h=Math.max(210,rect.height || 250);
    const dpr=Math.min(window.devicePixelRatio||1,2);
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.clearRect(0,0,w,h);
    const nums=series[selected],min=Math.min(...nums),max=Math.max(...nums),spread=Math.max(0.01,max-min);
    const pad={left:10,right:58,top:16,bottom:28},innerW=w-pad.left-pad.right,innerH=h-pad.top-pad.bottom;
    const px=i=>pad.left + (i/(nums.length-1))*innerW;
    const py=v=>pad.top+innerH-(v-(min-spread*.12))/(spread*1.24)*innerH;
    ctx.lineWidth=1;ctx.strokeStyle='#393254';
    for(let i=0;i<4;i++){
      const y=pad.top+(innerH/3)*i;
      ctx.beginPath();ctx.moveTo(pad.left,y);ctx.lineTo(w-pad.right+8,y);ctx.stroke();
      ctx.fillStyle='#a4a0bb';ctx.textAlign='right';ctx.font='11px system-ui';
      const value=(max+spread*.12)-(spread*1.24)*(i/3);
      ctx.fillText(format(value,config[selected].digits),w-5,y+4);
    }
    const rising=nums.at(-1)>=nums[0],lineColor=rising?'#3ddc97':'#ff5c7a';
    const fill=ctx.createLinearGradient(0,pad.top,0,h-pad.bottom);fill.addColorStop(0,rising?'rgba(61,220,151,.25)':'rgba(255,92,122,.24)');fill.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();nums.forEach((v,i)=>i?ctx.lineTo(px(i),py(v)):ctx.moveTo(px(i),py(v)));
    ctx.lineTo(px(nums.length-1),h-pad.bottom);ctx.lineTo(px(0),h-pad.bottom);ctx.closePath();ctx.fillStyle=fill;ctx.fill();
    ctx.beginPath();nums.forEach((v,i)=>i?ctx.lineTo(px(i),py(v)):ctx.moveTo(px(i),py(v)));
    ctx.lineWidth=2.4;ctx.lineJoin='round';ctx.strokeStyle=lineColor;ctx.stroke();
    ctx.beginPath();ctx.arc(px(nums.length-1),py(nums.at(-1)),4.5,0,Math.PI*2);ctx.fillStyle=lineColor;ctx.fill();
    ctx.fillStyle='#a4a0bb';ctx.font='11px system-ui';ctx.textAlign='left';ctx.fillText(tr('Hace 42 pasos'),pad.left,h-4);ctx.textAlign='right';ctx.fillText(tr('Ahora'),w-pad.right,h-4);
    canvas.setAttribute('aria-label',L(`Evolución ficticia de ${selected}, desde ${format(nums[0],config[selected].digits)} hasta ${format(nums.at(-1),config[selected].digits)} monedas`,`Simulated ${selected} trend, from ${format(nums[0],config[selected].digits)} to ${format(nums.at(-1),config[selected].digits)} coins`,`虚构的 ${selected} 价格走势，从 ${format(nums[0],config[selected].digits)} 到 ${format(nums.at(-1),config[selected].digits)} 币`));
  }
  function submitOrder(){
    const {amount,price,fee,units,valid}=amounts();
    if(!valid){updateFeedback(tr('Introduce un importe de al menos 10 MC.'),true);return;}
    const h=holdings[selected];
    if(side==='buy'){
      if(cash+1e-8<amount+fee){updateFeedback(tr('No tienes saldo suficiente para esa compra y su comisión.'),true);return;}
      cash-=amount+fee;h.qty+=units;h.cost+=amount+fee;
      updateFeedback(L(`Compra simulada: +${qtyText(units)} ${selected} por ${money(amount+fee)} MC.`,`Simulated buy: +${qtyText(units)} ${selected} for ${money(amount+fee)} MC.`,`模拟买入：+${qtyText(units)} ${selected}，花费 ${money(amount+fee)} MC。`));
    }else{
      if(h.qty+1e-8<units){updateFeedback(L(`No tienes suficientes ${selected} para vender ese importe.`,`Not enough ${selected} to sell this amount.`,`你没有足够的 ${selected} 可以出售。`),true);return;}
      const ratio=Math.min(1,units/h.qty);
      h.cost*=1-ratio;h.qty=Math.max(0,h.qty-units);if(h.qty<1e-8){h.qty=0;h.cost=0;}
      cash+=amount-fee;
      updateFeedback(L(`Venta simulada: -${qtyText(units)} ${selected}. Recibes ${money(amount-fee)} MC.`,`Simulated sell: -${qtyText(units)} ${selected}. You receive ${money(amount-fee)} MC.`,`模拟卖出：-${qtyText(units)} ${selected}，获得 ${money(amount-fee)} MC。`));
    }
    render();
  }
  root.querySelectorAll('[data-cat-market]').forEach(btn=>btn.addEventListener('click',()=>{
    selected=btn.dataset.catMarket;updateFeedback('');render();
  }));
  root.querySelectorAll('[data-cat-side]').forEach(btn=>btn.addEventListener('click',()=>{
    side=btn.dataset.catSide;updateFeedback('');render();
  }));
  $('cat-amount').addEventListener('input',()=>{updateFeedback('');render();});
  $('cat-next-tick').addEventListener('click',()=>{
    markets.forEach(code=>{const s=series[code];s.push(move(code,s.at(-1)));s.shift();});
    render();
  });
  $('cat-order-submit').addEventListener('click',submitOrder);
  $('cat-reset').addEventListener('click',()=>{resetState();updateFeedback(tr('Cartera y mercados reiniciados.'));});
  if('ResizeObserver' in window){new ResizeObserver(()=>drawChart()).observe($('cat-chart'));}
  else window.addEventListener('resize',drawChart,{passive:true});
  document.addEventListener('skylbot:languagechange',()=>{ updateFeedback(''); render(); });
  resetState();
})();
