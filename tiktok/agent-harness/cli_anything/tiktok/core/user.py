"""TikTok user profile commands."""

from cli_anything.tiktok.utils.tiktok_backend import get_current_user


def get_user_info() -> dict:
    user = get_current_user()
    return {
        "display_name": user.get("display_name", ""),
        "open_id": user.get("open_id", ""),
        "union_id": user.get("union_id", ""),
        "avatar_url": user.get("avatar_url", ""),
    }
