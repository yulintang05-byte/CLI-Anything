"""OAuth2 + PKCE authentication flow for TikTok Open API."""

import webbrowser
import http.server
import threading
from urllib.parse import urlparse, parse_qs

from cli_anything.tiktok.utils.tiktok_backend import (
    load_config, save_config, load_tokens, save_tokens,
    generate_pkce_pair, save_pkce_verifier, load_pkce_verifier,
    get_authorize_url, exchange_code, get_current_user,
    CONFIG_DIR,
)

DEFAULT_SCOPES = "user.info.basic,video.list,video.upload,video.publish"


def setup_oauth(client_key: str, client_secret: str,
                redirect_uri: str = "http://localhost:4199/callback",
                scopes: str = DEFAULT_SCOPES) -> dict:
    config = {
        "client_key": client_key,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "scopes": scopes,
    }
    save_config(config)
    return {
        "status": "configured",
        "client_key": client_key,
        "redirect_uri": redirect_uri,
        "scopes": scopes,
        "config_path": str(CONFIG_DIR / "config.json"),
    }


def login() -> dict:
    config = load_config()
    if not config.get("client_key") or not config.get("client_secret"):
        raise RuntimeError(
            "OAuth app not configured. Run 'auth setup' with your "
            "client_key and client_secret first."
        )

    client_key = config["client_key"]
    client_secret = config["client_secret"]
    redirect_uri = config.get("redirect_uri", "http://localhost:4199/callback")
    scopes = config.get("scopes", DEFAULT_SCOPES)

    parsed = urlparse(redirect_uri)
    port = parsed.port or 4199

    code_verifier, code_challenge = generate_pkce_pair()
    save_pkce_verifier(code_verifier)

    auth_url = get_authorize_url(client_key, redirect_uri, code_challenge, scopes)

    auth_code = [None]
    auth_error = [None]

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlparse(self.path).query)
            if "code" in query:
                auth_code[0] = query["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Authorization successful!</h2>"
                    b"<p>You can close this window and return to the CLI.</p>"
                    b"</body></html>"
                )
            elif "error" in query:
                auth_error[0] = query.get("error_description", query["error"])[0]
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"<html><body><h2>Authorization failed: {auth_error[0]}</h2>"
                    .encode()
                )
            else:
                self.send_response(400)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", port), CallbackHandler)
    server.timeout = 120

    webbrowser.open(auth_url)
    server.handle_request()
    server.server_close()

    if auth_error[0]:
        raise RuntimeError(f"Authorization failed: {auth_error[0]}")

    if not auth_code[0]:
        raise RuntimeError("Authorization timed out. Please try again.")

    tokens = exchange_code(client_key, client_secret, auth_code[0], code_verifier, redirect_uri)
    save_tokens(tokens)

    try:
        user = get_current_user()
        return {
            "status": "logged_in",
            "user": user.get("display_name", "unknown"),
            "open_id": user.get("open_id", ""),
        }
    except Exception:
        return {
            "status": "logged_in",
            "message": "Tokens saved. Could not verify user info.",
        }


def login_with_code(code: str) -> dict:
    config = load_config()
    if not config.get("client_key"):
        raise RuntimeError("OAuth app not configured. Run 'auth setup' first.")

    code_verifier = load_pkce_verifier()

    tokens = exchange_code(
        config["client_key"],
        config["client_secret"],
        code,
        code_verifier,
        config.get("redirect_uri", "http://localhost:4199/callback"),
    )
    save_tokens(tokens)

    try:
        user = get_current_user()
        return {
            "status": "logged_in",
            "user": user.get("display_name", "unknown"),
            "open_id": user.get("open_id", ""),
        }
    except Exception:
        return {"status": "logged_in", "message": "Tokens saved."}


def get_auth_status() -> dict:
    config = load_config()
    tokens = load_tokens()

    result = {
        "configured": bool(config.get("client_key")),
        "authenticated": bool(tokens.get("access_token")),
    }

    if config.get("client_key"):
        result["client_key"] = config["client_key"]
        result["redirect_uri"] = config.get("redirect_uri", "")

    if tokens.get("access_token"):
        try:
            user = get_current_user()
            result["user"] = user.get("display_name", "unknown")
            result["open_id"] = user.get("open_id", "")
            result["token_valid"] = True
        except Exception as e:
            result["token_valid"] = False
            result["token_error"] = str(e)

    return result


def logout() -> dict:
    token_file = CONFIG_DIR / "tokens.json"
    if token_file.exists():
        token_file.unlink()
    return {"status": "logged_out", "message": "Local tokens removed."}
