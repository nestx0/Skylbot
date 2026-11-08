/**
 * Discord Activity Platform - Main Entry Point
 * 
 * Key responsibilities:
 * - Initialize Discord SDK and authenticate
 * - Load specific game based on configuration
 * - Handle error recovery and token refresh
 */

import './style.css';
import { discordSdk } from './discordSdk';
import { setupDiscordSdk } from './utils/auth';
import { logger } from './utils/logger';

const ALLOWED_USER_ID = '0000';
const TOKEN_REFRESH_INTERVAL = 15 * 60 * 1000; // 15分钟

// =================================================================
// 🎮 游戏配置 - 修改这里来切换游戏
// =================================================================
// Removed CURRENT_GAME - now using dynamic game selector

// Available games configuration
const AVAILABLE_GAMES = [
    {
        name: 'blackjack',
        displayName: '🃏 Blackjack',
        description: 'Classic 21 card game - Beat the dealer!'
    },
    {
        name: 'gacha',
        displayName: '🎲 Gacha Game',
        description: 'Pull for rare characters and items!'
    },
    {
        name: 'rocket',
        displayName: '🏪 Warehouse',
        description: 'View all users and their inventory items!'
    }
] as const;

type GameName = typeof AVAILABLE_GAMES[number]['name'];

// =================================================================
// 📦 状态保持
// =================================================================
let globalApp: HTMLDivElement | null = null;
let globalToken: string | null = null;
let refreshTimer: number | null = null;

// =================================================================
// 🚀 初始化主流程
// =================================================================
async function initializeActivity(): Promise<void> {
    const app = document.querySelector<HTMLDivElement>('#app');
    globalApp = app;

    // 1. 浏览器环境检测
    if (!discordSdk || window.parent === window) {
        logger.warn('🚫 Browser/External access detected. Blocking.');
        if (app) renderMaintenancePage(app, { id: 'EXTERNAL_ACCESS' });
        return;
    }

    // 2. 尝试连接流程
    await attemptConnection();
}

