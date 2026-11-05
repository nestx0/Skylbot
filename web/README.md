# Skylbot — web

Sitio estático para presentar el bot, explicar los comandos y acceder a la autorización oficial de Discord. Todo el código de esta web está bajo `web/`. No necesita el servidor Python para mostrar páginas o ejecutar las demos.

## Ejecutar localmente

Desde la raíz del repositorio:

```bash
python3 -m http.server 8080 --directory web
```

Abrir `http://127.0.0.1:8080/`. Para probar la web bajo una subruta, servirla como `.../Skylbot/web/`. Los CSS, scripts, iconos y enlaces internos usan rutas relativas, tanto en la portada como en las páginas interiores.

## Incluido

- Portada gaming sobria y responsive.
- Catálogo de 28 comandos, incluidos `*shop`, `*plantinv`, `*water` y `*sellplant`, con búsqueda por categoría.
- Simulaciones locales de balance, trabajo, blackjack, ruleta, piedra-papel-tijera, gacha e inventario. La simulación no se conecta a Discord ni modifica el saldo del bot.
- Sección `catpital/` sobre [Catpital](https://github.com/Alogenes/Catpital), proyecto independiente con integración de economía prevista.
- `robots.txt`, `sitemap.xml`, Open Graph, manifest y políticas.

## Antes de publicar

1. Sustituir `https://skylbot.example` por el dominio definitivo en la canonical de las páginas HTML, metadatos Open Graph, `sitemap.xml` y `robots.txt`.
2. Configurar el **Client ID de Skylbot** en los botones de invitación (actualmente deshabilitados). No utilizar el Client ID de Catpital ni introducir secretos en el frontend.
3. Revisar los textos legales y el responsable del sitio.
4. Servir la carpeta `web/` como raíz del hosting, o publicarla en una subcarpeta que conserve la estructura. No mover los archivos CSS ni JS por separado.

Los endpoints económicos del bot Python no están autenticados para acceso público; no se llaman desde esta web. La integración Catpital–Skylbot depende de configuración externa y no se presenta como disponible por defecto.

## Comprobación rápida

```bash
python3 web/tests/check_assets.py
```

Este test comprueba que los enlaces a recursos locales resuelven desde cada página sin depender de la raíz del dominio.
