import { defineConfig, mergeConfig } from 'vite';
import baseConfig from './vite.config.js';

// Production-specific Vite configuration
export default defineConfig((configEnv) => {
    const base = baseConfig(configEnv);
    
    return mergeConfig(base, {
        // Production-specific overrides
        build: {
            // Aggressive optimization for production
            minify: 'esbuild',
            sourcemap: 'hidden', // Generate sourcemaps but don't expose them
            
            rollupOptions: {
                // Aggressive tree shaking
                treeshake: {
                    moduleSideEffects: false,
                    propertyReadSideEffects: false,
                    unknownGlobalSideEffects: false
                },
                
                output: {
                    // Use the same manual chunks function from base config
                    manualChunks: base.build?.rollupOptions?.output?.manualChunks,
                    
                    // Optimized chunk naming with hashes
                    chunkFileNames: 'assets/js/[name]-[hash].js',
                    assetFileNames: (assetInfo) => {
                        const info = assetInfo.name?.split('.') || [];
                        const ext = info[info.length - 1];
                        
                        if (/\.(css)$/.test(assetInfo.name || '')) {
                            return 'assets/css/[name]-[hash][extname]';
                        }
                        
                        if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name || '')) {
                            return 'assets/images/[name]-[hash][extname]';
                        }
                        
                        if (/\.(mp3|wav|ogg|flac|aac)$/i.test(assetInfo.name || '')) {
                            return 'assets/audio/[name]-[hash][extname]';
                        }
                        
                        return 'assets/[name]-[hash][extname]';
                    },
                    
                    // Note: experimentalMinChunkSize removed as it's not supported in current Vite version
                }
            },
            
            // Production asset optimizations
            assetsInlineLimit: 2048, // Smaller inline limit
            chunkSizeWarningLimit: 1000,
            reportCompressedSize: true,
            
            // CSS optimization
            cssMinify: 'esbuild',
            cssCodeSplit: true
        },
        
        // Production CSS handling
        css: {
            devSourcemap: false,
            modules: {
                generateScopedName: '[hash:base64:8]' // Shorter class names
            }
        },
        
        // Production dependency optimization
        optimizeDeps: {
            force: true,
            esbuildOptions: {
                target: 'es2020'
                // Note: Removed drop console/debugger as it can cause issues
            }
        },
        
        // Production logging
        logLevel: 'warn',
        clearScreen: true,
        
        // Additional production defines
        define: {
            'process.env.NODE_ENV': '"production"',
            __ENABLE_DEBUG__: 'false'
        }
    });
});