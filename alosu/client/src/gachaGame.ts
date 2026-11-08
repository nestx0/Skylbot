import './style.css'; 
import { ApiService } from './api';

// --- 🎧 导入音频文件 (Import Audio Files) ---
import bgmAudio from '../music/kong.wav';
import clickAudio from '../music/dianji.wav';
import meteorAudio from '../music/xialuo.wav';
import impactAudio from '../music/kong.wav';
import flip3Audio from '../music/kong.wav'; 
import flip4Audio from '../music/4star.wav';
import flip5Audio from '../music/kong.wav';

// --- 🎧 音频配置 (Configuración de Audio) ---
const AUDIO_SRC = {
    bgm: bgmAudio,      // 背景音乐 (Música de fondo)
    click: clickAudio,   // 点击音效 (Efecto de clic)
    meteor: meteorAudio, // 流星音效 (Efecto de meteoro)
    impact: impactAudio, // 撞击音效 (Efecto de impacto)
    flip_3: flip3Audio,  // 3星翻牌音效 (Voltear 3 estrellas)
    flip_4: flip4Audio,  // 4星翻牌音效 (Voltear 4 estrellas)
    flip_5: flip5Audio   // 5星翻牌音效 (Voltear 5 estrellas)
};

// --- 🔊 Sound Manager (Gestor de Sonido) ---
class SoundManager {
    sounds: { [key: string]: HTMLAudioElement } = {};
    bgmStarted = false;

    constructor() {
        // 预加载所有声音
        Object.entries(AUDIO_SRC).forEach(([key, src]) => {
            const audio = new Audio(src);
            if (key === 'bgm') {
                audio.loop = true;
                audio.volume = 0.3; // 背景音乐音量低一点
            } else {
                audio.volume = 0.5;
            }
            this.sounds[key] = audio;
        });
    }

    play(key: keyof typeof AUDIO_SRC) {
        const audio = this.sounds[key];
        if (audio) {
            audio.currentTime = 0; // 重置到开头
            audio.play().catch(e => console.warn('Audio blocked:', e));
        }
    }

    ensureBgm() {
        if (!this.bgmStarted) {
            const bgm = this.sounds['bgm'];
            if (bgm) {
                bgm.play().then(() => {
                    this.bgmStarted = true;
                }).catch(() => { /* 等待下一次交互 */ });
            }
        }
    }

    // 停止所有声音 (用于销毁时清理)
    stopAll() {
        Object.values(this.sounds).forEach(audio => {
            audio.pause();
            audio.currentTime = 0;
        });
        this.bgmStarted = false;
    }
}

// --- 配置 (Configuración) ---
// CONFIG 原用于本地抽卡逻辑，已迁移到后端
// const CONFIG = { ... } // 已移除 - 后端控制所有概率计算

// --- Data Pool ---
// 所有抽卡数据现在完全由后端提供，不再使用本地Pool
// const POOL = { ... } // 已移除 - 后端返回的数据驱动一切

type Rarity = 1 | 2 | 3 | 4 | 5;
type GachaItem = { 
    name: string
    rarity: Rarity
    element: string
    isNew: boolean
    stars?: string
    // 来自后端的完整数据
    id?: string
    lvl?: number
    stats?: { HP: number; ATK: number; DEF: number; SPE: number; LCK: number }
    desc?: string
    image?: string
};
type UserData = { id: string; name: string };

const LOG_VERBOSE = false;
const logVerbose = (...args: unknown[]) => {
    if (LOG_VERBOSE) {
        console.log(...args);
    }
};

