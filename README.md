<p align="center"><img src=".claude-plugin/icon.png" alt="webeyes" width="128"></p>

<h1 align="center">webeyes</h1>

<p align="center"><strong>Let Claude Code watch videos: YouTube, TikTok, Instagram reels and 1000+ sites, as a transcript plus frames.</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-d97757?style=for-the-badge" alt="Version 0.1.0">
  <img src="https://img.shields.io/badge/Claude%20Code-plugin-d97757?style=for-the-badge" alt="Claude Code plugin">
  <img src="https://img.shields.io/badge/requires-uv-6c6b85?style=for-the-badge" alt="Requires uv">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-3fb950?style=for-the-badge" alt="MIT License"></a>
</p>

<p align="center">
  🇪🇸 <a href="README-es.md">Español</a>
</p>

<p align="center">
  <a href="#install"><strong>Install</strong></a> ·
  <a href="#usage">Usage</a> ·
  <a href="#options">Options</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#notes">Notes</a>
</p>

---

## What it does

Paste a video link and Claude actually sees it. webeyes downloads the video, reads what is said with timestamps and pulls stills from across the whole clip, so Claude can summarize a talk, break down how a reel is edited, follow a tutorial step by step or check what a clip really shows. It can then zoom into any moment without downloading again.

## Features

- **Any site**: YouTube, TikTok, Instagram reels, X, Twitch, Vimeo, Reddit and [1000+ more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).
- **Transcript with timestamps**: the platform's subtitles when there are any (instant), otherwise [faster-whisper](https://github.com/SYSTRAN/faster-whisper) running on your machine, in any language.
- **Frames**: stills spread evenly across the video, 10 by default, up to 40 per call.
- **Zoom in**: ask again for a section (e.g. seconds 3 to 6 with 15 frames): the video is cached, nothing is downloaded twice.
- **Metadata**: title, author, duration, views, likes, date and description.
- **Zero setup**: ffmpeg, the JavaScript runtime YouTube needs and Whisper install themselves. You only need [uv](https://docs.astral.sh/uv/).
- **Logged-in posts**: optionally uses your browser's session for content that requires login.
- **Self-cleaning cache**: downloaded videos are removed after 7 days.

## Install

Requires [uv](https://docs.astral.sh/uv/):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then, inside Claude Code:

```
/plugin marketplace add SrPirson/webeyes
/plugin install webeyes@webeyes
```

Restart Claude Code (or run `/reload-plugins`) and check that `webeyes` is connected in `/mcp`.

From a terminal:

```bash
claude plugin marketplace add SrPirson/webeyes
claude plugin install webeyes@webeyes
```

**Update**

```bash
claude plugin marketplace update webeyes && claude plugin update webeyes@webeyes
```

**Uninstall**

```bash
claude plugin uninstall webeyes@webeyes
```

## Usage

Just ask in plain words:

```
Watch this reel and tell me how it's edited: https://www.instagram.com/reel/…
Summarize this talk and list the key moments: https://www.youtube.com/watch?v=…
What does the TikTok show between seconds 10 and 15? https://www.tiktok.com/@…/video/…
```

Or use the command:

| Command | Does |
| --- | --- |
| `/webeyes:watch <url>` | Watches the video and summarizes what is said, what is shown and how it is edited |
| `/webeyes:watch <url> <focus>` | Same, focused on what you ask, e.g. `/webeyes:watch <url> the on-screen text` |

### The `watch_video` tool

| Parameter | Default | Meaning |
| --- | --- | --- |
| `url` | — | Video link |
| `frames` | `10` | Number of stills, 1 to 40 |
| `start` / `end` | whole video | Section to sample, in seconds |
| `transcribe` | `true` | Run Whisper when there are no subtitles |
| `width` | `768` | Frame width in pixels |

## Options

Asked when you enable the plugin; change them later in `/plugin` → webeyes → configure.

| Option | Values | Default |
| --- | --- | --- |
| `cookies_browser` | empty, `chrome`, `firefox`, `edge`, `brave`, `chromium`, `safari` | empty |
| `whisper_model` | `tiny`, `base`, `small`, `medium` | `small` |

- **`cookies_browser`**: only needed for posts that require login. yt-dlp reads that browser's cookies locally to act as you.
- **`whisper_model`**: bigger is more accurate and slower. Use `base` if transcription is slow on your CPU.

## How it works

```
URL ──▶ yt-dlp ──▶ video (≤720p, cached 7 days)
                     ├──▶ subtitles ─── or ──▶ faster-whisper ──▶ timestamped transcript
                     └──▶ ffmpeg ──▶ frames
                                                    └──▶ Claude: metadata + transcript + images
```

webeyes is a small MCP server written in Python and launched by uv, which installs its dependencies the first time. Whisper lives in a separate script that is only installed the first time a video without subtitles needs transcribing, so the server starts in about a second.

## Notes

- **First use is slower**: the first video installs the dependencies (~100 MB), and the first one without subtitles also downloads the Whisper model. After that, a reel takes a few seconds.
- **Context**: every frame uses context. The default suits reels; for long videos Claude reads the transcript first and then asks for frames only where they matter.
- **Cache**: `~/.cache/webeyes` (or `$WEBEYES_CACHE`).
- **When a site breaks**: platforms change often and yt-dlp catches up fast. Run `uv cache clean` and restart Claude Code to get the latest version.
- **Privacy**: everything runs on your machine. Only the transcript and frames reach Claude, as part of your conversation. Cookies are sent only to the site the video comes from, just as your browser does.
- Downloading may go against some platforms' terms of service. Use webeyes for content you are allowed to view and analyze.

---

**Author:** [SrPirson](https://github.com/SrPirson) · MIT License
