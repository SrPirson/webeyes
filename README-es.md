<p align="center"><img src=".claude-plugin/icon.png" alt="webeyes" width="128"></p>

<h1 align="center">webeyes</h1>

<p align="center"><strong>Claude Code ve vídeos: YouTube, TikTok, reels de Instagram y más de 1000 webs, como transcripción y fotogramas.</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/versi%C3%B3n-0.1.0-d97757?style=for-the-badge" alt="Versión 0.1.0">
  <img src="https://img.shields.io/badge/Claude%20Code-plugin-d97757?style=for-the-badge" alt="Plugin de Claude Code">
  <img src="https://img.shields.io/badge/requiere-uv-6c6b85?style=for-the-badge" alt="Requiere uv">
  <a href="LICENSE"><img src="https://img.shields.io/badge/licencia-MIT-3fb950?style=for-the-badge" alt="Licencia MIT"></a>
</p>

<p align="center">
  🇬🇧 <a href="README.md">English</a>
</p>

<p align="center">
  <a href="#instalación"><strong>Instalación</strong></a> ·
  <a href="#uso">Uso</a> ·
  <a href="#opciones">Opciones</a> ·
  <a href="#cómo-funciona">Cómo funciona</a> ·
  <a href="#notas">Notas</a>
</p>

---

## Qué hace

Pegas el enlace de un vídeo y Claude lo ve de verdad. webeyes descarga el vídeo, saca lo que se dice con marcas de tiempo y extrae fotogramas de todo el clip, para que Claude pueda resumir una charla, desgranar cómo está editado un reel, seguir un tutorial paso a paso o comprobar qué muestra realmente un vídeo. Después puede acercarse a cualquier momento sin volver a descargarlo.

## Funciones

- **Cualquier web**: YouTube, TikTok, reels de Instagram, X, Twitch, Vimeo, Reddit y [más de 1000](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).
- **Transcripción con marcas de tiempo**: los subtítulos de la plataforma si los hay (al instante) y, si no, [faster-whisper](https://github.com/SYSTRAN/faster-whisper) en tu equipo, en cualquier idioma.
- **Fotogramas**: repartidos por todo el vídeo, 10 por defecto y hasta 40 por llamada.
- **Zoom**: vuelve a pedir un tramo (por ejemplo, del segundo 3 al 6 con 15 fotogramas): el vídeo queda en caché y no se descarga dos veces.
- **Metadatos**: título, autor, duración, vistas, likes, fecha y descripción.
- **Sin configurar nada**: ffmpeg, el runtime de JavaScript que necesita YouTube y Whisper se instalan solos. Solo hace falta [uv](https://docs.astral.sh/uv/).
- **Publicaciones con sesión**: puede usar, si quieres, la sesión de tu navegador para contenido que pide iniciar sesión.
- **Caché que se limpia sola**: los vídeos descargados se borran a los 7 días.

## Instalación

Requiere [uv](https://docs.astral.sh/uv/):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Después, dentro de Claude Code:

```
/plugin marketplace add SrPirson/webeyes
/plugin install webeyes@webeyes
```

Reinicia Claude Code (o ejecuta `/reload-plugins`) y comprueba en `/mcp` que `webeyes` está conectado.

Desde una terminal:

```bash
claude plugin marketplace add SrPirson/webeyes
claude plugin install webeyes@webeyes
```

**Actualizar**

```bash
claude plugin marketplace update webeyes && claude plugin update webeyes@webeyes
```

**Desinstalar**

```bash
claude plugin uninstall webeyes@webeyes
```

## Uso

Pídeselo con tus palabras:

```
Mira este reel y dime cómo está editado: https://www.instagram.com/reel/…
Resume esta charla y dame los momentos clave: https://www.youtube.com/watch?v=…
¿Qué se ve en el TikTok entre el segundo 10 y el 15? https://www.tiktok.com/@…/video/…
```

O usa el comando:

| Comando | Hace |
| --- | --- |
| `/webeyes:watch <url>` | Ve el vídeo y resume lo que se dice, lo que se ve y cómo está editado |
| `/webeyes:watch <url> <enfoque>` | Lo mismo, centrado en lo que pidas, p. ej. `/webeyes:watch <url> el texto en pantalla` |

### La herramienta `watch_video`

| Parámetro | Por defecto | Qué es |
| --- | --- | --- |
| `url` | — | Enlace del vídeo |
| `frames` | `10` | Número de fotogramas, de 1 a 40 |
| `start` / `end` | todo el vídeo | Tramo que se muestrea, en segundos |
| `transcribe` | `true` | Usar Whisper cuando no hay subtítulos |
| `width` | `768` | Ancho de los fotogramas en píxeles |

## Opciones

Se piden al activar el plugin; cámbialas después en `/plugin` → webeyes → configure.

| Opción | Valores | Por defecto |
| --- | --- | --- |
| `cookies_browser` | vacío, `chrome`, `firefox`, `edge`, `brave`, `chromium`, `safari` | vacío |
| `whisper_model` | `tiny`, `base`, `small`, `medium` | `small` |

- **`cookies_browser`**: solo hace falta para publicaciones que piden iniciar sesión. yt-dlp lee en local las cookies de ese navegador para actuar como tú.
- **`whisper_model`**: cuanto más grande, más preciso y más lento. Usa `base` si la transcripción va lenta en tu CPU.

## Cómo funciona

```
URL ──▶ yt-dlp ──▶ vídeo (≤720p, en caché 7 días)
                     ├──▶ subtítulos ─── o ──▶ faster-whisper ──▶ transcripción con tiempos
                     └──▶ ffmpeg ──▶ fotogramas
                                                    └──▶ Claude: metadatos + transcripción + imágenes
```

webeyes es un pequeño servidor MCP en Python que lanza uv, y uv instala sus dependencias la primera vez. Whisper va en un script aparte que solo se instala la primera vez que un vídeo sin subtítulos necesita transcripción, así que el servidor arranca en un segundo.

## Notas

- **La primera vez va más lenta**: el primer vídeo instala las dependencias (~100 MB) y el primero sin subtítulos descarga además el modelo de Whisper. Después, un reel tarda unos segundos.
- **Contexto**: cada fotograma ocupa contexto. El valor por defecto va bien para reels; en vídeos largos Claude lee primero la transcripción y luego pide fotogramas solo donde importan.
- **Caché**: `~/.cache/webeyes` (o `$WEBEYES_CACHE`).
- **Si una web deja de funcionar**: las plataformas cambian a menudo y yt-dlp se pone al día rápido. Ejecuta `uv cache clean` y reinicia Claude Code para tener la última versión.
- **Privacidad**: todo se ejecuta en tu equipo. A Claude solo le llegan la transcripción y los fotogramas, como parte de tu conversación. Las cookies solo se envían a la web de la que sale el vídeo, igual que hace tu navegador.
- Descargar contenido puede ir contra las condiciones de algunas plataformas. Usa webeyes con contenido que puedas ver y analizar.

---

**Autor:** [SrPirson](https://github.com/SrPirson) · Licencia MIT
