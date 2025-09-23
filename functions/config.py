import os
from pathlib import Path
from dotenv import load_dotenv

# Carga .env si existe
load_dotenv()

# --- Credenciales Blizzard ---
CLIENT_ID = os.getenv("", "1f083c51e0eb4025884eef1b2636aba4")
CLIENT_SECRET = os.getenv("", "8MHTt4Rr0O6hSfObqgABPrcpkiJLx2An")

# --- Config API ---
REGION = os.getenv("BLIZZARD_REGION", "eu")          # "eu" o "us"
LOCALE = os.getenv("BLIZZARD_LOCALE", "en_US")       # "en_US" o "es_ES"

# --- Items / realm ---
REALM_ID = int(os.getenv("REALM_ID", "1092"))
ITEM_ID_CARNE = int(os.getenv("ITEM_ID_CARNE", "223512"))
ITEM_ID_BELEDAR = int(os.getenv("ITEM_ID_BELEDAR", "222728"))

# --- Rutas (carpetas y ficheros) ---
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RES_DIR = ROOT / "resources"

DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE = DATA_DIR / "beneficio.csv"
PRECIOS_CSV = DATA_DIR / "precios.csv"

ICON_PATH = (RES_DIR / "icon.ico")
DEFAULT_BG = (RES_DIR / "fondo.png")
