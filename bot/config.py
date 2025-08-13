import os
from dotenv import load_dotenv
from pathlib import Path

# Load env once
load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")

# Data directory & DB path
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = str(DATA_DIR / "items.db")

# Feature flags
MULTI_USER = False  # set True later to switch to per-user storage

# UX
MENU_DELAY_SEC = 1
