# Clipper — Tool SOP

## Overview

Clipper is an agent-native video clipping harness built on the cli-anything methodology. It uses **ffmpeg** as its rendering backend and **ffprobe** for media inspection.

**Use case:** Create highlight clips from stream recordings (Twitch, YouTube, etc.) and export them for social platforms (TikTok, Shorts, Twitter/X, Instagram).

## Backend Analysis

| Concern | Solution |
|---------|----------|
| Media probing | `ffprobe -print_format json -show_streams -show_format` |
| Single clip render | `ffmpeg -ss <in> -i <src> -t <dur> -c:v libx264 -c:a aac <out>` |
| Compilation | Render segments → concat via `ffmpeg -f concat -safe 0` |
| Filter chain | Project filter spec → ffmpeg `-vf` / `-af` string |
| Undo/redo | `copy.deepcopy()` snapshots of the JSON project dict |

## Setup

```bash
# System dependency
brew install ffmpeg        # macOS
apt install ffmpeg         # Ubuntu

# Python package
cd clipper/agent-harness
pip install -e .

# Verify
ffmpeg -version
python3 -m cli_anything.clipper --help
```

## Project State

The project is a single JSON file with four top-level arrays: `sources`, `clips`, `metadata`, and `profile`. All mutations snapshot state before modifying.

```
project.json
  ├── profile   — video dimensions + FPS
  ├── sources[] — imported video files (probed by ffprobe)
  └── clips[]   — segments referencing sources with in/out points + filters
```

## Filter Translation

Project filter specs are translated to ffmpeg filter strings in `export.py`:

| Filter | ffmpeg equivalent |
|--------|------------------|
| `brightness` | `eq=brightness=X` |
| `contrast` | `eq=contrast=X` |
| `saturation` | `eq=saturation=X` |
| `blur` | `boxblur=R:R` |
| `fade_in` | `fade=t=in:st=0:d=D` + `afade=t=in:st=0:d=D` |
| `fade_out` | `fade=t=out:st=S:d=D` + `afade=t=out:st=S:d=D` |
| `crop` | `crop=W:H:X:Y` |
| `scale` | `scale=W:H` |
| `speed` | `setpts=F*PTS` + `atempo=X` (chained for >2.0) |
| `volume` | `volume=X` |
| `mute` | `volume=0` |

`brightness`, `contrast`, and `saturation` are merged into a single `eq=` filter to avoid ffmpeg duplicate filter errors.

## Known Limitations

1. **Speed < 0.5 or > 2.0:** `atempo` must be chained (handled automatically).
2. **GIF preset:** No audio supported.
3. **Compilation:** Uses `-c copy` after per-segment encoding, so all segments must use the same codec and container.
4. **Large files:** `ffprobe` timeout is 30s. Very large files may fail on slow storage.

## Example Workflows

### Typical stream clip workflow
```bash
clipper project new --name stream_highlights -o h.json
clipper --project h.json source add /path/to/stream.mp4
clipper --project h.json clip add --source src0 --in 00:12:05 --out 00:12:35 --name "Clutch"
clipper --project h.json filter add clip0 fade_in --params '{"duration": 0.5}'
clipper --project h.json filter add clip0 fade_out --params '{"duration": 0.5}'
clipper --project h.json export clip clip0 -o clutch.mp4 --preset twitch_clip
```

### Highlight reel for TikTok/Shorts
```bash
clipper --project h.json clip add --source src0 --in 22:10 --out 22:25
clipper --project h.json clip add --source src0 --in 45:30 --out 45:50
clipper --project h.json export compile -o reel.mp4 --preset tiktok
```

## Test Video

Place a test video at `/root/clipper/test.mp4` to enable E2E tests.

```bash
mkdir -p /root/clipper
# Option 1: Use an existing clip
cp /path/to/video.mp4 /root/clipper/test.mp4

# Option 2: Generate a synthetic test video with ffmpeg
ffmpeg -f lavfi -i "color=c=blue:size=1920x1080:rate=30" \
       -f lavfi -i "sine=frequency=440:sample_rate=44100" \
       -t 30 /root/clipper/test.mp4
```
