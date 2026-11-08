import { ApiService } from './api';

// ============================================
// 👤 用户名映射表 - 从 database.json 导入
// ============================================
const USER_NAME_MAP: { [userId: string]: string } = {
    '626797305567248398': 'alogenes',
    '708324499371851857': 'neste__',
    '548889602442657812': 'victordps',
    '719465850775535687': 'leo0628',
    '625048928571883526': 'skyltie',
    '686180053159247898': 'vlosfer',
    '805806172665020400': 'the_bluffa_5',
    '618470498015379500': 'juanxoo_06',
    '542729141099823100': '! Oriesu',
};

// ============================================
// Types & Interfaces (Tipos e Interfaces)
// ============================================

interface InventoryItem {
    id: number;
    name: string;
    desc: string;
    rarity: string;
    lvl: number;
    stats: {
        HP: number;
        ATK: number;
        DEF: number;
        SPE: number;
        LCK: number;
    };
    image: string;
}

interface UserData {
    user_id: number;
    username: string;
    balance: number;
    inventory: InventoryItem[];
}

// ============================================
// Helper Functions (Funciones Auxiliares)
// ============================================

function parseInventory(inventoryStr: string | unknown): InventoryItem[] {
    try {
        if (!inventoryStr) return [];
        if (Array.isArray(inventoryStr)) return inventoryStr;
        if (typeof inventoryStr !== 'string') return [];
        
        let parsed = inventoryStr;
        // Remove quotes iteratively
        while ((parsed.startsWith('"') && parsed.endsWith('"')) || (parsed.startsWith("'") && parsed.endsWith("'"))) {
            parsed = parsed.slice(1, -1);
        }
        
        parsed = parsed.replace(/\\"/g, '"').replace(/\\\\/g, '\\');
        const items = JSON.parse(parsed);
        return Array.isArray(items) ? items : [];
    } catch (error) {
        console.error('❌ Failed to parse inventory:', error);
        return [];
    }
}

function getSellValue(rarity: string, lvl: number): number {
    const rarityValues: { [key: string]: number } = {
        'Common': 500, 'Uncommon': 2000, 'Rare': 7000, 'Epic': 15000, 'Legendary': 30000
    };
    const baseValue = rarityValues[rarity] || 500;
    return Math.round(baseValue * lvl / 0.8);
}

function formatNumber(num: number): string {
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(2) + 'K';
    return num.toFixed(0);
}

function getRarityColor(rarity: string): string {
    const rarityColors: { [key: string]: string } = {
        'Common': '#95a5a6',
        'Uncommon': '#2ecc71',
        'Rare': '#3498db',
        'Epic': '#9b59b6',
        'Legendary': '#f39c12'
    };
    return rarityColors[rarity] || '#95a5a6';
}

function getImageUrl(imagePath: string): string {
    if (!imagePath) return '';
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) return imagePath;
    const filename = imagePath.split('/').pop() || imagePath;
    return `/api/alosu/proxy-image/${filename}`;
}

function getRarityNumber(rarity: string): number {
    const rarityMap: { [key: string]: number } = {
        'Common': 1, 'Uncommon': 2, 'Rare': 3, 'Epic': 4, 'Legendary': 5
    };
    return rarityMap[rarity] || 1;
}

// ============================================
// UI Components (Componentes de UI)
// ============================================

/**
 * 创建用户统计面板
 */
function createUserPage(user: UserData): string {
    const items = parseInventory(user.inventory);
    
    // Calculate total value
    const inventoryTotalValue = items.reduce((sum, item) => sum + getSellValue(item.rarity, item.lvl), 0);
    const totalAssets = user.balance + inventoryTotalValue;
    
    const itemsHtml = items.length > 0 
        ? items.map((item, idx) => createGachaStyleCard(item, idx + 1)).join('')
        : '<div class="empty-state">No items found in warehouse</div>';
    
    return `
        <div class="user-page">
            <!-- User Header Panel -->
            <div class="user-header">
                <div class="user-info">
                    <h2 class="username">${user.username}</h2>
                </div>
                
                <div class="stats-container">
                    <div class="stat-card balance">
                        <span class="stat-label">💰 BALANCE</span>
                        <span class="stat-value">${user.balance}</span>
                    </div>
                    <div class="stat-card inventory">
                        <span class="stat-label">📦 INVENTORY</span>
                        <span class="stat-value">${formatNumber(inventoryTotalValue)}</span>
                    </div>
                    <div class="stat-card total">
                        <span class="stat-label">⭐ TOTAL ASSETS</span>
                        <span class="stat-value">${formatNumber(totalAssets)}</span>
                    </div>
                </div>
            </div>

            <!-- Items Grid -->
            <div class="inventory-scroll-area">
                <div class="items-grid">
                    ${itemsHtml}
                </div>
            </div>
        </div>
    `;
}

