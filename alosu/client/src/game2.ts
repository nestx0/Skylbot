/**
 * 🎨 Blackjack + 🚀 服务端实时同步 (Prank Version)
 * 特性：
 * 1. 所有数据完全从服务器读写，实时多人同步
 * 2. 😈 内置必输开关 (Modo Infierno)
 */

// --- 配置常量 ---
const CONFIG = {
    API_BASE: '/api/alosu',
    DISCORD_API: 'https://discord.com/api',
    REFRESH_INTERVAL: 3000,
    AUTO_REFRESH_TIMEOUT: 8000,
    SAVE_LOCK_TIMEOUT: 500,
    DEALER_DRAW_DELAY: 600,
    DEALER_RESULT_DELAY: 800,
    CARD_ANIMATION_DELAY: 100,
    FLIP_ANIMATION_DURATION: 600,
    CONFETTI_COUNT: 100,
    DECK_SIZE: 52,
    NATURAL_BJ_DELAY: 500,
    DEALER_MIN_SCORE: 18,

    // 😈 必输开关 (Interruptor de Derrota)
    // true = 开启整蛊 (Jugador 必输)
    // false = 正常游戏
    PRANK_MODE: false, 
} as const;

// --- 1. 类型定义 ---
type Suit = '♠' | '♥' | '♣' | '♦';
type Card = { suit: Suit; value: string; weight: number };
type GameState = 'betting' | 'playing' | 'gameover';

type PlayerProfile = {
    id: string;
    username: string;
    avatarUrl: string;
    score: number;
    isMe: boolean;
};

