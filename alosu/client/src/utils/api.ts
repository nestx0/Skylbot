import type { TokenResponse } from '../types/index';
import { APIError, DiscordSDKError } from '../types/index';
import { logger } from './logger';

/**
 * Sleep utility for retries
 */
export function sleep(ms: number): Promise<void> {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Fetch with retry logic for handling rate limits
 * https://discord.com/developers/docs/topics/rate-limits#rate-limits
 */
export async function fetchAndRetry(
	input: RequestInfo | URL,
	init?: RequestInit,
	nRetries = 3,
): Promise<Response> {
	try {
		const response = await fetch(input, init);

		// Handle rate limiting
		if (response.status === 429 && nRetries > 0) {
			const retryAfter = Number(response.headers.get('retry_after'));
			if (!Number.isNaN(retryAfter)) {
				logger.warn(
					`Rate limited. Retrying after ${retryAfter} seconds`,
				);
				await sleep(retryAfter * 1000);
				return fetchAndRetry(input, init, nRetries - 1);
			}
		}

		if (!response.ok) {
			throw new APIError(
				`API request failed: ${response.statusText}`,
				response.status,
				await response.json().catch(() => null),
			);
		}

		return response;
	} catch (error) {
		if (nRetries <= 0) {
			throw error;
		}

		logger.warn(
			`Request failed, retrying... (${3 - nRetries + 1}/3)`,
		);
		await sleep(1000);
		return fetchAndRetry(input, init, nRetries - 1);
	}
}

/**
 * Get access token from the activity server
 */
export async function getAccessToken(code: string): Promise<string> {
	try {
		logger.info('Exchanging Discord authorization code');
		
		const response = await fetchAndRetry('/api/token', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ code }),
		});

		logger.info('Access token request successful');
		const data = (await response.json()) as TokenResponse;
		
		logger.info('Discord authorization complete');
		return data.access_token;
	} catch (error) {
		logger.error('Failed to get access token', error);
		throw new DiscordSDKError('Failed to authenticate with server');
	}
}

/**
 * Fetch guilds for the current user
 */
export async function fetchUserGuilds(
	accessToken: string,
): Promise<Array<{ id: string; name: string; icon: string | null }>> {
	try {
		const response = await fetchAndRetry(
			'https://discord.com/api/users/@me/guilds',
			{
				headers: {
					Authorization: `Bearer ${accessToken}`,
					'Content-Type': 'application/json',
				},
			},
		);

		return (await response.json()) as Array<{
			id: string;
			name: string;
			icon: string | null;
		}>;
	} catch (error) {
		logger.error('Failed to fetch guilds', error);
		throw error;
	}
}
