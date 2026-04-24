"""Unit tests for TikTok CLI — no network calls, no TikTok account required."""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from cli_anything.tiktok.tiktok_cli import cli


# ── Fixtures ────────────────────────────────────────────────────

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_config_dir(tmp_path):
    config_dir = tmp_path / ".cli-anything-tiktok"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_config(tmp_config_dir):
    with patch("cli_anything.tiktok.utils.tiktok_backend.CONFIG_DIR", tmp_config_dir), \
         patch("cli_anything.tiktok.utils.tiktok_backend.TOKEN_FILE",
               tmp_config_dir / "tokens.json"), \
         patch("cli_anything.tiktok.utils.tiktok_backend.CONFIG_FILE",
               tmp_config_dir / "config.json"), \
         patch("cli_anything.tiktok.utils.tiktok_backend.PKCE_VERIFIER_FILE",
               tmp_config_dir / "pkce_verifier.json"):
        yield tmp_config_dir


# ── Auth Tests ──────────────────────────────────────────────────

class TestAuthSetup:

    def test_setup_saves_config(self, runner, mock_config):
        result = runner.invoke(cli, [
            "auth", "setup",
            "--client-key", "test_key_123",
            "--client-secret", "test_secret_456",
        ])
        assert result.exit_code == 0
        assert "configured" in result.output.lower() or "TikTok" in result.output

    def test_setup_custom_redirect(self, runner, mock_config):
        result = runner.invoke(cli, [
            "auth", "setup",
            "--client-key", "key",
            "--client-secret", "secret",
            "--redirect-uri", "http://localhost:9000/cb",
        ])
        assert result.exit_code == 0
        config_file = mock_config / "config.json"
        assert config_file.exists()
        with open(config_file) as f:
            config = json.load(f)
        assert config["redirect_uri"] == "http://localhost:9000/cb"
        assert config["client_key"] == "key"

    def test_status_not_configured(self, runner, mock_config):
        result = runner.invoke(cli, ["auth", "status"])
        assert result.exit_code == 0
        assert "false" in result.output.lower() or "configured" in result.output.lower()

    def test_logout_no_tokens(self, runner, mock_config):
        result = runner.invoke(cli, ["auth", "logout"])
        assert result.exit_code == 0
        assert "logged_out" in result.output or "Logged" in result.output


class TestAuthLogin:

    def test_login_without_config_fails(self, runner, mock_config):
        result = runner.invoke(cli, ["auth", "login", "--code", "someauthcode"])
        assert result.exit_code != 0 or "error" in result.output.lower() or \
               "configured" in result.output.lower() or "not configured" in result.output.lower()

    def test_login_with_code(self, runner, mock_config):
        config_file = mock_config / "config.json"
        verifier_file = mock_config / "pkce_verifier.json"

        with open(config_file, "w") as f:
            json.dump({
                "client_key": "test_key",
                "client_secret": "test_secret",
                "redirect_uri": "http://localhost:4199/callback",
                "scopes": "user.info.basic",
            }, f)

        with open(verifier_file, "w") as f:
            json.dump({"code_verifier": "test_verifier_abc123"}, f)

        mock_tokens = {
            "access_token": "access_tok_xyz",
            "refresh_token": "refresh_tok_xyz",
            "expires_in": 86400,
            "open_id": "test_open_id",
        }
        mock_user = {"display_name": "TestUser", "open_id": "test_open_id"}

        with patch("requests.post") as mock_post, \
             patch("cli_anything.tiktok.utils.tiktok_backend.get_current_user",
                   return_value=mock_user):
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_tokens
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = runner.invoke(cli, ["auth", "login", "--code", "auth_code_abc"])

        assert result.exit_code == 0
        assert "logged_in" in result.output or "Login" in result.output


# ── Video Tests ─────────────────────────────────────────────────

