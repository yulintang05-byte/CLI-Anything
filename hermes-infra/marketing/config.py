"""Central config loaded from environment variables."""
import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")
DEVTO_API_KEY = os.getenv("DEVTO_API_KEY", "")

# Model settings — newest, most capable first; fallbacks for accounts that
# don't have access to the latest model yet.
MODEL = os.getenv("HERMES_MARKETING_MODEL", "claude-fable-5")
MODEL_FALLBACKS = ["claude-opus-4-8", "claude-sonnet-4-6"]
MAX_TOKENS = int(os.getenv("HERMES_MARKETING_MAX_TOKENS", "8192"))

PRODUCT_NAME = "Hermes"
PRODUCT_TAGLINE = "The terminal Claude deserves."
PRODUCT_URL = os.getenv("HERMES_PRODUCT_URL", "https://hermes-landing-c2k.pages.dev")
LICENSE_API_URL = os.getenv(
    "HERMES_LICENSE_API_URL", "https://hermes-license-proxy.luckylefty.workers.dev"
)
WHOP_URL = os.getenv("HERMES_WHOP_URL", "https://hermes-landing-c2k.pages.dev")
INSTALL_CMD = f'curl -fsSL {PRODUCT_URL}/install.sh | bash'
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
