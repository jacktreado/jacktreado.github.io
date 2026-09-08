#!/usr/bin/env python3
"""Generate a project's hero clip, hover-loop thumb clip, and poster image
from one high-resolution source .mp4, matching the conventions documented in
README.md section (c) ("Encoding new video/poster assets"). Shells out to
ffmpeg/ffprobe (must be on PATH) — no pip installs needed.

Usage:
    python3 scripts/make_project_media.py highres_movies/yourclip.mp4
    python3 scripts/make_project_media.py highres_movies/yourclip.mp4 --slug yourslug
    python3 scripts/make_project_media.py highres_movies/yourclip.mp4 --dry-run

By default this writes into docs/assets/video/, docs/assets/video/thumbs/, and
docs/assets/img/posters/, using a slug derived from the input filename. It
refuses to overwrite existing files unless --force is given. After a real run
it prints a front-matter snippet (with real pixel dimensions) ready to paste
into a docs/_projects/*.md file.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ASSETS_DIR = REPO_ROOT / "docs" / "assets"

# JPEG -q:v values to try, best quality (smallest number) first, when hunting
# for a poster under --poster-max-size-kb.
POSTER_QUALITY_LADDER = [2, 3, 4, 6, 8, 10, 14, 20, 26, 31]


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if not slug:
        sys.exit(f"error: could not derive a slug from '{text}' — pass --slug")
    return slug


def check_tools():
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        sys.exit(f"error: required tool(s) not found on PATH: {', '.join(missing)}")


def ffprobe_info(path):
    """Return (duration_seconds, width, height) for a media file."""
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-print_format", "json",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-show_entries", "format=duration",
            str(path),
        ],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        sys.exit(f"error: ffprobe failed on {path}:\n{out.stderr.strip()}")
    data = json.loads(out.stdout)
    stream = data["streams"][0]
    duration = float(data["format"]["duration"])
    return duration, int(stream["width"]), int(stream["height"])


def check_output_path(path, force):
    if path.exists() and not force:
        sys.exit(f"error: {path} already exists — pass --force to overwrite")


def run(cmd, dry_run):
    printable = " ".join(str(c) for c in cmd)
    if dry_run:
        print(f"[dry-run] {printable}")
        return
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"error: command failed:\n{printable}\n{result.stderr.strip()}")


def encode_video(input_path, output_path, duration, max_size_mb, width, trim_seconds, dry_run):
    """2-pass encode targeting a file-size budget. `duration` is the source
    clip's full duration; `trim_seconds` (if given) shortens the encode."""
    encode_seconds = min(duration, trim_seconds) if trim_seconds else duration
    target_bitrate = int(max_size_mb * 8_000_000 / encode_seconds * 0.98)

    scale_args = ["-vf", f"scale={width}:-2"] if width else []
    trim_args = ["-t", str(trim_seconds)] if trim_seconds else []

    output_path.parent.mkdir(parents=True, exist_ok=True)
    passlog = output_path.with_suffix("")

    run([
        "ffmpeg", "-y", "-i", str(input_path), *trim_args, *scale_args,
        "-c:v", "libx264", "-b:v", str(target_bitrate), "-preset", "slow",
        "-an", "-pass", "1", "-passlogfile", str(passlog),
        "-f", "mp4", "/dev/null",
    ], dry_run)
    run([
        "ffmpeg", "-y", "-i", str(input_path), *trim_args, *scale_args,
        "-c:v", "libx264", "-b:v", str(target_bitrate), "-preset", "slow",
        "-an", "-pass", "2", "-passlogfile", str(passlog),
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(output_path),
    ], dry_run)

    for logfile in output_path.parent.glob(f"{passlog.name}-0.log*"):
        logfile.unlink()


def extract_poster(input_path, output_path, max_size_kb, width, dry_run):
    scale = f",scale={width}:-2" if width else ""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    max_bytes = max_size_kb * 1024

    if dry_run:
        run([
            "ffmpeg", "-y", "-i", str(input_path),
            "-vf", f"select=eq(n\\,0){scale}", "-vsync", "vfr", "-frames:v", "1",
            "-q:v", str(POSTER_QUALITY_LADDER[0]), str(output_path),
        ], dry_run=True)
        return

    for q in POSTER_QUALITY_LADDER:
        run([
            "ffmpeg", "-y", "-i", str(input_path),
            "-vf", f"select=eq(n\\,0){scale}", "-vsync", "vfr", "-frames:v", "1",
            "-q:v", str(q), str(output_path),
        ], dry_run=False)
        if output_path.stat().st_size <= max_bytes or q == POSTER_QUALITY_LADDER[-1]:
            if output_path.stat().st_size > max_bytes:
                print(
                    f"warning: poster is {output_path.stat().st_size / 1024:.0f} KB, "
                    f"over the {max_size_kb:.0f} KB budget even at lowest quality"
                )
            return