/**
 * 创建抽卡风格卡片
 * Note: We pass the specific color as a CSS variable in the style attribute
 */
function createGachaStyleCard(item: InventoryItem, index: number = 1): string {
    const color = getRarityColor(item.rarity);
    const imageUrl = getImageUrl(item.image);
    const price = formatNumber(getSellValue(item.rarity, item.lvl));
    const rarityStars = '★'.repeat(getRarityNumber(item.rarity));
    
    // We inject the color as a CSS variable: --item-color
    return `
        <div class="gacha-card" style="--item-color: ${color}">
            <div class="card-bg-overlay"></div>

            <div class="card-image-container">
                <img src="${imageUrl}" alt="${item.name}" loading="lazy">
                <div class="card-index">${index}</div>
            </div>

            <div class="card-content">
                <div class="item-name">${item.name}</div>
                <div class="item-level">Lv.${item.lvl}</div>
                
                <div class="item-stats">
                    <span>❤️ ${item.stats.HP}</span>
                    <span>⚔️ ${item.stats.ATK}</span>
                    <span>🛡️ ${item.stats.DEF}</span>
                    <span>🏃 ${item.stats.SPE}</span>
                    <span>🍀 ${item.stats.LCK}</span>
                </div>

                <div class="item-rarity">${rarityStars}</div>
                
                <div class="item-price">
                    💎 ${price}
                </div>
            </div>
        </div>
    `;
}

// ============================================
// Main Logic (Lógica Principal)
// ============================================

