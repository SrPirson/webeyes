#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "mcp>=1.2,<2",
#   "yt-dlp[default,curl-cffi]",
#   "deno",
#   "imageio-ffmpeg",
# ]
# ///
"""webeyes: MCP server that lets Claude Code watch videos (YouTube, TikTok, Instagram, X...).

Optional environment variables:
  WEBEYES_COOKIES_BROWSER  chrome | firefox | edge ... (logged-in session for Instagram/TikTok)
  WEBEYES_WHISPER_MODEL    tiny | base | small | medium (default: small)
  WEBEYES_CACHE            cache folder (default: ~/.cache/webeyes)
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import deno
import imageio_ffmpeg
import yt_dlp
from mcp.server.fastmcp import FastMCP, Image

HERE = Path(__file__).resolve().parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()  # bundled ffmpeg: no apt install needed


def _env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    return "" if v.startswith("${") else v  # plugin option left unset arrives unsubstituted


COOKIES_BROWSER = _env("WEBEYES_COOKIES_BROWSER")
WHISPER_MODEL = _env("WEBEYES_WHISPER_MODEL") or "small"
CACHE = Path(os.environ.get("WEBEYES_CACHE") or Path.home() / ".cache" / "webeyes")
CACHE_DAYS = 7
CACHE.mkdir(parents=True, exist_ok=True)
for old in CACHE.iterdir():
    if old.is_dir() and time.time() - old.stat().st_mtime > CACHE_DAYS * 86400:
        shutil.rmtree(old, ignore_errors=True)

mcp = FastMCP("webeyes")


def _mmss(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60:02d}:{sec % 60:02d}"


def _ffmpeg_duration(video: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(video)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def _read_vtt(path: Path) -> str:
    lines, seen, t = [], set(), None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "-->" in line:
            t = line.split("-->")[0].strip().split(".")[0]
            continue
        text = re.sub(r"<[^>]+>", "", line).strip()
        if not text or t is None or text in seen:
            continue
        seen.add(text)
        lines.append(f"[{t}] {text}")
    return "\n".join(lines)


def _download(url: str, folder: Path) -> dict:
    info_path = folder / "info.json"
    if info_path.exists() and _video_file(folder):
        return json.loads(info_path.read_text())

    base = {
        "outtmpl": str(folder / "video.%(ext)s"),
        # max 720p; YouTube only serves separate video+audio, merged with the bundled ffmpeg
        "format": "bv*[height<=720]+ba/b[height<=720]/bv*+ba/b",
        "merge_output_format": "mp4",
        "quiet": True, "no_warnings": True, "noprogress": True, "noplaylist": True,
        "ffmpeg_location": FFMPEG,
        "js_runtimes": {"deno": {"path": deno.find_deno_bin()}},  # YouTube needs a JS runtime
    }
    if COOKIES_BROWSER:
        base["cookiesfrombrowser"] = (COOKIES_BROWSER,)
    with_subs = {**base, "writesubtitles": True, "writeautomaticsub": True,
                 "subtitleslangs": ["es.*", "en.*"], "subtitlesformat": "vtt"}
    try:
        with yt_dlp.YoutubeDL(with_subs) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError:
        # sometimes only the subtitles fail (HTTP 429): retry without them
        with yt_dlp.YoutubeDL(base) as ydl:
            info = ydl.extract_info(url, download=True)

    data = {k: info.get(k) for k in ("title", "uploader", "duration", "upload_date",
                                     "view_count", "like_count", "description", "webpage_url")}
    info_path.write_text(json.dumps(data, ensure_ascii=False))
    return data


def _video_file(folder: Path) -> Path | None:
    return next((p for p in folder.glob("video.*") if p.suffix not in (".vtt", ".part", ".ytdl")), None)


def _transcript(folder: Path, video: Path, transcribe: bool) -> str:
    cache = folder / "transcript.txt"
    if cache.exists():
        return cache.read_text()
    subs = sorted(folder.glob("video.*.vtt"), key=lambda p: (".es" not in p.name, p.name))
    if subs:
        text = "(platform subtitles)\n" + _read_vtt(subs[0])
    elif not transcribe:
        return "(transcription disabled)"
    else:
        # Whisper runs as its own uv script so the server starts fast; its deps install on first use
        uv = os.environ.get("UV") or shutil.which("uv") or "uv"
        r = subprocess.run([uv, "run", "--script", str(HERE / "transcribe.py"), str(video), WHISPER_MODEL],
                           capture_output=True, text=True)
        if r.returncode:
            return f"(no transcript: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'whisper failed'})"
        text = r.stdout.strip()
    cache.write_text(text)
    return text


def _frames(video: Path, start: float, end: float, n: int, width: int, folder: Path):
    out = []
    for i in range(n):
        t = start + (end - start) * (i + 0.5) / n
        img = folder / f"frame_{t:09.2f}_{width}.jpg"
        if not img.exists():
            subprocess.run([FFMPEG, "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
                            "-vf", f"scale='min({width},iw)':-2", "-q:v", "4", "-y", str(img)],
                           capture_output=True)
        if img.exists():
            out.append((t, img))
    return out


@mcp.tool()
def watch_video(url: str, frames: int = 10, start: float = 0, end: float | None = None,
                transcribe: bool = True, width: int = 768) -> list:
    """Watch a video from YouTube, TikTok, Instagram (reels), X, Twitch, Vimeo or any site
    supported by yt-dlp. Returns metadata, a timestamped transcript and `frames` stills spread
    evenly between `start` and `end` (seconds). To study a section in detail, call it again with
    start/end and more frames: the video is cached and not downloaded again. For long videos,
    read the transcript first with few frames, then ask for frames only where they matter."""
    folder = CACHE / hashlib.sha1(url.encode()).hexdigest()[:16]
    folder.mkdir(exist_ok=True)
    folder.touch()  # keeps it out of the cache cleanup while in use
    try:
        info = _download(url, folder)
    except Exception as e:
        hint = "" if COOKIES_BROWSER else (" For Instagram/TikTok, set the plugin option "
                                           "cookies_browser (chrome, firefox...) to use your logged-in session.")
        return [f"Could not download the video: {e}.{hint}"]

    video = _video_file(folder)
    if video is None:
        return ["Download finished but no video file was found."]
    duration = float(info.get("duration") or 0) or _ffmpeg_duration(video)
    end = min(end or duration, duration) if duration else (end or 10)
    n = max(1, min(int(frames), 40))

    header = (f"# {info.get('title') or 'Video'}\n"
              f"Author: {info.get('uploader')} | Duration: {_mmss(duration)} | "
              f"Views: {info.get('view_count')} | Likes: {info.get('like_count')} | "
              f"Date: {info.get('upload_date')} | URL: {info.get('webpage_url') or url}\n\n"
              f"## Description\n{(info.get('description') or '').strip()[:2000]}\n\n"
              f"## Transcript\n{_transcript(folder, video, transcribe)}\n\n"
              f"## Frames ({n}, between {_mmss(start)} and {_mmss(end)})")
    result: list = [header]
    for t, path in _frames(video, start, end, n, width, folder):
        result += [f"Frame at {_mmss(t)}", Image(path=str(path))]
    return result


if __name__ == "__main__":
    mcp.run()