// --- 2. 样式注入 (保持不变) ---
const STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

  @keyframes gradient-bg {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  @keyframes slide-in {
    0% { transform: translateY(-50px) scale(0.8) rotateY(90deg); opacity: 0; }
    100% { transform: translateY(0) scale(1) rotateY(0deg); opacity: 1; }
  }
  @keyframes fade-in-right {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
  }

  .bj-container {
    font-family: 'Orbitron', sans-serif; 
    background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #2a0a2e);
    background-size: 400% 400%;
    animation: gradient-bg 15s ease infinite;
    color: white;
    height: 100vh;
    width: 100%;
    display: flex;
    flex-direction: row; 
    overflow: hidden;
    position: relative;
    letter-spacing: 1px; 
  }

  .game-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    height: 100%;
    position: relative;
    z-index: 10;
  }

  .leaderboard-section {
    width: 300px;
    background: rgba(0, 0, 0, 0.4);
    border-left: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    padding: 20px;
    display: flex;
    flex-direction: column;
    z-index: 20;
    box-shadow: -5px 0 15px rgba(0,0,0,0.5);
    height: 100vh; 
    box-sizing: border-box;
  }

  .lb-title {
    font-size: 1.5rem; color: #f1c40f; text-align: center; margin-bottom: 20px;
    text-shadow: 0 0 10px rgba(241, 196, 15, 0.5);
    border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 10px;
  }

  .player-list {
    list-style: none;
    padding: 0;
    margin: 0;
    flex: 1; 
    overflow-y: auto;
    min-height: 0;
    scrollbar-width: thin; 
    scrollbar-color: rgba(255,255,255,0.3) transparent;
  }

  .player-row {
    display: flex; align-items: center; padding: 10px; margin-bottom: 8px;
    background: rgba(255,255,255,0.05); border-radius: 8px;
    animation: fade-in-right 0.5s ease forwards; transition: all 0.3s;
    border: 1px solid transparent;
  }

  .player-row.is-me {
    background: rgba(46, 204, 113, 0.2); border: 1px solid #2ecc71;
    box-shadow: 0 0 10px rgba(46, 204, 113, 0.3);
  }

  .rank-num { font-size: 1.2rem; font-weight: bold; width: 30px; color: #aaa; }
  .rank-1 .rank-num { color: #f1c40f; text-shadow: 0 0 5px #f1c40f; }
  .rank-2 .rank-num { color: #bdc3c7; }
  .rank-3 .rank-num { color: #cd7f32; }

  .avatar { width: 32px; height: 32px; border-radius: 50%; margin-right: 10px; border: 2px solid rgba(255,255,255,0.2); }
  .p-name { flex: 1; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .p-score { font-weight: bold; color: #5865F2; }

  .hand-area { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 180px; width: 100%; }
  .cards-row { display: flex; justify-content: center; gap: 10px; margin-top: 10px; perspective: 1000px; }

  .card {
    width: 80px; height: 110px; background: white; border-radius: 8px;
    display: flex; flex-direction: column; justify-content: space-between; padding: 5px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5); color: #333; font-weight: bold; font-size: 1.2rem;
    animation: slide-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    position: relative; user-select: none; transition: transform 0.2s;
    font-family: 'Orbitron', sans-serif; font-weight: 900; 
  }
  .card:hover { transform: translateY(-10px) scale(1.05); z-index: 10; }
  .card.red { color: #e74c3c; }
  .card.black { color: #2c3e50; }
  .card-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 2.5rem; opacity: 0.2; }

  .score-bubble {
    background: rgba(0, 0, 0, 0.6); padding: 5px 15px; border-radius: 20px;
    margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(5px); box-shadow: 0 0 10px rgba(88, 101, 242, 0.5);
  }

  .controls { display: flex; gap: 20px; margin-bottom: 30px; z-index: 100; }
  .btn {
    padding: 15px 30px; border: none; border-radius: 50px; font-size: 1.2rem; font-weight: bold;
    cursor: pointer; text-transform: uppercase; letter-spacing: 1px; transition: all 0.2s;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3); font-family: 'Orbitron', sans-serif;
  }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(1); }
  .btn-hit { background: #2ecc71; color: white; box-shadow: 0 0 15px #2ecc71; }
  .btn-hit:active { transform: scale(0.95); }
  .btn-stand { background: #e74c3c; color: white; box-shadow: 0 0 15px #e74c3c; }
  .btn-stand:active { transform: scale(0.95); }
  .btn-reset { background: #f1c40f; color: #333; box-shadow: 0 0 15px #f1c40f; }

  .overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.7); display: flex; flex-direction: column;
    justify-content: center; align-items: center; z-index: 200; backdrop-filter: blur(3px);
  }
  .result-text { font-size: 3rem; margin-bottom: 20px; text-shadow: 0 0 20px rgba(255,255,255,0.8); font-weight: 900; }
  .hidden { display: none !important; }
  #confetti-canvas { position: absolute; top: 0; left: 0; pointer-events: none; z-index: 999; }
  @media (max-width: 800px) { .leaderboard-section { display: none; } }
`;

// --- 3. 游戏逻辑类 ---
class BlackjackGame {
    deck: Card[] = [];
    playerHand: Card[] = [];
    dealerHand: Card[] = [];
    gameState: GameState = 'betting';
    
    players: PlayerProfile[] = [];
    currentUserId: string = '';
    autoRefreshInterval: number | null = null;
    isSaving: boolean = false; // 🔒 锁：防止重复提交
    completedGames: number = 0;
    completedGamesLoaded: boolean = false;

    app: HTMLDivElement;
    accessToken: string;

    constructor(app: HTMLDivElement, token: string) {
        this.app = app;
        this.accessToken = token;
        
        this.initUI();
        this.loadUserData().then(() => {
            // 初始化完成后才开始游戏
            this.startNewGame();
        });
        
        // 🔄 自动刷新
        this.autoRefreshInterval = window.setInterval(() => {
            if (!this.isSaving) { 
                this.loadUserData();
            }
        }, CONFIG.REFRESH_INTERVAL);
    }

    async loadUserData() {
        try {
            // 1. 获取用户信息
            if (!this.currentUserId) {
                const response = await fetch(`${CONFIG.DISCORD_API}/users/@me`, {
                    headers: { Authorization: `Bearer ${this.accessToken}` }
                });
                if (response.ok) {
                    const currentUser = await response.json();
                    this.currentUserId = currentUser.id;
                    (this as any)._cachedUser = currentUser; 
                    if (!this.completedGamesLoaded) {
                        const stored = Number(localStorage.getItem(`bj_games_completed_${this.currentUserId}`));
                        this.completedGames = Number.isFinite(stored) ? stored : 0;
                        this.completedGamesLoaded = true;
                    }
                }
            }

            // 2. 从服务器获取排行榜
            const lbResponse = await fetch(`${CONFIG.API_BASE}/leaderboard`);
            if (!lbResponse.ok) throw new Error('Failed to fetch leaderboard');
            const serverLeaderboard = await lbResponse.json();

            // 🛠️ 关键修复：Race Condition Fix
            const localMe = this.players.find(p => p.isMe);
            
            this.players = serverLeaderboard.map((p: any) => {
                const isMe = p.userId === this.currentUserId;
                let score = p.score;

                // 如果本地分数比服务器高（说明还没同步完），保留本地分数
                if (isMe && localMe && localMe.score > score) {
                    score = localMe.score;
                }

                return {
                    id: p.userId,
                    username: p.username,
                    avatarUrl: p.avatarUrl,
                    score: score,
                    isMe: isMe
                };
            });

            // 3. 自动注册
            if (this.currentUserId && !this.players.find(p => p.isMe)) {
                await this.registerUserIfNeeded();
            }

            this.renderLeaderboard();

        } catch (e) {
            console.error("❌ User fetch error:", e);
        }
    }

    private async registerUserIfNeeded() {
        const user = (this as any)._cachedUser;
        if (!user) return;

        const avatar = user.avatar 
            ? `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png` 
            : `https://cdn.discordapp.com/embed/avatars/${parseInt(user.discriminator || '0') % 5}.png`;
        
        try {
            await fetch(`${CONFIG.API_BASE}/score`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userId: user.id,
                    username: user.username,
                    avatarUrl: avatar,
                    score: 0
                })
            });
        } catch (e) {
            console.error("❌ Registration failed:", e);
        }
    }

    async saveMyScore() {
        const me = this.players.find(p => p.isMe);
        if (me) {
            try {
                this.isSaving = true;
                await fetch(`${CONFIG.API_BASE}/score`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        userId: me.id,
                        username: me.username,
                        avatarUrl: me.avatarUrl,
                        score: me.score
                    })
                });
            } catch (e) {
                console.error("❌ Failed to save score:", e);
            } finally {
                this.isSaving = false;
                this.loadUserData();
            }
        }
    }

    initUI() {
        this.app.innerHTML = `
            <style>${STYLES}</style>
            <canvas id="confetti-canvas"></canvas>
            <div class="bj-container">
                <div class="game-section">
                    <div class="hand-area" id="dealer-area">
                        <div class="score-bubble">🤖 Dealer <span id="dealer-score">0</span></div>
                        <div class="cards-row" id="dealer-cards"></div>
                    </div>
                    <div style="opacity: 0.1; font-size: 5rem; pointer-events: none;">♠♥♣♦</div>
                    <div class="hand-area" id="player-area">
                        <div class="cards-row" id="player-cards"></div>
                        <div class="score-bubble" style="margin-top: 10px;">👤 You <span id="player-score">0</span></div>
                    </div>
                    <div class="controls" id="controls">
                        <button class="btn btn-hit" id="btn-hit">Hit</button>
                        <button class="btn btn-stand" id="btn-stand">Stand</button>
                    </div>
                    <div class="overlay hidden" id="result-overlay">
                        <h1 class="result-text" id="result-text">WINNER!</h1>
                        <button class="btn btn-reset" id="btn-reset">Next Hand</button>
                    </div>
                </div>
                <div class="leaderboard-section">
                    <div class="lb-title" style="display: flex; justify-content: center; align-items: center; gap: 10px;">
                        🏆 RANKING 
                        <button id="btn-refresh-lb" style="background: none; border: none; cursor: pointer; font-size: 1.2rem;" title="Refresh">🔄</button>
                    </div>
                    <ul class="player-list" id="lb-list"></ul>
                    <div style="margin-top: auto; font-size: 0.7rem; color: #666; text-align: center; padding-top: 10px;">
                        * Live Data
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
        this.setupCanvas();
    }

    private attachEventListeners() {
        const btnHit = document.getElementById('btn-hit');
        const btnStand = document.getElementById('btn-stand');
        const btnReset = document.getElementById('btn-reset');
        const btnRefreshLb = document.getElementById('btn-refresh-lb');

        if (btnHit) btnHit.addEventListener('click', () => this.hit());
        if (btnStand) btnStand.addEventListener('click', () => this.stand());
        if (btnReset) btnReset.addEventListener('click', () => this.startNewGame());
        if (btnRefreshLb) {
            btnRefreshLb.addEventListener('click', () => {
                btnRefreshLb.style.transform = 'rotate(360deg)';
                this.loadUserData();
                setTimeout(() => { btnRefreshLb.style.transform = 'none'; }, 500);
            });
        }
    }

    private setupCanvas() {
        const canvas = document.getElementById('confetti-canvas') as HTMLCanvasElement;
        if (canvas) {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
    }

    renderLeaderboard() {
        const listEl = document.getElementById('lb-list');
        if (!listEl) return;
        
        const sortedPlayers = [...this.players].sort((a, b) => b.score - a.score);
        const existingRows = listEl.querySelectorAll('.player-row');
        
        const needsFullRender = existingRows.length !== sortedPlayers.length ||
            Array.from(existingRows).some((row, idx) => {
                const currentId = (row as HTMLElement).dataset.userId;
                return currentId !== sortedPlayers[idx]?.id;
            });
        
        if (needsFullRender) {
            listEl.innerHTML = sortedPlayers.map((p, index) => `
                <li class="player-row ${p.isMe ? 'is-me' : ''} rank-${index + 1}" data-user-id="${p.id}">
                    <span class="rank-num">#${index + 1}</span>
                    <img src="${p.avatarUrl}" class="avatar" alt="av" />
                    <span class="p-name">${p.username}</span>
                    <span class="p-score">${p.score}</span>
                </li>
            `).join('');
        } else {
            const playerMap = new Map(sortedPlayers.map(p => [p.id, p]));
            Array.from(existingRows).forEach((row, idx) => {
                const userId = (row as HTMLElement).dataset.userId;
                if (!userId) return;
                const player = playerMap.get(userId);
                if (player) {
                    const rankEl = row.querySelector('.rank-num');
                    const scoreEl = row.querySelector('.p-score');
                    if (rankEl) rankEl.textContent = `#${idx + 1}`;
                    if (scoreEl) scoreEl.textContent = player.score.toString();
                    row.className = `player-row ${player.isMe ? 'is-me' : ''} rank-${idx + 1}`;
                }
            });
        }
    }

    async updateScore(points: number) {
        const me = this.players.find(p => p.isMe);
        if (me) {
            me.score += points; 
            this.renderLeaderboard(); 
            await this.saveMyScore(); 
        }
    }

    createDeck() {
        const suits: Suit[] = ['♠', '♥', '♣', '♦'];
        const values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
        this.deck = [];
        
        const getWeight = (val: string): number => {
            if (['J', 'Q', 'K'].includes(val)) return 10;
            if (val === 'A') return 11;
            return parseInt(val);
        };

        for (const suit of suits) {
            for (const value of values) {
                this.deck.push({ suit, value, weight: getWeight(value) });
            }
        }
        // Fisher-Yates Shuffle
        for (let i = this.deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            const cardI = this.deck[i];
            const cardJ = this.deck[j];
            if (cardI && cardJ) {
                this.deck[i] = cardJ;
                this.deck[j] = cardI;
            }
        }
    }

    // 🕵️‍♂️ 辅助方法：作弊抽牌
    // 从 Baraja (牌堆) 中强制找到特定点数的 Carta (牌)
    private cheatDraw(targetWeight: number): Card {
        const index = this.deck.findIndex(c => c.weight === targetWeight);
        if (index !== -1) {
            const card = this.deck.splice(index, 1)[0];
            if (card) {
                return card;
            }
        }
        // 如果实在找不到（基本不可能），就随便抽一张
        return this.deck.pop()!;
    }

    startNewGame() {
        this.gameState = 'playing';
        this.createDeck();
        
        // 发牌
        this.playerHand = [this.drawCard(), this.drawCard()];
        this.dealerHand = [this.drawCard(), this.drawCard()];
        
        const resultOverlay = document.getElementById('result-overlay');
        const controls = document.getElementById('controls');
        if (resultOverlay) resultOverlay.classList.add('hidden');
        if (controls) controls.classList.remove('hidden');
        
        const btnHit = document.getElementById('btn-hit') as HTMLButtonElement;
        const btnStand = document.getElementById('btn-stand') as HTMLButtonElement;
        if (btnHit) btnHit.disabled = false;
        if (btnStand) btnStand.disabled = false;

        this.updateUI(false);

        // 检查起手 BlackJack
        this.checkNaturalBlackjack();
    }

    checkNaturalBlackjack() {
        if (this.completedGames < 1) return;
        const pScore = this.getScore(this.playerHand);
        if (pScore === 21) {
            setTimeout(() => {
                this.endGame('BLACKJACK!! (+10)', true, 10);
            }, CONFIG.NATURAL_BJ_DELAY);
        }
    }

    drawCard(): Card { 
        if (this.deck.length === 0) this.createDeck(); 
        return this.deck.pop()!; 
    }

    getScore(hand: Card[]): number {
        let score = 0; let aces = 0;
        for (const card of hand) {
            score += card.weight;
            if (card.value === 'A') aces += 1;
        }
        while (score > 21 && aces > 0) { score -= 10; aces -= 1; }
        return score;
    }

    updateUI(showDealerFull: boolean) {
        const dCardsEl = document.getElementById('dealer-cards');
        const pCardsEl = document.getElementById('player-cards');
        if (!dCardsEl || !pCardsEl) return;
        
        const dFragment = document.createDocumentFragment();
        const pFragment = document.createDocumentFragment();
        
        this.playerHand.forEach((card, index) => {
            pFragment.appendChild(this.createCardEl(card, index * CONFIG.CARD_ANIMATION_DELAY));
        });
        
        this.dealerHand.forEach((card, index) => {
            if (!showDealerFull && index === 0) {
                dFragment.appendChild(this.createHiddenCardEl());
            } else {
                dFragment.appendChild(this.createCardEl(card, index * CONFIG.CARD_ANIMATION_DELAY));
            }
        });
        
        dCardsEl.innerHTML = '';
        pCardsEl.innerHTML = '';
        dCardsEl.appendChild(dFragment);
        pCardsEl.appendChild(pFragment);

        const playerScoreEl = document.getElementById('player-score');
        const dealerScoreEl = document.getElementById('dealer-score');
        
        if (playerScoreEl) playerScoreEl.textContent = this.getScore(this.playerHand).toString();
        if (dealerScoreEl) {
            dealerScoreEl.textContent = showDealerFull ? this.getScore(this.dealerHand).toString() : '?';
        }
    }

    private createHiddenCardEl(): HTMLDivElement {
        const el = document.createElement('div');
        el.className = 'card';
        el.style.background = `repeating-linear-gradient(45deg, #2c3e50, #2c3e50 10px, #34495e 10px, #34495e 20px)`;
        el.style.border = '2px solid white';
        return el;
    }

    createCardEl(card: Card, delay: number): HTMLDivElement {
        const el = document.createElement('div');
        const colorClass = (card.suit === '♥' || card.suit === '♦') ? 'red' : 'black';
        el.className = `card ${colorClass}`;
        el.style.animationDelay = `${delay}ms`;
        el.innerHTML = `
            <div style="align-self: flex-start;">${card.value}</div>
            <div class="card-center">${card.suit}</div>
            <div style="align-self: flex-end; transform: rotate(180deg);">${card.value}</div>
        `;
        return el;
    }

    // 🔥 修改后的 hit 方法：包含整蛊逻辑
    hit() {
        if (this.gameState !== 'playing') return;

        let newCard: Card;

        // 😈 Jugador 必死模式：如果分数 >= 12，强行发 10 点，直接送走
        if (CONFIG.PRANK_MODE && this.getScore(this.playerHand) >= 12) {
             console.log("😈 Modo Prank: Enviando al Jugador a la ruina...");
             newCard = this.cheatDraw(10); 
        } else {
             newCard = this.drawCard();
        }

        this.playerHand.push(newCard);
        this.updateUI(false);
        
        const score = this.getScore(this.playerHand);
        if (score > 21) {
            this.endGame('BUSTED! (-3)', false, -3);
        }
    }

    // 🔥 修改后的 stand 方法：Crupier (庄家) 精准控分
    async stand() {
        if (this.gameState !== 'playing') return;
        
        const btnHit = document.getElementById('btn-hit') as HTMLButtonElement;
        const btnStand = document.getElementById('btn-stand') as HTMLButtonElement;
        if (btnHit) btnHit.disabled = true;
        if (btnStand) btnStand.disabled = true;

        // 1️⃣ 翻开首张牌
        await this.flipDealerFirstCard();

        const playerScore = this.getScore(this.playerHand);

        // 2️⃣ Crupier 抽牌循环
        while (this.getScore(this.dealerHand) < CONFIG.DEALER_MIN_SCORE) {
            await new Promise(r => setTimeout(r, CONFIG.DEALER_DRAW_DELAY));
            
            let newCard: Card;
            const currentDealerScore = this.getScore(this.dealerHand);

            // 😈 整蛊逻辑：如果 Crupier 分数 <= Jugador，透视抽牌
            if (CONFIG.PRANK_MODE && currentDealerScore <= playerScore) {
                const diff = playerScore - currentDealerScore;
                
                // 尝试让 Crupier 赢 1 分 (diff + 1)
                let targetWeight = diff + 1;
                // 如果需要的点数大于11（不可能的牌），就抽最大的10点牌
                if (targetWeight > 11) targetWeight = 10; 
                
                console.log(`😈 Modo Prank: Crupier necesita ${targetWeight} para ganar.`);
                newCard = this.cheatDraw(targetWeight);
            } else {
                newCard = this.drawCard();
            }

            this.dealerHand.push(newCard);
            
            this.updateUI(true);
            const dScore = this.getScore(this.dealerHand);
            const scoreEl = document.getElementById('dealer-score');
            if (scoreEl) {
                scoreEl.style.transition = 'color 0.2s';
                scoreEl.style.color = dScore > 21 ? '#e74c3c' : '#5865F2';
                scoreEl.textContent = dScore.toString();
            }
            
            // 如果整蛊模式下 Crupier 已经赢了，且分数合法，直接停止折磨
            if (CONFIG.PRANK_MODE && dScore > playerScore && dScore <= 21) {
                break;
            }
        }

        // 3️⃣ 显示结果
        await new Promise(r => setTimeout(r, CONFIG.DEALER_RESULT_DELAY));
        this.checkWinner();
    }

    // 🎬 翻牌动画
    async flipDealerFirstCard() {
        const dCardsEl = document.getElementById('dealer-cards');
        if (!dCardsEl) return;
        
        const backCard = dCardsEl.querySelector('.card') as HTMLElement;
        
        if (backCard) {
            backCard.style.transition = `transform ${CONFIG.FLIP_ANIMATION_DURATION}ms ease-in-out`;
            backCard.style.transform = 'rotateY(180deg)';
            
            await new Promise(r => setTimeout(r, CONFIG.FLIP_ANIMATION_DURATION));
            
            this.updateUI(true);
        }
    }

    checkWinner() {
        const pScore = this.getScore(this.playerHand);
        const dScore = this.getScore(this.dealerHand);

        if (dScore > 21) {
            this.endGame('Dealer Busted! (+3)', true, 3);
        } else if (pScore > dScore) {
            this.endGame('You Won! (+3)', true, 3);
        } else if (pScore < dScore) {
            this.endGame('You Lost (-2)', false, -2);
        } else {
            this.endGame('Push (+1)', false, 1);
        }
    }

    endGame(msg: string, win: boolean, points: number) {
        this.gameState = 'gameover';
        this.updateScore(points);
        this.completedGames += 1;
        if (this.currentUserId) {
            localStorage.setItem(`bj_games_completed_${this.currentUserId}`, String(this.completedGames));
        }
        
        const overlay = document.getElementById('result-overlay');
        const text = document.getElementById('result-text');
        if (overlay && text) {
            overlay.classList.remove('hidden');
            text.textContent = msg;
            text.style.color = win ? '#2ecc71' : (points > 0 ? '#f1c40f' : '#e74c3c');
            
            if (win) this.fireConfetti();
        }
    }

    private fireConfetti() {
        const canvas = document.getElementById('confetti-canvas') as HTMLCanvasElement;
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        const particles = this.generateConfettiParticles(CONFIG.CONFETTI_COUNT);
        this.animateConfetti(ctx, particles, canvas);
    }

    private generateConfettiParticles(count: number) {
        const colors = ['#f1c40f', '#e74c3c', '#2ecc71', '#3498db', '#9b59b6'];
        const particles = [];
        
        for (let i = 0; i < count; i++) {
            particles.push({
                x: window.innerWidth / 2,
                y: window.innerHeight / 2,
                vx: (Math.random() - 0.5) * 20,
                vy: (Math.random() - 0.5) * 20,
                color: colors[Math.floor(Math.random() * colors.length)],
                size: Math.random() * 10 + 5,
                life: 100
            });
        }
        return particles;
    } 

    private animateConfetti(ctx: CanvasRenderingContext2D, particles: any[], canvas: HTMLCanvasElement) {
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            let active = false;
            
            particles.forEach(p => {
                if (p.life > 0) {
                    active = true;
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.5;
                    p.life--;
                    
                    ctx.fillStyle = p.color;
                    ctx.fillRect(p.x, p.y, p.size, p.size);
                }
            });
            
            if (active) requestAnimationFrame(animate);
        };
        animate();
    }
}

export function initGame(app: HTMLDivElement, accessToken: string) {
    const game = new BlackjackGame(app, accessToken);
    
    return () => {
        if (game.autoRefreshInterval) {
            clearInterval(game.autoRefreshInterval);
        }
        app.innerHTML = '';
    };
}