// 🔄 独立的连接尝试函数
async function attemptConnection() {
    if (!globalApp) return;

    try {
        // --- UI: Loading ---
        globalApp.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #000; color: white; font-family: sans-serif;">
                <div style="font-size: 3rem; animation: spin 1s infinite linear;">🔄</div>
                <h3 id="loading-text" style="margin-top: 20px; letter-spacing: 2px;">CONECTANDO...</h3>
                <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
            </div>
        `;
        
        logger.info('Initializing Discord Activity...');

        // 🌟 SDK Ready (超时保护)
        if (!discordSdk) {
            throw new Error('Discord SDK is not available');
        }
        
        const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error("Connection Timeout (8s)")), 8000)
        );
        
        await Promise.race([discordSdk.ready(), timeoutPromise]);

        // 🌟 Auth
        globalApp.querySelector('#loading-text')!.textContent = "AUTENTICANDO...";
        
        // 获取 Token
        const accessToken = await setupDiscordSdk();
        globalToken = accessToken;

        // 🌟 启动自动刷新 (后台静默运行)
        startTokenAutoRefresh();

        // 🌟 获取用户信息
        const response = await fetch('https://discord.com/api/users/@me', {
            headers: { Authorization: `Bearer ${accessToken}` },
        });
        
        if (!response.ok) {
            throw new Error(`Auth Failed: ${response.status}`);
        }
        
        const user = await response.json();

        // 封禁检查
        if (user.id == ALLOWED_USER_ID) {
            renderMaintenancePage(globalApp, user);
            return;
        }

        // 保存 Discord 用户 ID/用户名 到 localStorage 与全局 window，供游戏模块使用
        try {
            localStorage.setItem('discord_user_id', String(user.id));
            localStorage.setItem('discord_username', String(user.username ?? 'Discord User'));
            (window as any).DISCORD_USER_ID = String(user.id);
            (window as any).DISCORD_USERNAME = String(user.username ?? 'Discord User');
            console.log('[Main] Stored DISCORD_USER_ID:', user.id);
        } catch (e) {
            console.warn('[Main] Failed to persist discord_user_id', e);
        }

        // 🌟 一切正常，显示游戏选择器
        showGameSelector();
        logger.info('Discord Activity initialized successfully');

    } catch (error) {
        logger.error('Failed', error);
        renderRetryPage(globalApp, error);
    }
}

// =================================================================
// 🔄 Token 自动刷新逻辑 (静默)
// =================================================================
function startTokenAutoRefresh() {
    if (refreshTimer) clearTimeout(refreshTimer);
    
    refreshTimer = window.setTimeout(async () => {
        try {
            logger.info('🔄 Silent Token Refresh...');
            
            const newToken = await setupDiscordSdk();
            if (newToken) {
                globalToken = newToken;
                logger.info('✅ Token refreshed silent.');
                
                // 广播给游戏实例
                window.dispatchEvent(new CustomEvent('DISCORD_TOKEN_REFRESHED', { 
                    detail: { token: newToken } 
                }));
            }
        } catch (err) {
            logger.warn('⚠️ Token refresh failed (will retry next cycle):', err);
        } finally {
            startTokenAutoRefresh();
        }
    }, TOKEN_REFRESH_INTERVAL);
}

// =================================================================
// 🎮 游戏选择器界面
// =================================================================
function showGameSelector() {
    if (!globalApp) return;
    
    // 清理之前的游戏
    if ((globalApp as any)._gameCleanup) {
        try {
            (globalApp as any)._gameCleanup();
        } catch (error) {
            console.warn('Error cleaning up previous game:', error);
        }
        (globalApp as any)._gameCleanup = null;
    }
    
    globalApp.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #2a0a2e); background-size: 400% 400%; animation: gradient-bg 15s ease infinite; color: white; font-family: 'Orbitron', sans-serif; text-align: center; padding: 20px;">
            <style>
                @keyframes gradient-bg {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }
                @keyframes float {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-20px); }
                }
                .game-selector-container {
                    background: rgba(0,0,0,0.4);
                    border-radius: 20px;
                    padding: 40px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.1);
                    max-width: 600px;
                    width: 100%;
                }
                .game-card {
                    background: rgba(255,255,255,0.1);
                    border: 2px solid transparent;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 15px 0;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(5px);
                }
                .game-card:hover {
                    background: rgba(255,255,255,0.2);
                    border-color: #4ecdc4;
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(78, 205, 196, 0.3);
                }
                .game-icon {
                    font-size: 3rem;
                    margin-bottom: 10px;
                    animation: float 3s ease-in-out infinite;
                }
                .game-title {
                    font-size: 1.5rem;
                    font-weight: bold;
                    margin-bottom: 8px;
                    color: #fff;
                }
                .game-description {
                    font-size: 1rem;
                    color: #ccc;
                    line-height: 1.4;
                }
            </style>
            <div class="game-selector-container">
                <div style="margin-bottom: 40px;">
                    <h1 style="font-size: 3rem; margin-bottom: 10px; text-shadow: 0 0 20px rgba(255,255,255,0.8);">🧊 ALOSU 🧊</h1>
                    <p style="font-size: 1.2rem; opacity: 0.8;">Choose your adventure</p>
                </div>
                <div id="game-cards-container">
                    ${AVAILABLE_GAMES.map(game => `
                        <div class="game-card" data-game="${game.name}">
                            <div class="game-icon">${game.displayName.split(' ')[0]}</div>
                            <div class="game-title">${game.displayName.split(' ').slice(1).join(' ')}</div>
                            <div class="game-description">${game.description}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    // Add click event listeners to game cards
    const gameCards = globalApp.querySelectorAll('.game-card');
    gameCards.forEach(card => {
        card.addEventListener('click', () => {
            const gameName = (card as HTMLElement).dataset.game as GameName;
            if (gameName) {
                startGame(gameName);
            }
        });
    });
}

// =================================================================
// 🎮 游戏启动逻辑
// =================================================================
function startGame(gameName: GameName) {
    if (!globalApp || !globalToken) return;
    
    console.log(`🎮 Starting game: ${gameName}`);
    
    // 显示加载状态
    globalApp.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #000; color: white; font-family: sans-serif;">
            <div style="text-align: center;">
                <div style="font-size: 3rem; animation: spin 1s infinite linear;">🎮</div>
                <h3 style="margin-top: 20px;">Loading ${gameName.toUpperCase()}...</h3>
                <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
            </div>
        </div>
    `;
    
    // 根据配置启动对应游戏
    switch (gameName) {
        case 'blackjack':
            startBlackjackGame();
            break;
        case 'gacha':
            startGachaGame();
            break;
        case 'rocket':
            startRocketGame();
            break;
        default:
            showError(`Unknown game: ${gameName}`);
    }
}

// =================================================================
// 🃏 Blackjack 游戏
// =================================================================
async function startBlackjackGame() {
    if (!globalApp) return;
    
    try {
        // 显示加载状态
        globalApp.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #000; color: white; font-family: sans-serif;">
                <div style="text-align: center;">
                    <div style="font-size: 3rem; animation: spin 1s infinite linear;">🃏</div>
                    <h3 style="margin-top: 20px;">Loading Blackjack...</h3>
                    <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
                </div>
            </div>
        `;

        // 动态导入 Blackjack 游戏模块 (game2)
        const { initGame } = await import('./game2.js');
        
        // 清空容器并启动游戏
        globalApp.innerHTML = '';
        const cleanup = initGame(globalApp, globalToken || '');

        // 添加返回按钮
        addBackButton();

        // 保存清理函数以便后续使用
        (globalApp as any)._gameCleanup = cleanup;

    } catch (error) {
        logger.error('Failed to load Blackjack game', error as Error);
        showError('Failed to load Blackjack game: ' + (error as Error).message);
    }
}

