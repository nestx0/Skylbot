import { discordSdk } from '../discordSdk';
import { logger } from './logger';
import { fetchUserGuilds } from './api';

/**
 * Render channel name in the UI
 */
export async function renderChannelInfo(accessToken: string): Promise<void> {
	const app = document.querySelector<HTMLDivElement>('#app');
	if (!app) {
		throw new Error('Could not find #app element');
	}

	let channelName = 'Unknown';

	try {
		// Requesting channel in GDMs requires dm_channels.read scope
		if (discordSdk.channelId && discordSdk.guildId) {
			const channel = await discordSdk.commands.getChannel({
				channel_id: discordSdk.channelId,
			});

			if (channel.name) {
				channelName = channel.name;
			}
		}

		const textElement = document.createElement('p');
		textElement.textContent = `Activity Channel: "${channelName}"`;
		textElement.className = 'channel-info';
		app.appendChild(textElement);

		logger.info(`Rendered channel info: ${channelName}`);
	} catch (error) {
		logger.error('Failed to render channel info', error);
	}
}

/**
 * Render guild avatar in the UI
 */
export async function renderGuildAvatar(
	accessToken: string,
): Promise<void> {
	const app = document.querySelector<HTMLDivElement>('#app');
	if (!app) {
		throw new Error('Could not find #app element');
	}

	try {
		const guilds = await fetchUserGuilds(accessToken);

		const currentGuild = guilds.find(
			(guild) => guild.id === discordSdk.guildId,
		);

		if (currentGuild?.icon) {
			const guildImg = document.createElement('img');
			const iconUrl = `https://cdn.discordapp.com/icons/${currentGuild.id}/${currentGuild.icon}.webp?size=128`;

			guildImg.setAttribute('src', iconUrl);
			guildImg.setAttribute('width', '128px');
			guildImg.setAttribute('height', '128px');
			guildImg.setAttribute('alt', `${currentGuild.name} icon`);
			guildImg.setAttribute('style', 'border-radius: 50%;');

			// Add error handling
			guildImg.onerror = () => {
				logger.error(`Failed to load guild avatar from ${iconUrl}`);
			};

			app.appendChild(guildImg);
			logger.info(`Rendered guild avatar for ${currentGuild.name}`);
		}
	} catch (error) {
		logger.error('Failed to render guild avatar', error);
	}
}