export function initGame(app: HTMLDivElement, accessToken: string) {
    console.log("🎮 Warehouse system loaded!");

    // Inject CSS Styles (Estilos CSS)
    // 使用 CSS 变量和类来减少 HTML 体积并提高可维护性
    app.innerHTML = `
        <style>
            :root {
                --bg-dark: #1a1a1a;
                --panel-bg: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                --text-primary: #ecf0f1;
                --text-secondary: #95a5a6;
                --border-color: #3a3a3a;
                --btn-primary: #3498db;
                --btn-success: #27ae60;
            }

            /* Global Layout */
            .warehouse-app {
                background-color: var(--bg-dark);
                color: var(--text-primary);
                height: 100vh;
                width: 100%;
                padding: 20px;
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                display: flex;
                flex-direction: column;
            }

            .main-container {
                max-width: 1400px;
                width: 100%;
                margin: 0 auto;
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }

            /* Navigation Bar */
            .nav-bar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid var(--border-color);
            }

            .nav-title {
                font-size: 28px;
                margin: 0;
                color: var(--btn-primary);
                font-weight: 700;
            }

            .nav-controls {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .btn {
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.2s;
                color: white;
            }
            .btn:disabled { opacity: 0.5; cursor: not-allowed; }
            .btn:hover:not(:disabled) { filter: brightness(1.1); transform: translateY(-1px); }
            .btn-primary { background: var(--btn-primary); }
            .btn-success { background: var(--btn-success); }
            
            .page-info { color: var(--text-secondary); font-size: 14px; min-width: 100px; text-align: center; }

            /* User Page Layout */
            /* Added width: 100% to fix layout collapse */
            .user-page { display: flex; flex-direction: column; height: 100%; overflow: hidden; width: 100%; }
            
            /* User Header Panel */
            .user-header {
                background: var(--panel-bg);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 20px;
            }
            
            .username { font-size: 24px; margin: 0; color: white; }

            .stats-container { display: flex; gap: 15px; flex-wrap: wrap; }
            
            .stat-card {
                padding: 10px 18px;
                border-radius: 8px;
                text-align: center;
                min-width: 120px;
                border: 2px solid rgba(0,0,0,0.1);
            }
            .stat-card.balance { background: linear-gradient(135deg, #27ae60 0%, #229954 100%); border-color: #1e8449; }
            .stat-card.inventory { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); border-color: #6c3483; }
            .stat-card.total { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); border-color: #d68910; }

            .stat-label { display: block; font-size: 11px; opacity: 0.9; margin-bottom: 4px; font-weight: 700; text-transform: uppercase; }
            .stat-value { font-size: 20px; font-weight: 800; }

            /* Grid Layout */
            .inventory-scroll-area { flex: 1; overflow-y: auto; padding-right: 8px; }
            .inventory-scroll-area::-webkit-scrollbar { width: 8px; }
            .inventory-scroll-area::-webkit-scrollbar-thumb { background: #3a3a3a; border-radius: 4px; }

            .items-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 16px;
                padding-bottom: 20px;
            }

            .empty-state { grid-column: 1/-1; text-align: center; padding: 50px; color: var(--text-secondary); }

            /* Gacha Card Styles */
            .gacha-card {
                /* --item-color is set inline by JS */
                position: relative;
                background: var(--panel-bg);
                border: 2px solid var(--item-color);
                border-radius: 12px;
                padding: 10px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                overflow: hidden;
            }
            
            .gacha-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3), 0 0 10px var(--item-color);
            }

            .card-bg-overlay {
                position: absolute; inset: 0; pointer-events: none;
                background: linear-gradient(to bottom, rgba(255,255,255,0.05), transparent 50%, rgba(0,0,0,0.4));
            }

            .card-image-container {
                position: relative;
                width: 100%;
                aspect-ratio: 1;
                border-radius: 8px;
                overflow: hidden;
                background: #000;
            }
            
            .card-image-container img { width: 100%; height: 100%; object-fit: cover; }
            
            .card-index {
                position: absolute; top: 5px; left: 5px;
                width: 24px; height: 24px;
                background: var(--item-color);
                color: #fff;
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-weight: bold; font-size: 12px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.5);
                z-index: 2;
            }

            .card-content { position: relative; z-index: 1; flex: 1; display: flex; flex-direction: column; }
            
            .item-name {
                color: var(--item-color);
                font-weight: 700; font-size: 16px;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                margin-bottom: 2px;
            }
            
            .item-level { color: var(--text-secondary); font-size: 12px; font-weight: 600; margin-bottom: 6px; }
            
            .item-stats {
                background: rgba(0,0,0,0.3);
                padding: 6px; border-radius: 4px;
                display: grid; grid-template-columns: 1fr 1fr 1fr;
                gap: 2px; font-size: 13px; color: #ddd;
                margin-bottom: 8px;
                font-weight: 600;
            }

            .item-rarity {
                color: var(--item-color);
                text-align: center; font-size: 14px; letter-spacing: 2px;
                margin-bottom: auto;
                text-shadow: 0 0 5px rgba(0,0,0,0.5);
            }

            .item-price {
                margin-top: 8px;
                background: rgba(39, 174, 96, 0.15);
                border: 1px solid #27ae60;
                color: #2ecc71;
                text-align: center;
                padding: 6px; border-radius: 6px;
                font-weight: 700; font-size: 14px;
            }

            /* Loading & Error */
            .loading-container, .error-container {
                flex: 1; display: flex; align-items: center; justify-content: center; font-size: 18px;
            }
            .error-container { color: #e74c3c; background: rgba(231, 76, 60, 0.1); border-radius: 8px; margin: 20px; }
        </style>

        <div class="warehouse-app">
            <div class="main-container">
                <div class="nav-bar">
                    <h1 class="nav-title">🏪 Global Warehouse</h1>
                    <div class="nav-controls">
                        <button id="prev-btn" class="btn btn-primary">← Prev</button>
                        <button id="refresh-btn" class="btn btn-success">🔄 Refresh</button>
                        <span id="page-info" class="page-info">Page 1/1</span>
                        <button id="next-btn" class="btn btn-primary">Next →</button>
                    </div>
                </div>
                
                <div id="loading-container" class="loading-container">
                    ⏳ Loading data...
                </div>
                
                <div id="warehouse-container" style="display: none; flex: 1; overflow: hidden;">
                    <!-- Content injected here -->
                </div>
                
                <div id="error-container" class="error-container" style="display: none;"></div>
            </div>
        </div>
    `;

    loadUsersData(app, accessToken);
}

