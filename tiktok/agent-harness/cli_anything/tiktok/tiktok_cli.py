#!/usr/bin/env python3
"""TikTok CLI — Manage TikTok videos and account from the command line.

This CLI wraps the TikTok Open API v2 via OAuth2 + PKCE. It covers
authentication, video management, and video upload/publishing.

Usage:
    # Setup OAuth credentials
    cli-anything-tiktok auth setup --client-key <KEY> --client-secret <SECRET>

    # Login via browser
    cli-anything-tiktok auth login

    # List videos
    cli-anything-tiktok video list

    # Upload a video
    cli-anything-tiktok upload video myvideo.mp4 --title "My Video"

    # Interactive REPL
    cli-anything-tiktok repl
"""

import sys
import os
import json
import click

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.tiktok.core import auth as auth_mod
from cli_anything.tiktok.core import user as user_mod
from cli_anything.tiktok.core import videos as vid_mod
from cli_anything.tiktok.core import upload as up_mod

_json_output = False
_repl_mode = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({
                    "error": str(e),
                    "type": type(e).__name__,
                }))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI Group ──────────────────────────────────────────────
@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """TikTok CLI — Video management from the command line.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Auth Commands ───────────────────────────────────────────────
@cli.group()
def auth():
    """Authentication and OAuth2 + PKCE setup."""
    pass


@auth.command("setup")
@click.option("--client-key", required=True, help="TikTok app Client Key")
@click.option("--client-secret", required=True, help="TikTok app Client Secret")
@click.option("--redirect-uri", default="http://localhost:4199/callback",
              help="OAuth redirect URI (must match app config)")
@click.option("--scopes", default="user.info.basic,video.list,video.upload,video.publish",
              help="Comma-separated OAuth scopes")
@handle_error
def auth_setup(client_key, client_secret, redirect_uri, scopes):
    """Configure TikTok OAuth app credentials."""
    result = auth_mod.setup_oauth(client_key, client_secret, redirect_uri, scopes)
    output(result, "TikTok app configured successfully.")


@auth.command("login")
@click.option("--code", default=None,
              help="Authorization code (for manual flow)")
@handle_error
def auth_login(code):
    """Login via OAuth2 + PKCE browser flow.

    Opens a browser for TikTok authorization. After approving,
    tokens are saved locally for subsequent API calls.

    Use --code if you need to manually paste the authorization code.
    """
    if code:
        result = auth_mod.login_with_code(code)
    else:
        result = auth_mod.login()
    output(result, "Login successful.")


@auth.command("status")
@handle_error
def auth_status():
    """Check authentication status."""
    result = auth_mod.get_auth_status()
    output(result)


@auth.command("logout")
@handle_error
def auth_logout():
    """Remove saved tokens."""
    result = auth_mod.logout()
    output(result, "Logged out.")


# ── User Commands ───────────────────────────────────────────────
@cli.group()
def user():
    """User profile commands."""
    pass


@user.command("info")
@handle_error
def user_info():
    """Get authenticated user's profile."""
    result = user_mod.get_user_info()
    output(result)


# ── Video Commands ──────────────────────────────────────────────
@cli.group()
def video():
    """Video management commands."""
    pass


@video.command("list")
@click.option("--max-count", type=int, default=20, help="Max videos to return")
@click.option("--cursor", type=int, default=0, help="Pagination cursor")
@handle_error
def video_list(max_count, cursor):
    """List your TikTok videos."""
    result = vid_mod.list_videos(max_count=max_count, cursor=cursor)
    output(result, "Videos:")


@video.command("info")
@click.argument("video_id")
@click.option("--fields", default=None,
              help="Comma-separated fields to return")
@handle_error
def video_info(video_id, fields):
    """Get details for a specific video."""
    field_list = fields.split(",") if fields else None
    result = vid_mod.get_video(video_id, fields=field_list)
    output(result)


@video.command("delete")
@click.argument("video_id")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@handle_error
def video_delete(video_id, confirm):
    """Delete a TikTok video."""
    if not confirm and not _repl_mode:
        click.confirm(f"Delete video {video_id}?", abort=True)
    result = vid_mod.delete_video(video_id)
    output(result, f"Video {video_id} deleted.")


# ── Upload Commands ─────────────────────────────────────────────
@cli.group()
def upload():
    """Video upload commands."""
    pass


@upload.command("video")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--title", default="", help="Video title/caption")
@click.option("--privacy", default="SELF_ONLY",
              type=click.Choice(["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS",
                                 "FOLLOWER_OF_CREATOR", "SELF_ONLY"]),
              help="Privacy level")
@handle_error
def upload_video(file_path, title, privacy):
    """Upload and publish a video to TikTok.

    FILE_PATH: Local path to the video file.
    """
    click.echo(f"Uploading {file_path}...")
    result = up_mod.upload_video(file_path, title=title, privacy_level=privacy)
    output(result, "Upload complete.")


# ── REPL ─────────────────────────────────────────────────────────
@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.tiktok.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("tiktok", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "auth":   "setup|login|status|logout",
        "user":   "info",
        "video":  "list|info|delete",
        "upload": "video",
        "help":   "Show this help",
        "quit":   "Exit REPL",
    }

    try:
        status = auth_mod.get_auth_status()
        if status.get("authenticated"):
            skin.success(f"Authenticated as: {status.get('user', 'unknown')}")
        elif status.get("configured"):
            skin.warning("App configured but not logged in. Run: auth login")
        else:
            skin.info("Not configured. Run: auth setup --client-key <KEY> --client-secret <SECRET>")
    except Exception:
        skin.info("Run 'auth setup' to configure TikTok app credentials.")

    while True:
        try:
            try:
                status = auth_mod.get_auth_status()
                context = status.get("user", "") if status.get("authenticated") else ""
            except Exception:
                context = ""

            line = skin.get_input(pt_session, context=context)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry Point ──────────────────────────────────────────────────
def main():
    cli()


if __name__ == "__main__":
    main()