// =================================================================
// 🎲 Gacha 游戏
// =================================================================
async function startGachaGame() {
    if (!globalApp) return;
    
    try {
        // 显示加载状态
        globalApp.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #000; color: white; font-family: sans-serif;">
                <div style="text-align: center;">
                    <div style="font-size: 3rem; animation: spin 1s infinite linear;">🎲</div>
                    <h3 style="margin-top: 20px;">Loading Gacha Game...</h3>
                    <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
                </div>
            </div>
        `;

        // 动态导入 Gacha 游戏模块
        const { initGame } = await import('./gachaGame');
        
        // 清空容器并启动游戏
        globalApp.innerHTML = '';
        const cleanup = initGame(globalApp, globalToken || '');

        // 添加返回按钮
        addBackButton();

        // 保存清理函数以便后续使用
        (globalApp as any)._gameCleanup = cleanup;

    } catch (error) {
        logger.error('Failed to load Gacha game', error as Error);
        showError('Failed to load Gacha game: ' + (error as Error).message);
    }
}

// =================================================================
// 🏪 仓库展示系统
// =================================================================
async function startRocketGame() {
    if (!globalApp) return;
    
    try {
        // 显示加载状态
        globalApp.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #000; color: white; font-family: sans-serif;">
                <div style="text-align: center;">
                    <div style="font-size: 3rem; animation: spin 1s infinite linear;">🏪</div>
                    <h3 style="margin-top: 20px;">Loading Warehouse...</h3>
                    <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
                </div>
            </div>
        `;

        // 动态导入仓库模块
        const { initGame } = await import('./game');
        
        // 清空容器并启动游戏
        globalApp.innerHTML = '';
        const cleanup = initGame(globalApp, globalToken || '');

        // 添加返回按钮
        addBackButton();

        // 保存清理函数以便后续使用
        (globalApp as any)._gameCleanup = cleanup;

    } catch (error) {
        logger.error('Failed to load Warehouse', error as Error);
        showError('Failed to load Warehouse: ' + (error as Error).message);
    }
}

// =================================================================
// 🛠️ 通用工具函数
// =================================================================
function addBackButton() {
    if (!globalApp) return;
    
    // 创建返回按钮
    const backButton = document.createElement('button');
    backButton.innerHTML = '← Back to Games';
    backButton.style.cssText = `
        position: absolute;
        top: 20px;
        left: 20px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        cursor: pointer;
        font-family: 'Orbitron', sans-serif;
        transition: all 0.3s ease;
        z-index: 1000;
    `;
    
    backButton.addEventListener('mouseenter', () => {
        backButton.style.background = 'rgba(255,255,255,0.2)';
        backButton.style.transform = 'translateY(-2px)';
    });
    
    backButton.addEventListener('mouseleave', () => {
        backButton.style.background = 'rgba(255,255,255,0.1)';
        backButton.style.transform = 'translateY(0)';
    });
    
    backButton.addEventListener('click', () => {
        showGameSelector();
    });
    
    // 添加到页面
    globalApp.appendChild(backButton);
}

// =================================================================
// 🛠️ 错误处理
// =================================================================
function showError(message: string) {
    if (!globalApp) return;
    
    globalApp.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #000; color: white; font-family: sans-serif; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 20px; color: #ff6b6b;">❌</div>
            <h2>Error</h2>
            <p style="color: #aaa; margin: 20px 0;">${message}</p>
        </div>
    `;
}

// =================================================================
// 🛠️ 错误处理 UI
// =================================================================
function renderRetryPage(container: HTMLElement, error: any) {
    container.innerHTML = `
        <div style="padding: 2rem; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; background: #0a0a0a; color: white; font-family: monospace; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 10px; color: #ff6b6b;">⚠️</div>
            <h2 style="margin-bottom: 10px;">CONEXIÓN PERDIDA</h2>
            <div style="background: #222; padding: 10px; border-radius: 5px; margin-bottom: 20px; font-size: 0.8rem; color: #aaa; max-width: 80%;">
                ${error instanceof Error ? error.message : String(error)}
            </div>
            <button id="retry-btn" style="background: #5865F2; color: white; border: none; padding: 12px 24px; font-size: 1rem; border-radius: 4px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 10px rgba(88, 101, 242, 0.3);">
                REINTENTAR (RETRY)
            </button>
        </div>
    `;
    
    container.querySelector('#retry-btn')?.addEventListener('click', () => {
        attemptConnection();
    });
}

function renderMaintenancePage(container: HTMLElement, user: { id: string }) {
    container.innerHTML = `<div style="color:red; text-align:center; padding-top:40vh">BLOCKED: ${user.id}</div>`;
}

// 🎬 启动
initializeActivity();