def display_path(path):
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def fmt_size(num_bytes):
    if num_bytes >= 1_000_000:
        return f"{num_bytes / 1_000_000:.2f} MB"
    return f"{num_bytes / 1024:.0f} KB"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("input", type=Path, help="path to the high-resolution source .mp4")
    parser.add_argument("--slug", help="output filename stem (default: derived from input filename)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ASSETS_DIR,
                         help="base assets dir (default: docs/assets)")

    parser.add_argument("--hero-max-size-mb", type=float, default=3.0)
    parser.add_argument("--hero-max-width", type=int, default=None,
                         help="cap hero width in px (default: keep source resolution)")

    parser.add_argument("--thumb-max-size-mb", type=float, default=0.4)
    parser.add_argument("--thumb-width", type=int, default=640)
    parser.add_argument("--thumb-duration", type=float, default=6.0)

    parser.add_argument("--poster-max-size-kb", type=float, default=80.0)

    parser.add_argument("--skip-hero", action="store_true")
    parser.add_argument("--skip-thumb", action="store_true")
    parser.add_argument("--skip-poster", action="store_true")
    parser.add_argument("--force", action="store_true", help="overwrite existing output files")
    parser.add_argument("--dry-run", action="store_true", help="print ffmpeg commands without running them")
    args = parser.parse_args()

    check_tools()
    if not args.input.is_file():
        sys.exit(f"error: input file not found: {args.input}")

    slug = args.slug or slugify(args.input.stem)
    hero_path = args.output_dir / "video" / f"{slug}.mp4"
    thumb_path = args.output_dir / "video" / "thumbs" / f"{slug}.mp4"
    poster_path = args.output_dir / "img" / "posters" / f"{slug}.jpg"

    for path, skip in ((hero_path, args.skip_hero), (thumb_path, args.skip_thumb), (poster_path, args.skip_poster)):
        if not skip and not args.dry_run:
            check_output_path(path, args.force)

    duration, src_width, src_height = ffprobe_info(args.input)
    print(f"source: {args.input} ({src_width}x{src_height}, {duration:.1f}s)")

    if not args.skip_hero:
        encode_video(
            args.input, hero_path, duration,
            args.hero_max_size_mb, args.hero_max_width, trim_seconds=None,
            dry_run=args.dry_run,
        )
    if not args.skip_thumb:
        encode_video(
            args.input, thumb_path, duration,
            args.thumb_max_size_mb, args.thumb_width, trim_seconds=args.thumb_duration,
            dry_run=args.dry_run,
        )
    if not args.skip_poster:
        extract_poster(
            args.input, poster_path, args.poster_max_size_kb, args.hero_max_width,
            dry_run=args.dry_run,
        )

    if args.dry_run:
        print("\n[dry-run] no files were written")
        return

    print()
    hero_video_url = poster_url = thumb_video_url = None
    if not args.skip_hero:
        _, hw, hh = ffprobe_info(hero_path)
        hero_video_url = f"/assets/video/{slug}.mp4"
        print(f"wrote {display_path(hero_path)}  ({hw}x{hh}, {fmt_size(hero_path.stat().st_size)})")
    if not args.skip_thumb:
        _, tw, th = ffprobe_info(thumb_path)
        thumb_video_url = f"/assets/video/thumbs/{slug}.mp4"
        print(f"wrote {display_path(thumb_path)}  ({tw}x{th}, {fmt_size(thumb_path.stat().st_size)})")
    if not args.skip_poster:
        poster_url = f"/assets/img/posters/{slug}.jpg"
        print(f"wrote {display_path(poster_path)}  ({fmt_size(poster_path.stat().st_size)})")

    if not (args.skip_hero or args.skip_thumb or args.skip_poster):
        print("\nfront matter:\n")
        print(f"hero_video:  {hero_video_url}")
        print(f"hero_poster: {poster_url}")
        print(f"hero_width:  {hw}")
        print(f"hero_height: {hh}")
        print()
        print(f"thumb_video:  {thumb_video_url}")
        print(f"thumb_poster: {poster_url}")
        print(f"thumb_width:  {tw}")
        print(f"thumb_height: {th}")


if __name__ == "__main__":
    main()
