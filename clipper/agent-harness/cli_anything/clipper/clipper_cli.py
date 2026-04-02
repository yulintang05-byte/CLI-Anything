"""Clipper CLI - Agent-native video clipping tool.

Provides a full CLI for creating highlight clips from stream recordings and
videos. Designed for AI agents (Claude Code, OpenCode, Codex) and humans alike.

Usage:
    python3 -m cli_anything.clipper [--json] [--project PATH] <command>
    python3 -m cli_anything.clipper  (launches REPL)
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.clipper.core.session import Session
from cli_anything.clipper.core import project as proj_mod
from cli_anything.clipper.core import clips as clips_mod
from cli_anything.clipper.core import filters as filters_mod
from cli_anything.clipper.core import export as export_mod
from cli_anything.clipper.utils.time import parse_timecode, format_duration

# ── Global state ──────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False
_repl_mode: bool = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            click.echo(f"{pad}{k}: [{len(v)} items]")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for item in lst:
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            click.echo("  " + "  ".join(parts))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


# ── Error handling decorator ──────────────────────────────────────────────────

def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, ValueError, IndexError, RuntimeError, KeyError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI group ────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.option(
    "--project", "project_path", default=None,
    help="Path to project file to load on startup"
)
@click.version_option("1.0.0", prog_name="clipper")
@click.pass_context
def cli(ctx: click.Context, use_json: bool, project_path: Optional[str]) -> None:
    """Clipper — agent-native video clipping tool.

    Create highlight clips from stream recordings and videos.
    Export to YouTube Shorts, TikTok, Twitch, Twitter, and more.

    \b
    Quick start:
      clipper project new --name my_clips -o project.json
      clipper --project project.json source add video.mp4
      clipper --project project.json clip add --source src0 --in 10 --out 30
      clipper --project project.json export clip clip0 -o out.mp4
    """
    global _json_output
    _json_output = use_json

    if project_path:
        sess = get_session()
        if not sess.has_project():
            try:
                proj_mod.open_project(sess, project_path)
            except Exception as e:
                _err(str(e))
                if not _repl_mode:
                    sys.exit(1)

    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=project_path)


# ── project group ─────────────────────────────────────────────────────────────

@cli.group()
def project():
    """Project lifecycle commands (new, open, save, info, profiles)."""
    pass


@project.command("new")
@click.option("--name", default="untitled", show_default=True, help="Project name")
@click.option(
    "--profile", default="hd1080p30", show_default=True,
    help="Video profile (run 'project profiles' to list options)"
)
@click.option("-o", "--output", "output_path", default=None, help="Save path (.json)")
@handle_error
def project_new(name: str, profile: str, output_path: Optional[str]) -> None:
    """Create a new empty project."""
    sess = get_session()
    result = proj_mod.new_project(sess, name=name, profile=profile)
    if output_path:
        proj_mod.save_project(sess, output_path)
        result["saved_to"] = output_path
    output(result, f"Created project '{name}' with profile '{profile}'")


@project.command("open")
@click.argument("path")
@handle_error
def project_open(path: str) -> None:
    """Open a project file."""
    sess = get_session()
    result = proj_mod.open_project(sess, path)
    output(result, f"Opened project '{result['name']}' from {path}")


@project.command("save")
@click.argument("path", required=False, default=None)
@handle_error
def project_save(path: Optional[str]) -> None:
    """Save the current project. Uses loaded path if no PATH given."""
    sess = get_session()
    result = proj_mod.save_project(sess, path)
    output(result, f"Saved project to {result['path']}")


@project.command("info")
@handle_error
def project_info() -> None:
    """Show information about the current project."""
    sess = get_session()
    result = proj_mod.project_info(sess)
    output(result, f"Project: {result['name']}")


@project.command("profiles")
@handle_error
def project_profiles() -> None:
    """List available video profiles."""
    result = proj_mod.list_profiles()
    output(result, "Available profiles:")


# ── source group ──────────────────────────────────────────────────────────────

@cli.group()
def source():
    """Source video file management (add, remove, list, probe)."""
    pass


@source.command("add")
@click.argument("path")
@click.option("--name", default=None, help="Override display name for this source")
@handle_error
def source_add(path: str, name: Optional[str]) -> None:
    """Import a video file as a source."""
    sess = get_session()
    result = clips_mod.add_source(sess, path, name)
    output(result, f"Added source '{result['name']}' ({format_duration(result['duration'])})")


@source.command("remove")
@click.argument("source_id")
@handle_error
def source_remove(source_id: str) -> None:
    """Remove a source by ID. Fails if clips reference it."""
    sess = get_session()
    result = clips_mod.remove_source(sess, source_id)
    output(result, f"Removed source '{result['name']}'")


@source.command("list")
@handle_error
def source_list() -> None:
    """List all sources in the project."""
    sess = get_session()
    result = clips_mod.list_sources(sess)
    if not _json_output:
        if not result:
            click.echo("  No sources. Use 'source add <path>' to import a video.")
            return
        from cli_anything.clipper.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Name", "Duration", "Resolution", "FPS"],
            [
                [
                    s["id"],
                    s["name"][:30],
                    s["duration_fmt"],
                    f"{s['video']['width']}x{s['video']['height']}" if s.get("video") else "-",
                    str(s["video"]["fps"]) if s.get("video") else "-",
                ]
                for s in result
            ]
        )
    else:
        output(result)


@source.command("probe")
@click.argument("path")
@handle_error
def source_probe(path: str) -> None:
    """Probe a video file with ffprobe (does not add to project)."""
    result = clips_mod.probe_source(path)
    output(result, f"Probe: {path}")


# ── clip group ────────────────────────────────────────────────────────────────

@cli.group()
def clip():
    """Clip management (add, trim, remove, list, show, move, label)."""
    pass


@clip.command("add")
@click.option("--source", "source_id", required=True, help="Source ID (from 'source list')")
@click.option("--in", "in_point", required=True, help="In point (seconds or HH:MM:SS.mmm)")
@click.option("--out", "out_point", required=True, help="Out point (seconds or HH:MM:SS.mmm)")
@click.option("--name", default=None, help="Clip name")
@handle_error
def clip_add(source_id: str, in_point: str, out_point: str, name: Optional[str]) -> None:
    """Define a new clip segment from a source."""
    sess = get_session()
    in_s = parse_timecode(in_point)
    out_s = parse_timecode(out_point)
    result = clips_mod.add_clip(sess, source_id, in_s, out_s, name)
    output(
        result,
        f"Added clip '{result['name']}' ({format_duration(result['duration'])})"
    )


@clip.command("trim")
@click.argument("clip_id")
@click.option("--in", "in_point", default=None, help="New in point")
@click.option("--out", "out_point", default=None, help="New out point")
@handle_error
def clip_trim(clip_id: str, in_point: Optional[str], out_point: Optional[str]) -> None:
    """Adjust the in/out points of a clip."""
    sess = get_session()
    in_s = parse_timecode(in_point) if in_point is not None else None
    out_s = parse_timecode(out_point) if out_point is not None else None
    result = clips_mod.trim_clip(sess, clip_id, in_s, out_s)
    output(result, f"Trimmed clip '{result['name']}' to {format_duration(result['duration'])}")


@clip.command("remove")
@click.argument("clip_id")
@handle_error
def clip_remove(clip_id: str) -> None:
    """Remove a clip from the project."""
    sess = get_session()
    result = clips_mod.remove_clip(sess, clip_id)
    output(result, f"Removed clip '{result['name']}'")


@clip.command("list")
@handle_error
def clip_list() -> None:
    """List all clips in the project."""
    sess = get_session()
    result = clips_mod.list_clips(sess)
    if not _json_output:
        if not result:
            click.echo("  No clips. Use 'clip add' to define a clip.")
            return
        from cli_anything.clipper.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["#", "ID", "Name", "Source", "In", "Out", "Duration", "Filters"],
            [
                [
                    str(c["index"]),
                    c["id"],
                    c["name"][:25],
                    c["source_id"],
                    format_duration(c["in"]),
                    format_duration(c["out"]),
                    c["duration_fmt"],
                    str(c["filter_count"]),
                ]
                for c in result
            ]
        )
    else:
        output(result)


@clip.command("show")
@click.argument("clip_id")
@handle_error
def clip_show(clip_id: str) -> None:
    """Show detailed information about a clip."""
    sess = get_session()
    result = clips_mod.show_clip(sess, clip_id)
    output(result, f"Clip: {result['name']}")


@clip.command("move")
@click.argument("clip_id")
@click.argument("index", type=int)
@handle_error
def clip_move(clip_id: str, index: int) -> None:
    """Reorder a clip to a new position in the compilation order."""
    sess = get_session()
    result = clips_mod.move_clip(sess, clip_id, index)
    output(result, f"Moved clip '{result['name']}' to position {index}")


@clip.command("label")
@click.argument("clip_id")
@click.argument("label")
@handle_error
def clip_label(clip_id: str, label: str) -> None:
    """Set a label on a clip."""
    sess = get_session()
    result = clips_mod.label_clip(sess, clip_id, label)
    output(result, f"Set label '{label}' on clip {clip_id}")


# ── filter group ──────────────────────────────────────────────────────────────

@cli.group("filter")
def filter_group():
    """Filter management (add, remove, set, list, available, info)."""
    pass


@filter_group.command("add")
@click.argument("clip_id")
@click.argument("filter_name")
@click.option(
    "--params", default=None,
    help='Filter params as JSON string, e.g. \'{"level": 0.5}\''
)
@handle_error
def filter_add(clip_id: str, filter_name: str, params: Optional[str]) -> None:
    """Add a filter to a clip."""
    sess = get_session()
    parsed_params = None
    if params:
        try:
            parsed_params = json.loads(params)
        except json.JSONDecodeError as e:
            _err(f"Invalid JSON params: {e}")
            if not _repl_mode:
                sys.exit(1)
            return
    result = filters_mod.add_filter(sess, clip_id, filter_name, parsed_params)
    output(result, f"Added filter '{filter_name}' to clip {clip_id}")


@filter_group.command("remove")
@click.argument("clip_id")
@click.argument("filter_index", type=int)
@handle_error
def filter_remove(clip_id: str, filter_index: int) -> None:
    """Remove a filter by index from a clip."""
    sess = get_session()
    result = filters_mod.remove_filter(sess, clip_id, filter_index)
    output(result, f"Removed filter '{result['removed_filter']}' from clip {clip_id}")


@filter_group.command("set")
@click.argument("clip_id")
@click.argument("filter_index", type=int)
@click.argument("param_name")
@click.argument("value")
@handle_error
def filter_set(clip_id: str, filter_index: int, param_name: str, value: str) -> None:
    """Update a parameter on an existing clip filter."""
    sess = get_session()
    # Attempt numeric conversion
    parsed_value: Any = value
    try:
        parsed_value = int(value)
    except ValueError:
        try:
            parsed_value = float(value)
        except ValueError:
            parsed_value = value

    result = filters_mod.set_filter_param(sess, clip_id, filter_index, param_name, parsed_value)
    output(result, f"Set {result['filter_name']}.{param_name} = {parsed_value}")


@filter_group.command("list")
@click.argument("clip_id")
@handle_error
def filter_list(clip_id: str) -> None:
    """List all filters applied to a clip."""
    sess = get_session()
    result = filters_mod.list_clip_filters(sess, clip_id)
    if not _json_output:
        if not result:
            click.echo(f"  No filters on clip {clip_id}.")
            return
        from cli_anything.clipper.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["#", "Filter", "Params", "Description"],
            [
                [
                    str(f["index"]),
                    f["name"],
                    json.dumps(f["params"]),
                    f["description"][:40],
                ]
                for f in result
            ]
        )
    else:
        output(result)


@filter_group.command("available")
@click.option("--category", default=None, help="Filter by category (color/video/audio/etc.)")
@handle_error
def filter_available(category: Optional[str]) -> None:
    """List available filters."""
    result = filters_mod.available_filters(category)
    if not _json_output:
        from cli_anything.clipper.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Name", "Category", "Description", "Params"],
            [
                [f["name"], f["category"], f["description"], str(f["param_count"])]
                for f in result
            ]
        )
    else:
        output(result)


@filter_group.command("info")
@click.argument("filter_name")
@handle_error
def filter_info(filter_name: str) -> None:
    """Show detailed info about a filter including all parameters."""
    result = filters_mod.filter_info(filter_name)
    output(result, f"Filter: {filter_name}")


# ── export group ──────────────────────────────────────────────────────────────

@cli.group()
def export():
    """Export commands (clip, compile, presets, preset-info)."""
    pass


@export.command("clip")
@click.argument("clip_id")
@click.option("-o", "--output", "output_path", required=True, help="Output file path")
@click.option("--preset", default="hd_mp4", show_default=True, help="Export preset")
@handle_error
def export_clip(clip_id: str, output_path: str, preset: str) -> None:
    """Render a single clip to a file."""
    sess = get_session()
    click.echo(f"Rendering clip {clip_id} → {output_path} ...")
    result = export_mod.render_clip(sess, clip_id, output_path, preset)
    output(result, f"Rendered to {output_path}")


@export.command("compile")
@click.option("-o", "--output", "output_path", required=True, help="Output file path")
@click.option("--preset", default="hd_mp4", show_default=True, help="Export preset")
@handle_error
def export_compile(output_path: str, preset: str) -> None:
    """Render all clips concatenated into a single file."""
    sess = get_session()
    click.echo(f"Compiling all clips → {output_path} ...")
    result = export_mod.render_compilation(sess, output_path, preset)
    output(
        result,
        f"Compiled {result['clip_count']} clips → {output_path} "
        f"({format_duration(result['total_duration'])})"
    )


@export.command("presets")
@handle_error
def export_presets() -> None:
    """List available export presets."""
    result = export_mod.list_presets()
    if not _json_output:
        from cli_anything.clipper.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Name", "Description", "Video", "Audio", "Ext"],
            [
                [p["name"], p["description"][:35], p["vcodec"], p["acodec"], p["extension"]]
                for p in result
            ]
        )
    else:
        output(result)


@export.command("preset-info")
@click.argument("preset_name")
@handle_error
def export_preset_info(preset_name: str) -> None:
    """Show full details for an export preset."""
    result = export_mod.preset_info(preset_name)
    output(result, f"Preset: {preset_name}")


# ── session group ─────────────────────────────────────────────────────────────

@cli.group("session")
def session_group():
    """Session commands (undo, redo, status, history)."""
    pass


@session_group.command("undo")
@handle_error
def session_undo() -> None:
    """Undo the last operation."""
    sess = get_session()
    description = sess.undo()
    output(
        {"success": True, "undone": description},
        f"Undone: {description}"
    )


@session_group.command("redo")
@handle_error
def session_redo() -> None:
    """Redo the last undone operation."""
    sess = get_session()
    description = sess.redo()
    output(
        {"success": True, "redone": description},
        f"Redone: {description}"
    )


@session_group.command("status")
@handle_error
def session_status() -> None:
    """Show session status (project, undo/redo counts, modified flag)."""
    sess = get_session()
    result = sess.status()
    output(result, "Session status:")


@session_group.command("history")
@handle_error
def session_history() -> None:
    """Show the undo history stack."""
    sess = get_session()
    result = sess.list_history()
    output(result, f"History ({len(result)} entries):")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--project", "project_path", default=None, help="Project file to open on start")
def repl(project_path: Optional[str]) -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.clipper.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    sess = get_session()

    if project_path and not sess.has_project():
        try:
            proj_mod.open_project(sess, project_path)
            skin.success(f"Opened project: {project_path}")
        except Exception as e:
            skin.error(str(e))

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "project new": "Create a new project",
        "project open <path>": "Open a project file",
        "project save [path]": "Save current project",
        "project info": "Show project info",
        "project profiles": "List video profiles",
        "source add <path>": "Import a video source",
        "source list": "List sources",
        "source probe <path>": "Probe a video file",
        "clip add --source <id> --in <tc> --out <tc>": "Add a clip",
        "clip list": "List clips",
        "clip trim <id> --in <tc> --out <tc>": "Trim a clip",
        "clip show <id>": "Show clip details",
        "clip remove <id>": "Remove a clip",
        "filter add <clip_id> <filter>": "Add a filter",
        "filter list <clip_id>": "List clip filters",
        "filter available": "List available filters",
        "export clip <id> -o <path>": "Render a single clip",
        "export compile -o <path>": "Render all clips",
        "export presets": "List export presets",
        "session undo": "Undo last operation",
        "session redo": "Redo last operation",
        "session status": "Show session status",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        try:
            project_name = ""
            modified = False
            if sess.has_project():
                project_name = sess.project.get("name", "untitled")
                modified = sess._modified

            raw = skin.get_input(pt_session, project_name, modified)

        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break

        if not raw:
            continue

        cmd = raw.strip()

        if cmd in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if cmd in ("help", "h", "?"):
            skin.help(_repl_commands)
            continue

        # Route the command through Click
        try:
            args = shlex.split(cmd)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except click.exceptions.BadParameter as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
