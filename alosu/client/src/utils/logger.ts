/**
 * Logger utility
 */
type LogLevel = 'debug' | 'info' | 'warn' | 'error';

class Logger {
	private isDevelopment = import.meta.env.DEV;

	private getTimestamp(): string {
		return new Date().toISOString();
	}

	private log(level: LogLevel, message: string, data?: unknown): void {
		const timestamp = this.getTimestamp();
		const prefix = `[${timestamp}] [${level.toUpperCase()}]`;

		if (data) {
			console[level === 'error' ? 'error' : 'log'](
				`${prefix} ${message}`,
				data,
			);
		} else {
			console[level === 'error' ? 'error' : 'log'](
				`${prefix} ${message}`,
			);
		}
	}

	debug(message: string, data?: unknown): void {
		if (this.isDevelopment) {
			this.log('debug', message, data);
		}
	}

	info(message: string, data?: unknown): void {
		this.log('info', message, data);
	}

	warn(message: string, data?: unknown): void {
		this.log('warn', message, data);
	}

	error(message: string, error?: unknown): void {
		this.log('error', message, error);
	}
}

export const logger = new Logger();
