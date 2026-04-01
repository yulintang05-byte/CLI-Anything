# Clipper — Agent-Native Video Clipping Tool

**cli-anything harness for video clipping** — Create highlight clips from stream recordings and videos, export to YouTube Shorts, TikTok, Twitch, Twitter, and more.

## Installation

```bash
cd clipper/agent-harness
pip install -e .
```

Requires: Python 3.10+, `click`, `ffmpeg` (system install)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
apt install ffmpeg
```

## Quick Start

```bash
# Create a project
python3 -m cli_anything.clipper project new --name my_clips -o clips.json

# Import a video source
python3 -m cli_anything.clipper --project clips.json source add stream_recording.mp4

# Add a clip (seconds or HH:MM:SS.mmm)
python3 -m cli_anything.clipper --project clips.json clip add \
  --source src0 --in 00:01:05.000 --out 00:01:35.000 --name "Epic moment"

# Export a single clip
python3 -m cli_anything.clipper --project clips.json export clip clip0 -o epic.mp4

# Export all clips as a highlight reel
python3 -m cli_anything.clipper --project clips.json export compile -o reel.mp4 --preset tiktok
```

## Interactive REPL

```bash
python3 -m cli_anything.clipper
# or with a project pre-loaded:
python3 -m cli_anything.clipper --project clips.json
```

## JSON Mode (for AI agents)

All commands support `--json` for machine-readable output:

```bash
python3 -m cli_anything.clipper --json project info
python3 -m cli_anything.clipper --json --project clips.json clip list
python3 -m cli_anything.clipper --json export presets
```

---

## Command Reference

### `project`

| Command | Description |
|---------|-------------|
| `project new --name NAME [--profile PROFILE] [-o PATH]` | Create a new project |
| `project open PATH` | Open an existing project file |
| `project save [PATH]` | Save the current project |
| `project info` | Show project statistics |
| `project profiles` | List available video profiles |

**Profiles:** `hd1080p30` (default), `hd1080p60`, `hd720p30`, `hd720p60`, `vertical1080p`, `vertical720p`, `square1080p`, `4k30`

### `source`

| Command | Description |
|---------|-------------|
| `source add PATH [--name NAME]` | Import a video file |
| `source remove SOURCE_ID` | Remove a source (fails if clips reference it) |
| `source list` | List all sources |
| `source probe PATH` | Probe a file without importing |

### `clip`

| Command | Description |
|---------|-------------|
| `clip add --source SRC_ID --in TC --out TC [--name NAME]` | Define a clip segment |
| `clip trim CLIP_ID [--in TC] [--out TC]` | Adjust in/out points |
| `clip remove CLIP_ID` | Remove a clip |
| `clip list` | List all clips in compilation order |
| `clip show CLIP_ID` | Show detailed clip info |
| `clip move CLIP_ID INDEX` | Reorder clip in compilation |
| `clip label CLIP_ID LABEL` | Tag a clip with a label |

**Timecode formats:** `10.5`, `1:30`, `00:01:30.500`, `90f` (frames at 30fps)

### `filter`

| Command | Description |
|---------|-------------|
| `filter add CLIP_ID FILTER [--params JSON]` | Add a filter |
| `filter remove CLIP_ID INDEX` | Remove a filter by index |
| `filter set CLIP_ID INDEX PARAM VALUE` | Update a filter parameter |
| `filter list CLIP_ID` | List clip's filters |
| `filter available [--category CAT]` | List available filters |
| `filter info FILTER_NAME` | Show filter parameters |

**Available filters:** `brightness`, `contrast`, `saturation`, `blur`, `fade_in`, `fade_out`, `crop`, `scale`, `speed`, `volume`, `mute`

**Categories:** `color`, `video`, `audio`, `geometry`, `time`, `transition`

### `export`

| Command | Description |
|---------|-------------|
| `export clip CLIP_ID -o PATH [--preset PRESET]` | Render a single clip |
| `export compile -o PATH [--preset PRESET]` | Render all clips concatenated |
| `export presets` | List export presets |
| `export preset-info PRESET` | Show preset details |

**Presets:** `hd_mp4` (default), `youtube_short`, `tiktok`, `twitch_clip`, `twitter`, `instagram`, `prores`, `lossless`, `gif`, `audio_only`

### `session`

| Command | Description |
|---------|-------------|
| `session undo` | Undo last operation |
| `session redo` | Redo last undone operation |
| `session status` | Show undo/redo counts, modified flag |
| `session history` | Show undo history |

---

## Example Workflows

### Stream highlight reel
```bash
# Import VOD
python3 -m cli_anything.clipper --project vod.json source add vod_2024.mp4

# Mark highlights
python3 -m cli_anything.clipper --project vod.json clip add --source src0 --in 00:12:05 --out 00:12:25 --name "First kill"
python3 -m cli_anything.clipper --project vod.json clip add --source src0 --in 00:45:10 --out 00:45:40 --name "Clutch play"

# Add fades
python3 -m cli_anything.clipper --project vod.json filter add clip0 fade_in --params '{"duration": 0.5}'
python3 -m cli_anything.clipper --project vod.json filter add clip0 fade_out --params '{"duration": 0.5}'

# Export for TikTok
python3 -m cli_anything.clipper --project vod.json export compile -o highlights.mp4 --preset tiktok
```

### Color grade a clip
```bash
python3 -m cli_anything.clipper --project p.json filter add clip0 brightness --params '{"level": 0.05}'
python3 -m cli_anything.clipper --project p.json filter add clip0 contrast --params '{"level": 1.1}'
python3 -m cli_anything.clipper --project p.json filter add clip0 saturation --params '{"level": 1.2}'
python3 -m cli_anything.clipper --project p.json export clip clip0 -o graded.mp4
```

---

## Project File Format

Projects are stored as JSON (`.json`):

```json
{
  "version": "1.0",
  "name": "my_clips",
  "profile": {"name": "hd1080p30", "width": 1920, "height": 1080, "fps": 30},
  "sources": [
    {"id": "src0", "name": "vod.mp4", "path": "/abs/path/vod.mp4", "duration": 7200.0}
  ],
  "clips": [
    {
      "id": "clip0", "source_id": "src0", "name": "Highlight",
      "in": 65.0, "out": 85.0, "filters": [], "label": ""
    }
  ],
  "metadata": {}
}
```

---

## Running Tests

```bash
cd clipper/agent-harness
# Unit tests (no media required)
pytest tests/test_core.py -v

# E2E tests (requires ffmpeg + test video at /root/clipper/test.mp4)
pytest tests/test_full_e2e.py -v

# All tests
pytest tests/ -v
```

---

## Architecture

```
cli_anything/clipper/
├── clipper_cli.py      # Click CLI + REPL (main entry point)
├── core/
│   ├── session.py      # Undo/redo state management
│   ├── project.py      # Project lifecycle + profiles
│   ├── clips.py        # Source + clip management (ffprobe)
│   ├── filters.py      # Filter registry + application
│   └── export.py       # ffmpeg rendering + presets
└── utils/
    ├── time.py         # Timecode parsing/formatting
    └── repl_skin.py    # REPL UI (colors, prompts, tables)
```