// --- CSS Styles (Estilos CSS) ---
const STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');

  :root {
    --gold: #FFD700;
    --purple: #D000FF;
    --blue: #38B6FF;
    --green: #35C46A;
    --gray: #9AA0A6;
    --dark-bg: #090A0F;
    --card-width: 240px;
    --card-height: 380px;
  }

  body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #000; }

  .gacha-container {
    position: relative; width: 100%; height: 100vh;
    background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
    font-family: 'Montserrat', 'Noto Sans SC', sans-serif;
    color: white; user-select: none;
    perspective: 1200px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }

  /* --- 背景动画 (Animación de Fondo) --- */
  .space-bg {
    position: absolute; inset: 0; z-index: 0;
    background-image: 
        radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 3px),
        radial-gradient(white, rgba(255,255,255,.1) 1px, transparent 2px);
    background-size: 550px 550px, 350px 350px;
    animation: space-move 120s linear infinite;
    opacity: 0.6;
    pointer-events: none;
  }
  @keyframes space-move { from { transform: translateY(0); } to { transform: translateY(-550px); } }

  /* --- UI Overlay --- */
  .start-screen {
    z-index: 50;
    text-align: center;
    transition: opacity 0.5s;
  }
  .start-screen.hidden { opacity: 0; pointer-events: none; }

  .banner-view {
    position: absolute; inset: 0; z-index: 10;
    display: flex; flex-direction: column; justify-content: flex-end; align-items: center;
    padding-bottom: 60px; transition: opacity 0.5s;
  }

  .title {
    font-size: 4rem; margin-bottom: 10px; font-weight: 900;
    text-shadow: 0 0 20px rgba(56, 182, 255, 0.5);
    background: linear-gradient(to bottom, #fff, #aaa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }

  .wish-btn {
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2);
    color: white; padding: 12px 30px; border-radius: 4px; cursor: pointer;
    backdrop-filter: blur(5px); margin: 0 10px; transition: 0.2s;
    display: flex; flex-direction: column; align-items: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  }
  .wish-btn:hover { background: rgba(255,255,255,0.2); transform: translateY(-2px); border-color: rgba(255,255,255,0.5); }
  .wish-btn:active { transform: translateY(0); }

    .banner-view.loading .wish-btn {
        pointer-events: none;
        opacity: 0.6;
        filter: grayscale(0.2);
    }

    .pull-loading {
        margin-top: 16px;
        font-size: 0.9rem;
        color: #9ad6ff;
        letter-spacing: 1px;
        opacity: 0;
        transform: translateY(6px);
        transition: opacity 0.2s ease, transform 0.2s ease;
    }

    .banner-view.loading .pull-loading {
        opacity: 1;
        transform: translateY(0);
    }

  /* --- 动画层 (Capa de Animación) --- */
  .anim-layer {
    position: absolute; inset: 0; transform-style: preserve-3d;
    z-index: 100; pointer-events: none; display: none;
  }

  .meteor {
    position: absolute; top: 50%; left: 50%;
    width: 10px; height: 10px; border-radius: 50%;
    transform: translate3d(80vw, -200vh, -6000px);
    opacity: 0;
  }

  .meteor::after {
    content: ''; position: absolute; top: 50%; left: 50%;
    height: 8px; width: 0px;
    clip-path: polygon(0 0, 100% 50%, 0 100%);
    transform-origin: left center;
    transform: translateY(-50%) rotateZ(-25deg);
    filter: blur(2px);
  }

  @keyframes tail-grow {
    0% { width: 0; opacity: 0; } 20% { width: 100px; opacity: 1; }
    80% { width: 800px; opacity: 1; } 100% { width: 900px; opacity: 0; }
  }

  .meteor.gold { background: #fff; box-shadow: 0 0 60px 20px rgba(255, 215, 0, 0.9); }
  .meteor.gold::after { background: linear-gradient(90deg, #FFD700 10%, transparent 100%); }

  .meteor.purple { background: #fff; box-shadow: 0 0 60px 20px rgba(208, 0, 255, 0.9); }
  .meteor.purple::after { background: linear-gradient(90deg, #D000FF 10%, transparent 100%); }

  .meteor.blue { background: #fff; box-shadow: 0 0 60px 20px rgba(56, 182, 255, 0.9); }
  .meteor.blue::after { background: linear-gradient(90deg, #38B6FF 10%, transparent 100%); }

  .meteor.green { background: #fff; box-shadow: 0 0 60px 20px rgba(53, 196, 106, 0.9); }
  .meteor.green::after { background: linear-gradient(90deg, #35C46A 10%, transparent 100%); }

  .meteor.gray { background: #fff; box-shadow: 0 0 60px 20px rgba(154, 160, 166, 0.9); }
  .meteor.gray::after { background: linear-gradient(90deg, #9AA0A6 10%, transparent 100%); }

  @keyframes meteor-3d-fall {
    0% { opacity: 0; transform: translate3d(80vw, -200vh, -6000px) rotate(0deg); }
    10% { opacity: 1; }
    100% { opacity: 1; transform: translate3d(-20vw, 20vh, 500px) rotate(-10deg); }
  }

  .falling { animation: meteor-3d-fall 2.2s cubic-bezier(0.19, 1, 0.22, 1) forwards; }
  .falling::after { animation: tail-grow 5s ease-out forwards; }

  .atmosphere-tint {
    position: absolute; inset: 0; pointer-events: none; z-index: 95;
    opacity: 0; transition: opacity 0.3s;
  }
  .tint-gold { background: radial-gradient(circle at bottom left, rgba(255, 215, 0, 0.5), transparent 60%); }
  .tint-purple { background: radial-gradient(circle at bottom left, rgba(208, 0, 255, 0.5), transparent 60%); }
  .tint-blue { background: radial-gradient(circle at bottom left, rgba(56, 182, 255, 0.5), transparent 60%); }
  .tint-green { background: radial-gradient(circle at bottom left, rgba(53, 196, 106, 0.5), transparent 60%); }
  .tint-gray { background: radial-gradient(circle at bottom left, rgba(154, 160, 166, 0.5), transparent 60%); }
  .active-tint { opacity: 1; }

  .flash {
    position: absolute; inset: 0; background: white; opacity: 0; z-index: 110; pointer-events: none;
  }
  .flashing { animation: flash-anim 0.8s ease-out forwards; }
  @keyframes flash-anim { 0% { opacity: 0; } 20% { opacity: 1; } 100% { opacity: 0; } }

  /* --- 结果视图 (Vista de Resultados) --- */
  .result-view {
    position: absolute; inset: 0; z-index: 20;
    display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
    background: rgba(0,0,0,0.85);
    opacity: 0; pointer-events: none; transition: opacity 0.5s;
    overflow-y: auto; /* 允许垂直滚动 */
    overflow-x: hidden;
  }
  .result-view.active { opacity: 1; pointer-events: auto; }

  /* 自定义滚动条样式 */
  .result-view::-webkit-scrollbar { width: 8px; }
  .result-view::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
  .result-view::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
  .result-view::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }

  .result-grid {
    display: flex; flex-wrap: wrap; justify-content: center; gap: 20px;
    width: 95%; max-width: 1400px; padding: 40px 20px 100px 20px; /* 增加上下内边距 */
    perspective: 1000px;
    margin: auto; /* 垂直居中 */
  }

  /* 响应式卡片大小 - 小屏幕自动缩小 */
  @media (max-height: 800px) {
    :root { --card-width: 200px; --card-height: 320px; }
    .result-grid { gap: 15px; padding: 30px 15px 80px 15px; }
  }
  
  @media (max-height: 600px) {
    :root { --card-width: 160px; --card-height: 260px; }
    .result-grid { gap: 10px; padding: 20px 10px 60px 10px; }
    .char-name { font-size: 1.1rem; }
    .char-rarity { font-size: 0.85rem; }
    .panel-name { font-size: 0.95rem; }
  }

  /* --- 卡片核心样式 (Estilos de Tarjeta) --- */
  .card-container {
    width: var(--card-width); height: var(--card-height);
    position: relative; cursor: pointer;
    opacity: 0; transform: translateY(30px);
  }
  .card-container.visible { animation: card-enter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }

  @keyframes card-enter { to { opacity: 1; transform: translateY(0); } }

  .card-inner {
    position: relative; width: 100%; height: 100%;
    transform-style: preserve-3d;
    transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    border-radius: 12px;
  }

  .card-container.flipped .card-inner { transform: rotateY(180deg); }

  /* --- 卡片背面 (Reverso) --- */
  .card-back {
    position: absolute; inset: 0; backface-visibility: hidden;
    background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
    border: 2px solid #333; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 3rem; color: rgba(255,255,255,0.1);
    z-index: 2;
  }
  .card-back::after { content: '✦'; font-size: 4rem; text-shadow: 0 0 20px rgba(255,255,255,0.2); }

    .r5 .card-back { border-color: rgba(255, 215, 0, 0.6); box-shadow: 0 0 25px rgba(255, 215, 0, 0.2); }
    .r4 .card-back { border-color: rgba(208, 0, 255, 0.6); box-shadow: 0 0 25px rgba(208, 0, 255, 0.2); }
    .r3 .card-back { border-color: rgba(56, 182, 255, 0.6); }
    .r2 .card-back { border-color: rgba(53, 196, 106, 0.6); box-shadow: 0 0 20px rgba(53, 196, 106, 0.2); }
    .r1 .card-back { border-color: rgba(154, 160, 166, 0.6); box-shadow: 0 0 15px rgba(154, 160, 166, 0.2); }

  /* --- 卡片正面 (Frente) --- */
  .card-front {
    position: absolute; inset: 0; backface-visibility: hidden;
    transform: rotateY(180deg);
    border-radius: 12px; overflow: hidden;
    background-color: #1a1a1a;
    background-size: cover; background-position: center;
    border: 2px solid transparent;
  }

    .r5 .card-front { border-color: var(--gold); box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); }
    .r4 .card-front { border-color: var(--purple); box-shadow: 0 0 20px rgba(208, 0, 255, 0.4); }
    .r3 .card-front { border-color: var(--blue); }
    .r2 .card-front { border-color: var(--green); box-shadow: 0 0 18px rgba(53, 196, 106, 0.35); }
    .r1 .card-front { border-color: var(--gray); box-shadow: 0 0 14px rgba(154, 160, 166, 0.3); }

  .card-front::before {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 40%, transparent 100%);
    z-index: 1;
  }

  /* --- 基础信息层 (Layer de Info Básica) --- */
  .basic-info {
    position: absolute; bottom: 15px; left: 15px; right: 15px; z-index: 2;
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    transition: transform 0.3s ease, opacity 0.3s ease;
  }
  .card-container.flipped:hover .basic-info { transform: translateY(-10px); opacity: 0; }

  .char-name { font-size: 1.4rem; font-weight: 800; color: #fff; margin: 0; line-height: 1.2; }
  .char-rarity { font-size: 1rem; letter-spacing: 2px; margin-top: 4px; }
    .r5 .char-rarity { color: var(--gold); }
    .r4 .char-rarity { color: var(--purple); }
    .r3 .char-rarity { color: var(--blue); }
    .r2 .char-rarity { color: var(--green); }
    .r1 .char-rarity { color: var(--gray); }

  /* --- 详细属性面板 (Panel de Estadísticas) --- */
  .stats-panel {
    position: absolute; inset: 0; z-index: 10;
    background: rgba(15, 15, 20, 0.9);
    backdrop-filter: blur(8px);
    padding: 20px;
    display: flex; flex-direction: column; justify-content: center;
    opacity: 0; transform: translateY(20px);
    transition: all 0.3s ease;
    pointer-events: none;
  }

  .card-container.flipped:hover .stats-panel {
    opacity: 1; transform: translateY(0); pointer-events: auto;
  }

  .panel-header {
    border-bottom: 1px solid rgba(255,255,255,0.2);
    padding-bottom: 8px; margin-bottom: 12px;
  }
  .panel-name { font-size: 1.1rem; font-weight: bold; color: white; }
  .panel-lvl { font-size: 0.8rem; color: #aaa; margin-top: 2px; }

  .stats-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
    margin-bottom: 15px;
  }
  .stat-row {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(255,255,255,0.05); padding: 4px 8px; border-radius: 4px;
  }
  .stat-icon { font-size: 0.9rem; margin-right: 6px; }
  .stat-val { font-weight: bold; font-family: monospace; color: #eee; font-size: 0.9rem; }

  .desc-box {
    font-size: 0.75rem; line-height: 1.4; color: #ccc;
    background: rgba(0,0,0,0.3); padding: 8px; border-radius: 4px;
    font-style: italic; border-left: 2px solid rgba(255,255,255,0.3);
    margin-bottom: 10px;
  }

    /* --- 按钮 (Botones) --- */
    .action-bar {
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        flex-direction: column;
        gap: 12px;
        z-index: 100;
    }
  .btn {
    padding: 12px 30px; border: none; border-radius: 50px;
    font-weight: bold; cursor: pointer; text-transform: uppercase;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    font-family: inherit;
  }
  .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.4); }
  .btn-start { background: linear-gradient(45deg, #38B6FF, #0056b3); color: white; font-size: 1.2rem; padding: 15px 50px; }
  .btn-skip { background: rgba(255,255,255,0.15); color: white; backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.3); }
  .btn-confirm { background: white; color: black; }
  .hidden { display: none !important; }

  /* Toast Message */
  .gacha-toast {
    position: fixed; top: 40px; right: 20px; z-index: 9999;
    background: rgba(0, 0, 0, 0.9); color: #fff;
    padding: 12px 20px; border-radius: 8px;
    border: 2px solid #38B6FF;
    font-weight: bold; font-size: 0.9rem;
    animation: slideIn 0.3s ease-out;
  }
  @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }

  @keyframes slideInRight {
    from { transform: translateX(400px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(400px); opacity: 0; }
  }
`;

class GachaGame {
    app: HTMLDivElement;
    token: string;
    audio: SoundManager;
    
    // State (Estado)
    pity5 = 0; pity4 = 0; goldCount = 0;
    currentResults: GachaItem[] = [];
    private timers: number[] = [];

    // 用户数据相关 (Datos de usuario)
    currentUser: UserData | null = null;
    userBalanceMap: Map<string, number> = new Map();
    readonly COST_PER_PULL = 3000;
    private balanceSyncTimer?: number;
    private isPulling = false;

    /**
     * 显示消息 (由于 Discord iframe 沙箱限制，不能使用 alert)
     */
    private showMessage(message: string, type: 'info' | 'error' | 'warning' = 'info'): void {
        const colorMap = {
            'info': '#4ecdc4',
            'error': '#ff6b6b',
            'warning': '#FFD700'
        };
        console.log(`%c[Gacha Message] ${message}`, `color: ${colorMap[type]}; font-weight: bold;`);
        
        // 在页面上显示临时提示
        const existingToast = this.app.querySelector('.gacha-toast');
        if (existingToast) existingToast.remove();
        
        const toast = document.createElement('div');
        toast.className = 'gacha-toast';
        toast.style.cssText = `
            position: fixed; top: 80px; right: 20px; z-index: 9999;
            background: rgba(0, 0, 0, 0.9); color: ${colorMap[type]};
            padding: 12px 20px; border-radius: 8px;
            border: 2px solid ${colorMap[type]};
            font-weight: bold; font-size: 0.9rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            animation: slideInRight 0.3s ease-out;
        `;
        toast.textContent = message;
        this.app.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    private setStoredBalance(userId: string, balance: number): void {
        try {
            localStorage.setItem(`gacha_balance_${userId}`, String(balance));
        } catch {
            // ignore storage errors
        }
    }

    private setBalance(userId: string, balance: number | null): void {
        if (balance === null || balance === undefined) {
            this.userBalanceMap.delete(userId);
            return;
        }
        this.userBalanceMap.set(userId, balance);
    }

    private setPullState(isPulling: boolean): void {
        this.isPulling = isPulling;
        const banner = this.app.querySelector('#banner-view') as HTMLElement | null;
        const p1 = this.app.querySelector('#pull-1') as HTMLButtonElement | null;
        const p10 = this.app.querySelector('#pull-10') as HTMLButtonElement | null;

        if (banner) {
            banner.classList.toggle('loading', isPulling);
        }
        if (p1) p1.disabled = isPulling;
        if (p10) p10.disabled = isPulling;
    }

    constructor(app: HTMLDivElement, token: string) {
        this.app = app;
        this.token = token;
        this.audio = new SoundManager();
        console.log(`[Gacha] Constructor called with token: ${token}`);

        this.app.innerHTML = `
            <style>${STYLES}</style>
            <div class="gacha-container">
                <div class="space-bg"></div>
                <div class="atmosphere-tint" id="tint-layer"></div>
                
                <div class="banner-view" id="banner-view">
                    <div style="text-align:center; margin-bottom:20px;">
                          <div style="font-size:4rem; margin-bottom:10px; filter:drop-shadow(0 0 30px rgba(255,255,255,0.3))">Pull Simulator</div>
                          <h1 style="font-size:2.5rem; margin:0; letter-spacing:4px; font-weight:900;">ALOSU</h1>
                    </div>
                        <div style="display:flex; gap:12px; align-items:center; justify-content:center; margin-bottom:12px;">
                            <div id="user-display" style="font-size:0.9rem; color:#ddd">User: Loading...</div>
                            <div style="font-size:1.1rem; color:#38B6FF; font-weight:bold;">💎 <span id="balance-display">Loading...</span></div>
                        </div>
                    
                    <div style="display:flex; gap:20px;">
                        <button class="wish-btn" id="pull-1" disabled>
                            <span style="font-weight:700; font-size:1.1rem">WISH x1</span>
                            <span style="font-size:0.75rem; opacity:0.7">💎 3000</span>
                        </button>
                        <button class="wish-btn" id="pull-10" disabled>
                            <span style="font-weight:700; font-size:1.1rem">WISH x10</span>
                            <span style="font-size:0.75rem; opacity:0.7">💎 30000</span>
                        </button>
                    </div>
                    <div class="pull-loading" id="pull-loading">Connecting to server...</div>
                </div>

                <div class="anim-layer" id="anim-layer">
                    <div class="meteor" id="meteor"></div>
                </div>
                <div class="flash" id="flash"></div>

                <div class="result-view" id="result-view">
                    <div class="result-grid" id="result-grid"></div>
                    <div class="action-bar">
                        <button class="action-btn" id="skip-btn">SKIP</button>
                        <button class="action-btn hidden" id="close-btn">CONFIRM</button>
                    </div>
                </div>
            </div>
        `;

        // 先绑定事件，然后再异步加载数据
        this.bindEvents();
        
        // 异步初始化（不阻塞UI）
        this.loadData().then(() => {
            console.log('[Gacha] Game initialization complete');
            // 启用按钮
            const p1 = this.app.querySelector('#pull-1') as HTMLButtonElement;
            const p10 = this.app.querySelector('#pull-10') as HTMLButtonElement;
            if (p1) p1.disabled = false;
            if (p10) p10.disabled = false;
        }).catch(err => {
            console.error('[Gacha] Failed to initialize game:', err);
            this.showMessage('Failed to load game: ' + String(err), 'error');
        });
        
        this.startBalanceSync();
    }

    private setTimer(callback: () => void, ms: number) {
        const id = window.setTimeout(callback, ms);
        this.timers.push(id);
        return id;
    }

    // 启动定时余额同步 (Iniciar sincronización periódica de saldo)
    private startBalanceSync() {
        console.log('⏱️ Starting balance sync: every 5 seconds');
        this.balanceSyncTimer = window.setInterval(async () => {
            if (!this.currentUser) return;
            
            try {
                const balanceResult = await ApiService.getBalance(this.currentUser.id);
                if (balanceResult.balance === null) return;
                
                const oldBalance = this.userBalanceMap.get(this.currentUser.id);
                const newBalance = balanceResult.balance;
                
                // 只有当余额真的变化时才更新UI
                if (oldBalance !== undefined && oldBalance !== newBalance) {
                    const change = newBalance - oldBalance;
                    const changeStr = change > 0 ? `+${change}` : `${change}`;
                    console.log(`%c[Gacha] 💰 Balance changed: ${oldBalance} → ${newBalance} (${changeStr})`, 'color: #FFD700; font-weight: bold;');
                    
                    this.setBalance(this.currentUser.id, newBalance);
                    this.setStoredBalance(this.currentUser.id, newBalance);
                    this.updateUI();
                    
                    // 显示提示信息
                    this.showMessage(`Balance updated: ${changeStr} 💎`, change > 0 ? 'info' : 'warning');
                } else if (oldBalance === undefined) {
                    // 首次同步，不显示提示
                    this.setBalance(this.currentUser.id, newBalance);
                    this.setStoredBalance(this.currentUser.id, newBalance);
                }
            } catch (err) {
                // 静默失败，不影响用户体验
            }
        }, 5000) as unknown as number;
    }

    bindEvents() {
        const p1 = this.app.querySelector('#pull-1');
        const p10 = this.app.querySelector('#pull-10');

        p1?.addEventListener('click', async () => {
            if (this.isPulling) return;
            this.audio.play('click');
            this.audio.ensureBgm();
            await this.attemptPull(1);
        });

        p10?.addEventListener('click', async () => {
            if (this.isPulling) return;
            this.audio.play('click');
            this.audio.ensureBgm();
            await this.attemptPull(10);
        });

        this.app.querySelector('#skip-btn')?.addEventListener('click', () => {
            this.audio.play('click');
            this.revealAllCards();
        });
        this.app.querySelector('#close-btn')?.addEventListener('click', () => {
            this.audio.play('click');
            this.resetUI();
        });
    }

    // 1. 开启游戏时加载数据 (Carga de datos)
    async loadData(): Promise<void> {
        const d = JSON.parse(localStorage.getItem('gacha_ultimate') || '{}');
        this.pity5 = d.p5 || 0; 
        this.goldCount = d.g || 0;
        this.updateUI();

        try {
            console.log('%c[Gacha] Loading user from Discord context...', 'color: #4ecdc4; font-weight: bold;');
            const discordUserId = localStorage.getItem('discord_user_id') || (window as any).DISCORD_USER_ID || '';
            const discordUsername = localStorage.getItem('discord_username') || (window as any).DISCORD_USERNAME || 'Discord User';

            if (discordUserId) {
                this.currentUser = { id: discordUserId, name: discordUsername };
                console.log('%c[Gacha] Discord user id:', 'color: #FFD700', discordUserId);
                
                // 只调用 balance 接口同步余额，不调用 getAllUsers
                const balanceResult = await ApiService.getBalance(this.currentUser.id);
                if (balanceResult.balance !== null) {
                    this.setBalance(this.currentUser.id, balanceResult.balance);
                    this.setStoredBalance(this.currentUser.id, balanceResult.balance);
                    console.log('%c[Gacha] ✅ Balance synced:', 'color: #51cf66', balanceResult.balance);
                } else {
                    this.showMessage('Failed to sync balance', 'warning');
                }
            } else {
                console.error("%c[Gacha] ❌ No Discord user id found!", 'color: #ff6b6b; font-weight: bold;');
                this.showMessage('Discord authentication required', 'error');
            }
        } catch (error) {
            console.error("%c[Gacha] ❌ Load data error:", 'color: #ff6b6b; font-weight: bold;', error);
            this.showMessage('Failed to load user data', 'error');
        }
        this.updateUI();
    }

    // 2. 抽卡核心流程 - 使用Pull API (Lógica principal del Gacha - Pull API)
    async attemptPull(amount: number) {
        if (!this.currentUser) {
            this.showMessage("(Por favor espera a que se carguen los datos)", 'warning');
            return;
        }

        if (this.isPulling) {
            return;
        }

        this.setPullState(true);

        // --- A. 发送Pull请求到后端 (参考 sqltest.py) ---
        console.log(`%c[Gacha] Sending Pull request for ${amount} pulls...`, 'color: #FFD700; font-weight: bold;');
        let pullResp: any = null;
        try {
            pullResp = await ApiService.pull(this.currentUser.id, amount);
        } catch (err) {
            console.error(err);
            this.showMessage('(Request failed)', 'error');
            this.setPullState(false);
            return;
        }

        // --- B. 处理后端响应 ---
        if (!pullResp || pullResp.status !== 'success') {
            const errorMsg = pullResp?.error || 'Unknown Error';
            const message = pullResp?.message || errorMsg;
            
            if (errorMsg === 'insufficient_funds') {
                this.showMessage(`❌ NO MONEY BRO! Balance: ${pullResp?.balance ?? 0}`, 'error');
            } else {
                this.showMessage(`❌ ${message}`, 'error');
            }
            
            // 如果后端返回了最新余额，更新显示
            if (pullResp?.balance !== undefined) {
                this.setBalance(this.currentUser.id, pullResp.balance);
                this.updateUI();
            }
            this.setPullState(false);
            return;
        }

        // --- C. 后端返回成功，处理详细结果 ---
        console.log('%c[Gacha] ✅ Pull successful!', 'color: #51cf66; font-weight: bold;');
        logVerbose('%c[Gacha] Full pullResp:', 'color: #4ecdc4', pullResp);
        logVerbose('%c[Gacha] pullResp.results:', 'color: #4ecdc4', pullResp.results);
        logVerbose('%c[Gacha] pullResp.results length:', 'color: #4ecdc4', pullResp.results?.length);
        logVerbose('%c   Results:', 'color: #4ecdc4');
        
        const summary = pullResp.summary;
        if (summary) {
            // 更新余额和Pity计数
            this.setBalance(this.currentUser.id, summary.new_balance);
            this.setStoredBalance(this.currentUser.id, summary.new_balance);
            this.pity5 = summary.pity5 ?? this.pity5;
            this.pity4 = summary.pity4 ?? this.pity4;
            this.goldCount = summary.goldCount ?? this.goldCount;
            
            logVerbose(`%c   New Balance: ${summary.new_balance}`, 'color: #FFD700');
            logVerbose(`%c   Cost: ${summary.total_cost}`, 'color: #FFD700');
            logVerbose(`%c   Pity5: ${summary.pity5}, Pity4: ${summary.pity4}, GoldCount: ${summary.goldCount}`, 'color: #FFD700');
        }

        // 转换结果用于动画展示 - 保留所有返回的数据
        this.currentResults = (pullResp.results || []).map((r: any) => ({ 
            name: r.name, 
            rarity: r.rarity, 
            element: r.element, 
            isNew: !!r.isNew,
            stars: r.stars || '★'.repeat(r.rarity),
            // 保留所有来自后端的额外数据
            id: r.id,
            lvl: r.lvl,
            stats: r.stats,
            desc: r.desc,
            image: r.image
        }));
        
        logVerbose('%c[Gacha] After mapping, currentResults.length:', 'color: #FFD700', this.currentResults.length);
        logVerbose('%c[Gacha] currentResults with full data:', 'color: #4ecdc4', this.currentResults);
        
        // 详细日志每个获取物品
        if (pullResp.results && pullResp.results.length > 0) {
            pullResp.results.forEach((item: any, idx: number) => {
                logVerbose(`%c      [${idx + 1}] ${item.stars} ${item.name} (${item.element})`, 
                    `color: ${item.rarity === 5 ? '#FFD700' : item.rarity === 4 ? '#D000FF' : '#38B6FF'}; font-weight: bold;`);
                logVerbose(`%c         Image: ${item.image}`, 'color: #4ecdc4');
                logVerbose(`%c         Stats:`, 'color: #4ecdc4', item.stats);
            });
        } else {
            console.warn('%c[Gacha] ⚠️ No results received!', 'color: #FFD700; font-weight: bold;');
        }
        
        this.saveData(); 
        this.updateUI();
        this.startSequence(amount); // 开始展示动画
    }

    saveData() {
        localStorage.setItem('gacha_ultimate', JSON.stringify({ p5: this.pity5, g: this.goldCount }));
    }

    updateUI() {
        const pityEl = this.app.querySelector('#pity-count');
        const goldEl = this.app.querySelector('#gold-count');
        if (pityEl) pityEl.textContent = this.pity5.toString();
        if (goldEl) goldEl.textContent = this.goldCount.toString();
        
        const userEl = this.app.querySelector('#user-display');
        const balEl = this.app.querySelector('#balance-display');
        
        if (this.currentUser) {
            if (userEl) userEl.textContent = `User: ${this.currentUser.name} (ID: ${this.currentUser.id})`;
            if (this.userBalanceMap.has(this.currentUser.id)) {
                const balance = this.userBalanceMap.get(this.currentUser.id) ?? 0;
                if (balEl) balEl.textContent = balance.toString();
            } else {
                if (balEl) balEl.textContent = 'N/A';
            }
        }
    }

    // --- 动画逻辑 (Lógica de animación) ---
    // 注：所有数据生成逻辑已迁移到后端，本地不再生成抽卡数据

    async startSequence(_amount: number) {
        let maxRarity = 0;

        // ✅ 所有数据现在由后端pull请求提供，不需要本地生成
        // 计算最大稀有度用于决定流星颜色
        for (const item of this.currentResults) {
            if (item.rarity > maxRarity) maxRarity = item.rarity;
        }

        this.saveData(); 
        
        // 隐藏 Banner，开始播放流星动画
        const banner = this.app.querySelector('#banner-view') as HTMLElement;
        banner.style.opacity = '0'; banner.style.pointerEvents = 'none';
        
        const meteor = this.app.querySelector('#meteor') as HTMLElement;
        const tint = this.app.querySelector('#tint-layer') as HTMLElement;
        const animLayer = this.app.querySelector('#anim-layer') as HTMLElement;

        meteor.className = 'meteor';
        tint.className = 'atmosphere-tint';
        let colorClass = 'blue';
        if (maxRarity === 5) colorClass = 'gold';
        else if (maxRarity === 4) colorClass = 'purple';
        else if (maxRarity === 3) colorClass = 'blue';
        else if (maxRarity === 2) colorClass = 'green';
        else if (maxRarity === 1) colorClass = 'gray';
        meteor.classList.add(colorClass);
        tint.classList.add(`tint-${colorClass}`);

        animLayer.style.display = 'block';
        meteor.classList.add('falling');
        this.audio.play('meteor');

        // 背景变色
        this.setTimer(() => { tint.classList.add('active-tint'); }, 1200);
        
        // 等待撞击
        await new Promise(r => this.setTimer(() => r(undefined), 2000)); 
        this.app.querySelector('#flash')?.classList.add('flashing');
        this.audio.play('impact');
        
        // 切换到结果界面
        this.setTimer(() => {
            animLayer.style.display = 'none';
            tint.classList.remove('active-tint');
            this.showCardsStage();
        }, 300);
        this.setTimer(() => this.app.querySelector('#flash')?.classList.remove('flashing'), 1000);
    }

    showCardsStage() {
        const view = this.app.querySelector('#result-view') as HTMLElement;
        const grid = this.app.querySelector('#result-grid') as HTMLElement;
        const skipBtn = this.app.querySelector('#skip-btn') as HTMLElement;
        const closeBtn = this.app.querySelector('#close-btn') as HTMLElement;

        view.classList.add('active');
        grid.innerHTML = '';
        skipBtn.classList.remove('hidden');
        closeBtn.classList.add('hidden');

        this.currentResults.forEach((item, idx) => {
            const cardContainer = document.createElement('div');
            cardContainer.className = `card-container r${item.rarity}`;
            cardContainer.style.animationDelay = `${idx * 100}ms`;

            // 使用实际返回的stats数据，如果没有则生成默认值
            const stats = item.stats || {
                HP: Math.floor(Math.random() * 1000) + 500 + (item.rarity === 5 ? 300 : item.rarity === 4 ? 150 : 0),
                ATK: Math.floor(Math.random() * 300) + 50 + (item.rarity === 5 ? 100 : item.rarity === 4 ? 50 : 0),
                DEF: Math.floor(Math.random() * 200) + 30 + (item.rarity === 5 ? 80 : item.rarity === 4 ? 40 : 0),
                SPE: Math.floor(Math.random() * 100) + 10,
                LCK: Math.floor(Math.random() * 50) + 1
            };
            
            // 使用HTTP请求返回的ID和等级
            const charLevel = item.lvl || 1;  // 默认等级为1
            const charId = item.id || `unknown`;  // 使用HTTP返回的ID
            const description = item.desc || `Element: ${item.element}`;
            
            // 图片URL处理和调试
            const imageUrl = item.image || '';
            logVerbose(`%c[Card ${idx}] Image URL:`, 'color: #4ecdc4', imageUrl);
            logVerbose(`%c[Card ${idx}] Character:`, 'color: #4ecdc4', item.name);
            

            cardContainer.innerHTML = `
                <div class="card-inner">
                    <div class="card-back"></div>
                    <div class="card-front">
                        ${imageUrl ? `<img src="${imageUrl}" alt="${item.name}" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0;" crossorigin="anonymous" class="char-image">` : ''}
                        <div class="basic-info">
                            <h3 class="char-name">${item.name}</h3>
                            <div class="char-rarity">${'★'.repeat(item.rarity)}</div>
                        </div>

                        <div class="stats-panel">
                            <div class="panel-header">
                                <div class="panel-name">${item.name}</div>
                                <div class="panel-lvl">ID: ${charId} | Lv.${charLevel}</div>
                            </div>
                            <div class="stats-grid">
                                <div class="stat-row"><span class="stat-icon">❤️</span> <span class="stat-val">${stats.HP}</span></div>
                                <div class="stat-row"><span class="stat-icon">⚔️</span> <span class="stat-val">${stats.ATK}</span></div>
                                <div class="stat-row"><span class="stat-icon">🛡️</span> <span class="stat-val">${stats.DEF}</span></div>
                                <div class="stat-row"><span class="stat-icon">⚡</span> <span class="stat-val">${stats.SPE}</span></div>
                                <div class="stat-row"><span class="stat-icon">🍀</span> <span class="stat-val">${stats.LCK}</span></div>
                            </div>
                            <div class="desc-box">"${description}"</div>
                            ${item.isNew ? '<div style="margin-top:auto; color:#ff4d4d; font-weight:bold; font-size:0.7rem; text-align:right;">✨ NEW</div>' : ''}
                        </div>
                    </div>
                </div>
            `;
            
            // 添加图片加载错误处理（不使用内联事件）
            const imgEl = cardContainer.querySelector('.char-image');
            if (imgEl) {
                imgEl.addEventListener('error', () => {
                    console.error(`Failed to load image for ${item.name}: ${imageUrl}`);
                });
                imgEl.addEventListener('load', () => {
                    logVerbose(`✅ Successfully loaded image for ${item.name}`);
                });
            }

            // 点击单张翻牌
            cardContainer.addEventListener('click', () => {
                if (!cardContainer.classList.contains('flipped')) {
                    cardContainer.classList.add('flipped');
                    if (item.rarity === 5) this.audio.play('flip_5');
                    else if (item.rarity === 4) this.audio.play('flip_4');
                    else this.audio.play('flip_3');
                    this.checkAllRevealed();
                }
            });

            grid.appendChild(cardContainer);

            // 错峰显示动画
            this.setTimer(() => cardContainer.classList.add('visible'), 50 + (idx * 100));
        });
    }

    revealAllCards() {
        const cards = this.app.querySelectorAll('.card-container');
        cards.forEach((card, i) => {
            if (i === 0) this.audio.play('flip_3');
            this.setTimer(() => { card.classList.add('flipped'); }, i * 50);
        });
        this.checkAllRevealed(true);
    }

    checkAllRevealed(force = false) {
        const cards = this.app.querySelectorAll('.card-container');
        const flipped = this.app.querySelectorAll('.card-container.flipped');
        if (force || flipped.length === cards.length) {
            this.app.querySelector('#skip-btn')?.classList.add('hidden');
            this.app.querySelector('#close-btn')?.classList.remove('hidden');
        }
    }

    resetUI() {
        const resultView = this.app.querySelector('#result-view') as HTMLElement;
        resultView.classList.remove('active');
        const banner = this.app.querySelector('#banner-view') as HTMLElement;
        banner.style.opacity = '1';
        banner.style.pointerEvents = 'auto';
        this.setPullState(false);
        
        // 动画结束后，刷新余额确保显示最新数据
        if (this.currentUser) {
            ApiService.getBalance(this.currentUser.id)
                .then(balanceResult => {
                    if (balanceResult.balance !== null) {
                        this.setBalance(this.currentUser!.id, balanceResult.balance);
                        this.setStoredBalance(this.currentUser!.id, balanceResult.balance);
                        this.updateUI();
                        console.log('%c[Gacha] ✅ Balance refreshed after animation:', 'color: #51cf66', balanceResult.balance);
                    }
                })
                .catch(err => console.warn('[Gacha] Balance refresh failed:', err));
        }
    }

    destroy() {
        console.log('🗑️ Destroying game instance...');
        if (this.balanceSyncTimer) {
            clearInterval(this.balanceSyncTimer);
            console.log('🛑 Balance sync timer cleared');
        }
        this.timers.forEach(id => clearTimeout(id));
        this.audio.stopAll();
        this.app.innerHTML = '';
    }
}

export function initGame(app: HTMLDivElement, token: string) {
    const game = new GachaGame(app, token);
    return () => game.destroy();
}