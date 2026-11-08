# Alosu integrado en Skylbot

- `client/`: interfaz de Discord con TypeScript y Vite.
- `api.py`: blueprint Flask; OAuth, sesión, economia, gacha, imágenes, Blackjack y puntuaciones.
- `runtime/`: datos de puntuación escritos al ejecutar (ignorado por Git).
- `tests/`: pruebas de integración de Flask con SQLite temporal.

Ejecuta `npm ci && npm run build` en `client/` tras crear `.env.local` con `VITE_CLIENT_ID`.
`main.py` registra el blueprint mediante `register_alosu(app)`.
Consulta las instrucciones de la raíz del paquete para instalación y desplegado.
