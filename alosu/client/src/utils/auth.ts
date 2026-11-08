import { discordSdk } from '../discordSdk';
import { logger } from './logger';
import { getAccessToken } from './api';

/**
 * OAuth scopes for the Discord Activity
 * 最基础的权限，绝对不会报错
 */
const OAUTH_SCOPES = [
    // 'applications.commands', // ❌ 删掉它！这个权限在某些 SDK 版本会导致必须传 redirect_uri 的死循环
    'identify',
    // 'rpc.voice.read',      // 🔒 暂时保持注释
];

/**
 * Setup Discord SDK and authenticate
 */
export async function setupDiscordSdk(): Promise<string> {
    try {
        logger.info('Setting up Discord SDK...');

        if (!discordSdk) {
            throw new Error('Discord SDK is not initialized');
        }
        
        logger.info('Waiting for Discord SDK to be ready...');
        await discordSdk.ready();
        logger.info('Discord SDK ready');

        // Request authorization code from Discord client
        logger.info('Requesting authorization from Discord...');
        const authOptions = {
            client_id: import.meta.env.VITE_CLIENT_ID,
            response_type: 'code' as const,
            state: '',
            // 👇 关键：只用最纯净的 scopes，且不要传 redirect_uri
            scope: OAUTH_SCOPES as any, 
            
            // ❌ 彻底删除这一行！RPC 流程禁止传这个参数
            // redirect_uri: ... 
        };
        let code: string;
        try {
            ({ code } = await discordSdk.commands.authorize({ ...authOptions, prompt: 'none' }));
        } catch {
            // First use may require a native Discord consent dialog.
            ({ code } = await discordSdk.commands.authorize(authOptions));
        }

        logger.info('Authorization code received');

        // Exchange authorization code for access token
        logger.info('Exchanging code for access token...');
        const accessToken = await getAccessToken(code);
        logger.info('Access token obtained');

        // Authenticate with Discord client using the access token
        logger.info('Authenticating with Discord client...');
        const auth = await discordSdk.commands.authenticate({
            access_token: accessToken,
        });

        if (!auth) {
            throw new Error('Authentication failed - no auth response');
        }

        logger.info('Successfully authenticated with Discord');
        return accessToken;
        
    } catch (error) {
        logger.error('Failed to setup Discord SDK:', error);
        
        // 提供更详细的错误信息
        if (error instanceof Error) {
            throw new Error(`Discord authentication failed: ${error.message}`);
        } else {
            throw new Error('Discord authentication failed: Unknown error');
        }
    }
}