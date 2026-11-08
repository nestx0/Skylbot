import { DiscordSDK } from '@discord/embedded-app-sdk';

/**
 * 尝试初始化 Discord SDK
 * 如果在浏览器环境 (非 iframe) 运行，返回 null，防止崩溃
 */
let discordSdkInstance: DiscordSDK | null = null;

// window.parent !== window 意味着我们在 iframe 里 (即 Discord)
if (window.parent !== window) {
  try {
    discordSdkInstance = new DiscordSDK(import.meta.env.VITE_CLIENT_ID);
  } catch (error) {
    console.warn('Failed to initialize DiscordSDK instance:', error);
  }
}

// 导出实例 (在本地浏览器中它是 null)
export const discordSdk = discordSdkInstance;