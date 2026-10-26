# webeyes

Lets Claude Code **watch videos**: YouTube, TikTok, Instagram reels, X, Twitch, Vimeo and
[1000+ sites supported by yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

Claude gets the metadata, a **timestamped transcript** (platform subtitles when there are any,
otherwise [faster-whisper](https://github.com/SYSTRAN/faster-whisper) on your machine) and
**frames** spread across the video. It can then zoom into any section (e.g. seconds 3 to 6 with 15
frames) without downloading again.

## Install

Requires [uv](https://docs.astral.sh/uv/) (everything else, ffmpeg included, installs itself):

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh      # macOS / Linux
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

Then, in Claude Code:

```text
/plugin marketplace add SrPirson/webeyes
/plugin install webeyes@webeyes
```

Restart Claude Code and ask: *"watch this reel: https://www.instagram.com/reel/…"* or use
`/webeyes:watch <url> [what to look for]`.

## Options

Asked when you enable the plugin (change them later in `/plugin`):

| Option | Default | What it does |
|---|---|---|
| `cookies_browser` | empty | Browser whose logged-in session yt-dlp uses (`chrome`, `firefox`, `edge`…). Only needed for posts that require login. |
| `whisper_model` | `small` | `tiny`, `base`, `small`, `medium`. Use `base` if transcription is slow on your CPU. |

## Good to know

- **First use is slower**: the first video installs the dependencies (~100 MB), and the first one
  without subtitles also downloads the Whisper model. After that, a reel takes seconds.
- **Context**: each frame costs context. The default (10 frames) suits reels; for long videos Claude
  reads the transcript first and asks for frames only where they matter.
- **Cache**: videos are kept in `~/.cache/webeyes` (or `$WEBEYES_CACHE`) and deleted after 7 days.
- **Sites change**: when a platform breaks downloads, updating yt-dlp usually fixes it:
  run `uv cache clean` and restart Claude Code (the next start installs the latest versions).
- **Cookies**: `cookies_browser` reads your browser's cookies locally so yt-dlp can act as you. They
  never leave your machine, but only enable it if you need it.
- Downloading may go against some platforms' terms of service. Use it for content you are allowed to
  view and analyze.

## License

MIT