class TestVideoCommands:

    def _write_tokens(self, config_dir):
        import time
        with open(config_dir / "tokens.json", "w") as f:
            json.dump({
                "access_token": "tok_abc",
                "refresh_token": "ref_abc",
                "expires_in": 86400,
                "saved_at": time.time(),
            }, f)

    def test_list_videos(self, runner, mock_config):
        self._write_tokens(mock_config)
        mock_resp = {
            "data": {
                "videos": [
                    {"id": "v1", "title": "My First Video", "duration": 30},
                ],
                "cursor": 0,
                "has_more": False,
            }
        }
        with patch("cli_anything.tiktok.core.videos.api_post",
                   return_value=mock_resp):
            result = runner.invoke(cli, ["video", "list"])
        assert result.exit_code == 0

    def test_get_video(self, runner, mock_config):
        self._write_tokens(mock_config)
        mock_resp = {
            "data": {
                "videos": [{"id": "v1", "title": "Test", "duration": 15}]
            }
        }
        with patch("cli_anything.tiktok.core.videos.api_post",
                   return_value=mock_resp):
            result = runner.invoke(cli, ["video", "info", "v1"])
        assert result.exit_code == 0

    def test_delete_video(self, runner, mock_config):
        self._write_tokens(mock_config)
        mock_resp = {"data": {}, "error": {"code": "ok"}}
        with patch("cli_anything.tiktok.core.videos.api_post",
                   return_value=mock_resp):
            result = runner.invoke(cli, ["video", "delete", "v1", "--confirm"])
        assert result.exit_code == 0


# ── Upload Tests ────────────────────────────────────────────────

class TestUploadCommands:

    def test_upload_init_called(self, mock_config):
        import time
        with open(mock_config / "tokens.json", "w") as f:
            json.dump({
                "access_token": "tok",
                "refresh_token": "ref",
                "expires_in": 86400,
                "saved_at": time.time(),
            }, f)

        mock_init_resp = {
            "data": {
                "publish_id": "pub_123",
                "upload_url": "https://upload.tiktok.com/fake",
            }
        }
        with patch("cli_anything.tiktok.core.upload.api_post",
                   return_value=mock_init_resp) as mock_post:
            from cli_anything.tiktok.core.upload import init_upload
            result = init_upload(video_size=1024, chunk_size=1024, total_chunk_count=1)

        assert mock_post.called
        assert result["data"]["publish_id"] == "pub_123"


# ── JSON Output Tests ───────────────────────────────────────────

class TestJsonOutput:

    def _write_tokens(self, config_dir):
        import time
        with open(config_dir / "tokens.json", "w") as f:
            json.dump({
                "access_token": "tok",
                "refresh_token": "ref",
                "expires_in": 86400,
                "saved_at": time.time(),
            }, f)

    def test_video_list_json(self, runner, mock_config):
        self._write_tokens(mock_config)
        mock_resp = {"data": {"videos": [{"id": "v1"}], "cursor": 0}}
        with patch("cli_anything.tiktok.core.videos.api_post",
                   return_value=mock_resp):
            result = runner.invoke(cli, ["--json", "video", "list"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert isinstance(parsed, dict)

    def test_auth_status_json(self, runner, mock_config):
        result = runner.invoke(cli, ["--json", "auth", "status"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert "configured" in parsed
        assert "authenticated" in parsed


# ── Backend Unit Tests ──────────────────────────────────────────

class TestBackend:

    def test_config_save_load(self, mock_config):
        from cli_anything.tiktok.utils.tiktok_backend import save_config, load_config
        save_config({"client_key": "k1", "client_secret": "s1"})
        loaded = load_config()
        assert loaded["client_key"] == "k1"

    def test_token_save_load(self, mock_config):
        from cli_anything.tiktok.utils.tiktok_backend import save_tokens, load_tokens
        save_tokens({"access_token": "tok", "refresh_token": "ref", "expires_in": 86400})
        loaded = load_tokens()
        assert loaded["access_token"] == "tok"
        assert "saved_at" in loaded

    def test_pkce_pair_generation(self):
        from cli_anything.tiktok.utils.tiktok_backend import generate_pkce_pair
        verifier, challenge = generate_pkce_pair()
        assert 43 <= len(verifier) <= 128
        # code_challenge must be base64url without padding
        assert "=" not in challenge
        assert len(challenge) == 43  # SHA-256 digest → 32 bytes → 43 base64url chars

    def test_authorize_url_contains_code_challenge(self):
        from cli_anything.tiktok.utils.tiktok_backend import (
            generate_pkce_pair, get_authorize_url, OAUTH_AUTHORIZE_URL
        )
        verifier, challenge = generate_pkce_pair()
        url = get_authorize_url("my_key", "http://localhost:4199/callback", challenge)
        assert "code_challenge=" in url
        assert challenge in url
        assert "code_challenge_method=S256" in url
        assert url.startswith(OAUTH_AUTHORIZE_URL)

    def test_pkce_verifier_save_load(self, mock_config):
        from cli_anything.tiktok.utils.tiktok_backend import (
            save_pkce_verifier, load_pkce_verifier
        )
        save_pkce_verifier("my_verifier_string")
        loaded = load_pkce_verifier()
        assert loaded == "my_verifier_string"
