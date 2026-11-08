// api.ts

// 使用相对 URL 以绕过 Discord iframe 的 CSP
// 在 Discord iframe 中，/api 会相对于当前域名请求
const BASE_URL = ``; // 空字符串 = 使用相对 URL

// 👇 2. 模拟模式开关
// ⚠️ 设为 FALSE，因为我们要连接真实后端获取那些 inventory 数据
const MOCK_MODE = false;

export interface UserData {
    id: string;
    name: string;
}

export interface DrawResult {
    success: boolean;
    error?: string;
    balance?: number;
    pity5?: number;
    pity4?: number;
    goldCount?: number;
    results?: Array<{
        name: string;
        rarity: 1 | 2 | 3 | 4 | 5;
        element: string;
        isNew: boolean;
    }>;
}

export interface PullResult {
    status: 'success' | 'error';
    error?: string;
    message?: string;
    pulls?: number;
    results?: Array<{
        index: number;
        name: string;
        rarity: 1 | 2 | 3 | 4 | 5;
        element: string;
        isNew: boolean;
        stars: string;
    }>;
    summary?: {
        new_balance: number;
        total_cost: number;
        pity5: number;
        pity4: number;
        goldCount: number;
    };
    balance?: number;
}

export const ApiService = {
    /**
     * 获取用户列表
     * 后端会在此步骤去数据服务器拉取最新数据并缓存
     */
    async getAllUsers(userId?: string): Promise<UserData[] | null> {
        if (MOCK_MODE) {
            return [{ id: '1', name: 'Traveler (Mock)' }];
        }

        let url = `${BASE_URL}/api/alosu/all_users`;
        if (userId) {
            url += `?userId=${encodeURIComponent(userId)}`;
        }
        const controller = new AbortController();
        const timeoutId = window.setTimeout(() => controller.abort(), 8000);
        try {
            console.log('%c[API] Fetching users from: ' + url, 'color: #FFD700; font-weight: bold;');
            const response = await fetch(url, { signal: controller.signal });
            console.log('%c[API] Users response status:', 'color: #4ecdc4', response.status, response.statusText);
            
            if (!response.ok) {
                console.error('%c[API] ❌ Server error', 'color: #ff6b6b; font-weight: bold;', response.status);
                const errorText = await response.text();
                console.error('%c[API] Error details:', 'color: #ff6b6b', errorText);
                return null;
            }
            const data = await response.json();
            console.log('%c[API] Users response:', 'color: #4ecdc4', data);
            console.log('%c[API] Response type:', 'color: #FFD700', Array.isArray(data) ? 'array' : typeof data);
            
            if (Array.isArray(data)) {
                console.log('%c[API] ✅ Returned array with', 'color: #51cf66', data.length, 'users');
                if (data.length > 0) {
                    console.log('%c[API] First user:', 'color: #51cf66', data[0]);
                }
                return data as UserData[];
            }
            console.warn('%c[API] ⚠️ Data is not array:', 'color: #FFD700', data);
            return null;
        } catch (e) {
            const message = e instanceof DOMException && e.name === 'AbortError'
                ? 'Request timed out'
                : (e instanceof Error ? e.message : String(e));
            console.error("%c[API] ❌ Fetch error:", 'color: #ff6b6b; font-weight: bold;', message);
        } finally {
            window.clearTimeout(timeoutId);
        }
        return null;
    },

    /**
     * 获取余额
     */
    async getBalance(_userId: string): Promise<{ balance: number | null; fallback: boolean }> {
        if (MOCK_MODE) return { balance: 16000, fallback: false };

        const url = `${BASE_URL}/api/alosu/balance`;
        try {
            console.log('%c[API] Fetching balance from: ' + url, 'color: #FFD700; font-weight: bold;');
            const response = await fetch(url);
            console.log('%c[API] Balance response status:', 'color: #4ecdc4', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('%c[API] Balance data:', 'color: #4ecdc4', data);
                const balance = typeof data === 'object' ? Number(data.balance) : Number(data);
                const fallback = typeof data === 'object' && data?.fallback === true;
                console.log('%c[API] ✅ Parsed balance:', 'color: #51cf66', balance);
                return { balance, fallback };
            }
            console.error('%c[API] ❌ Balance fetch failed, status:', 'color: #ff6b6b; font-weight: bold;', response.status);
        } catch (e) {
            console.error("%c[API] ❌ Balance error:", 'color: #ff6b6b; font-weight: bold;', e);
        }
        return { balance: null, fallback: false };
    },

    /**
     * 核心：抽卡函数（Pull 风格）
     * Se asocia a la cuenta Discord autenticada en servidor; no se usa el userId del cliente.
     */
    async pull(_userId: string, amount: number = 1): Promise<PullResult | null> {
        if (MOCK_MODE) {
            await new Promise(r => setTimeout(r, 500));
            return { status: 'error', error: 'Mock disabled' };
        }

        const url = `${BASE_URL}/api/alosu/gacha/pull`; 
        
        try {
            console.log('%c[API] Sending gacha pull request:', 'color: #FFD700; font-weight: bold;');
            console.log(`   URL: ${url}`);
            console.log(`   Amount: ${amount}`);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount })
            });

            console.log(`%c[API] Pull response status: ${response.status}`, 'color: #4ecdc4');
            
            if (response.ok) {
                const data = await response.json() as PullResult;
                console.log('%c[API] ✅ Pull successful:', 'color: #51cf66');
                console.log(`   Status: ${data.status}`);
                console.log(`   Results: ${data.results?.length} items`);
                if (data.summary) {
                    console.log(`   New Balance: ${data.summary.new_balance}`);
                    console.log(`   Pity 5: ${data.summary.pity5}, Pity 4: ${data.summary.pity4}`);
                }
                return data;
            } else {
                const data = await response.json();
                console.error(`%c[API] ❌ Pull failed (${response.status}):`, 'color: #ff6b6b; font-weight: bold;', data);
                return data;
            }
        } catch (e) {
            console.error("%c[API] ❌ Pull error:", 'color: #ff6b6b; font-weight: bold;', e);
            return null;
        }
    },

    /**
     * 核心：抽卡函数（Draw 风格，保留向后兼容）
     * 直接发送请求给后端，后端处理扣费和随机
     */
    async draw(_userId: string, amount: number): Promise<DrawResult | null> {
        if (MOCK_MODE) {
            await new Promise(r => setTimeout(r, 500));
            // Mock logic omitted for brevity
            return { success: false, error: 'Mock disabled' };
        }

        const url = `${BASE_URL}/api/alosu/gacha/pull`; 
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount })
            });

            if (response.ok) {
                const data = await response.json();
                return { success: data.status === "success", ...data };
            } else {
                console.error(`[!] Server Error: ${response.status}`);
                return { success: false, error: `Server error ${response.status}` };
            }
        } catch (e) {
            console.error("[!] Network Error:", e);
            return { success: false, error: 'Network connection failed' };
        }
    }
};