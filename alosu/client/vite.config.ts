import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
    // 指定环境变量文件的位置 (.env 在根目录)
    envDir: './',
    
    base: "/alosu/",
    server: {
        port: 3000,
        host: '0.0.0.0', // 允许所有 IP 访问
        
        // 允许外部域名访问（通过反向代理 HTTPS）
        allowedHosts: true,

        // 代理配置 (让前端能访问后端 API)
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5000',
                changeOrigin: true,
                secure: false,
                ws: true,
            },
        },
    },
});