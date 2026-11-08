/**
 * Discord SDK and authentication types
 */
export interface AuthResponse {
	access_token: string;
	token_type: string;
	expires_in: number;
	refresh_token: string;
	scope: string;
}

export interface TokenResponse {
	access_token: string;
}

/**
 * Guild and Channel types
 */
export interface Guild {
	id: string;
	name: string;
	icon: string | null;
	owner: boolean;
	permissions: string;
	features: string[];
}

export interface Channel {
	id: string;
	name: string;
	type: number;
	guild_id?: string;
	parent_id?: string;
}

/**
 * API error types
 */
export class APIError extends Error {
	constructor(
		message: string,
		public statusCode: number,
		public response?: unknown,
	) {
		super(message);
		this.name = 'APIError';
	}
}

export class DiscordSDKError extends Error {
	constructor(message: string) {
		super(message);
		this.name = 'DiscordSDKError';
	}
}
