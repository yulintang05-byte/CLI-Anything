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
PRODUCT_NAME = "Hermes"
PRODUCT_TAGLINE = "The terminal Claude deserves."
PRODUCT_URL = "https://hermes.sh"
WHOP_URL = "https://whop.com/hermes"
INSTALL_CMD = 'curl -fsSL https://hermes.sh/install.sh | bash'
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
