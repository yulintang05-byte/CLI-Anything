"""TikTok Open API backend — wraps TikTok Open API v2 via OAuth2 + PKCE.

This module handles all HTTP communication with the TikTok API.
It is the only module that makes network requests.
"""

import base64
import hashlib
import json
import secrets
import time
import requests
from pathlib import Path
from typing import Any
from urllib.parse import urlencode


API_BASE = "https://open.tiktokapis.com/v2"
OAUTH_AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
OAUTH_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
OAUTH_REVOKE_URL = "https://open.tiktokapis.com/v2/oauth/revoke/"

CONFIG_DIR = Path.home() / ".cli-anything-tiktok"
TOKEN_FILE = CONFIG_DIR / "tokens.json"
CONFIG_FILE = CONFIG_DIR / "config.json"
PKCE_VERIFIER_FILE = CONFIG_DIR / "pkce_verifier.json"


def get_config_dir() -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config: dict):
    get_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def load_tokens() -> dict:
    if not TOKEN_FILE.exists():
        return {}
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)


def save_tokens(tokens: dict):
    get_config_dir()
    tokens["saved_at"] = time.time()
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)


def generate_pkce_pair() -> tuple[str, str]:
    """Generate a PKCE code_verifier and code_challenge (S256)."""
    code_verifier = secrets.token_urlsafe(96)[:128]
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


def save_pkce_verifier(verifier: str):
    get_config_dir()
    with open(PKCE_VERIFIER_FILE, "w") as f:
        json.dump({"code_verifier": verifier}, f)


def load_pkce_verifier() -> str:
    if not PKCE_VERIFIER_FILE.exists():
        raise RuntimeError("PKCE verifier not found. Start a new login flow.")
    with open(PKCE_VERIFIER_FILE, "r") as f:
        return json.load(f)["code_verifier"]


def get_authorize_url(client_key: str, redirect_uri: str,
                      code_challenge: str,
                      scopes: str = "user.info.basic,video.list,video.upload,video.publish") -> str:
    params = {
        "client_key": client_key,
        "scope": scopes,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{OAUTH_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code(client_key: str, client_secret: str,
                  code: str, code_verifier: str, redirect_uri: str) -> dict:
    resp = requests.post(
        OAUTH_TOKEN_URL,
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(client_key: str, client_secret: str,
                         refresh_token: str) -> dict:
    resp = requests.post(
        OAUTH_TOKEN_URL,
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _get_valid_token() -> str:
    tokens = load_tokens()
    if not tokens:
        raise RuntimeError("Not authenticated. Run 'auth login' first.")

    access_token = tokens.get("access_token")
    saved_at = tokens.get("saved_at", 0)
    expires_in = tokens.get("expires_in", 86400)

    if time.time() - saved_at > (expires_in - 300):
        config = load_config()
        if not config.get("client_key") or not config.get("client_secret"):
            raise RuntimeError("OAuth config missing. Run 'auth setup' first.")
        new_tokens = refresh_access_token(
            config["client_key"],
            config["client_secret"],
            tokens["refresh_token"],
        )
        new_tokens["refresh_token"] = new_tokens.get(
            "refresh_token", tokens["refresh_token"]
        )
        save_tokens(new_tokens)
        access_token = new_tokens["access_token"]

    return access_token


def api_request(method: str, endpoint: str,
                params: dict | None = None,
                json_data: dict | None = None) -> Any:
    token = _get_valid_token()
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    resp = requests.request(
        method,
        url,
        headers=headers,
        params=params,
        json=json_data,
        timeout=60,
    )
    resp.raise_for_status()

    if resp.status_code == 204:
        return {"status": "success"}

    return resp.json()


def api_get(endpoint: str, params: dict | None = None) -> Any:
    return api_request("GET", endpoint, params=params)


def api_post(endpoint: str, data: dict | None = None) -> Any:
    return api_request("POST", endpoint, json_data=data)


def get_current_user() -> dict:
    resp = api_get(
        "/user/info/",
        params={"fields": "open_id,union_id,avatar_url,display_name"},
    )
    return resp.get("data", {}).get("user", {})
