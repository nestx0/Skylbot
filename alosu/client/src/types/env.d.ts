/**
 * Environment variable type declarations
 * 
 * This file provides type definitions for environment variables
 * and global objects used throughout the application.
 */

/// <reference types="vite/client" />

// Vite environment variables
interface ImportMetaEnv {
  readonly VITE_DISCORD_CLIENT_ID: string;
  readonly VITE_API_URL?: string;
  readonly VITE_DEBUG?: string;
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly MODE: string;
  readonly BASE_URL: string;
  readonly npm_package_version?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Node.js environment variables
declare namespace NodeJS {
  interface ProcessEnv {
    readonly NODE_ENV?: string;
    readonly ANALYZE?: string;
    readonly npm_package_version?: string;
  }
}

// Global test utilities
declare global {
  function createMockContainer(): HTMLElement;
  function cleanupMockContainer(container: HTMLElement): void;
  
  // Vitest globals
  const beforeEach: (fn: () => void | Promise<void>) => void;
  const afterEach: (fn: () => void | Promise<void>) => void;
  const describe: (name: string, fn: () => void) => void;
  const it: (name: string, fn: () => void | Promise<void>) => void;
  const expect: any;
  const vi: any;
}

// Discord SDK types
declare global {
  interface Window {
    discordSdk?: any;
  }
}

// HTML element dataset extensions
declare global {
  interface DOMStringMap {
    userId?: string;
    game?: string;
    [key: string]: string | undefined;
  }
}

// Memory info for performance monitoring
declare global {
  interface MemoryInfo {
    readonly jsHeapSizeLimit: number;
    readonly totalJSHeapSize: number;
    readonly usedJSHeapSize: number;
  }
  
  interface Performance {
    readonly memory?: MemoryInfo;
  }
}

export {};