// ============================================
// Data Loading Logic (Lógica de Datos)
// ============================================

async function loadUsersData(app: HTMLDivElement, accessToken: string) {
    const refs = {
        loading: app.querySelector('#loading-container') as HTMLElement,
        container: app.querySelector('#warehouse-container') as HTMLElement,
        error: app.querySelector('#error-container') as HTMLElement,
        prevBtn: app.querySelector('#prev-btn') as HTMLButtonElement,
        nextBtn: app.querySelector('#next-btn') as HTMLButtonElement,
        refreshBtn: app.querySelector('#refresh-btn') as HTMLButtonElement,
        pageInfo: app.querySelector('#page-info') as HTMLElement,
    };

    try {
        console.log('Loading user data...');
        const users = await ApiService.getAllUsers();
        if (!users || users.length === 0) throw new Error('Failed to load user data');

        if (refs.loading) refs.loading.style.display = 'none';

        // Get current user details
        const currentUserId = localStorage.getItem('discord_user_id') || (window as any).DISCORD_USER_ID || '';
        const currentUsername = localStorage.getItem('discord_username') || (window as any).DISCORD_USERNAME || '';

        // Process data
        let userData: UserData[] = (users as any[]).map((user: any) => {
            const userId = String(user.user_id);
            let displayName = `User ${user.user_id}`; // Default

            // Logic 1: Manual Map
            if (USER_NAME_MAP[userId]) {
                displayName = USER_NAME_MAP[userId]!;
            } 
            // Logic 2: Fuzzy Match
            else {
                const prefix = userId.substring(0, 15);
                const fuzzyMatch = Object.keys(USER_NAME_MAP).find(key => key.startsWith(prefix));
                if (fuzzyMatch) displayName = USER_NAME_MAP[fuzzyMatch]!;
                // Logic 3: Current User
                else if (currentUserId && userId === String(currentUserId)) displayName = currentUsername || user.username || displayName;
                // Logic 4: Backend Name
                else if (user.username) displayName = user.username;
            }
            
            return {
                user_id: user.user_id,
                username: displayName,
                balance: user.balance,
                inventory: parseInventory(user.inventory)
            };
        });

        // Sort by Total Assets
        userData.sort((a, b) => {
            const getVal = (u: UserData) => u.balance + u.inventory.reduce((sum, i) => sum + getSellValue(i.rarity, i.lvl), 0);
            return getVal(b) - getVal(a);
        });

        // Pagination
        let currentPage = 0;
        const renderPage = () => {
            if (refs.container) {
                const user = userData[currentPage];
                refs.container.innerHTML = user ? createUserPage(user) : '';
                // Changed display to 'block' to ensure correct width
                refs.container.style.display = 'block'; 
            }
            
            if (refs.pageInfo) refs.pageInfo.textContent = `Page ${currentPage + 1}/${userData.length}`;
            if (refs.prevBtn) refs.prevBtn.disabled = currentPage === 0;
            if (refs.nextBtn) refs.nextBtn.disabled = currentPage === userData.length - 1;
        };

        // Event Listeners
        refs.prevBtn?.addEventListener('click', () => {
            if (currentPage > 0) { currentPage--; renderPage(); }
        });
        
        refs.nextBtn?.addEventListener('click', () => {
            if (currentPage < userData.length - 1) { currentPage++; renderPage(); }
        });
        
        refs.refreshBtn?.addEventListener('click', () => {
            if (refs.loading) refs.loading.style.display = 'flex';
            if (refs.container) refs.container.style.display = 'none';
            if (refs.error) refs.error.style.display = 'none';
            loadUsersData(app, accessToken);
        });

        renderPage();
        console.log('✅ Warehouse rendered');

    } catch (error) {
        console.error('❌ Load failed:', error);
        if (refs.loading) refs.loading.style.display = 'none';
        if (refs.error) {
            refs.error.style.display = 'block';
            refs.error.textContent = `❌ Error: ${error instanceof Error ? error.message : String(error)}`;
        }
    }
}