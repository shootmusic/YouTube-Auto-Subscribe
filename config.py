# config.py
import os
from datetime import datetime

# ===== KONFIGURASI =====
TARGET_CHANNEL = "https://www.youtube.com/@remass62"
CHANNEL_NAME = "@remass62"

# Telegram (sesuai punya Yang Mulia)
TELEGRAM_TOKEN = "8702596327:AAHnYrI9Mh4-yxpTomqkKZcjz_D0Gq9wdUo"
TELEGRAM_CHAT_ID = "7710155531"

# Jadwal (WIB ke UTC)
JAM_PRODUKSI_AKUN = 9   # Jam 9 pagi WIB = 2:00 UTC
JAM_SUBSCRIBE = 11      # Jam 11 pagi WIB = 4:00 UTC
TARGET_AKUN_PER_HARI = 100
TARGET_SUBSCRIBE_PER_HARI = 100

# Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DIR = os.path.join(BASE_DIR, "accounts")
COOKIES_DIR = os.path.join(BASE_DIR, "cookies")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Buat folder
for dir_path in [ACCOUNTS_DIR, COOKIES_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# File database
ACCOUNTS_DB = os.path.join(ACCOUNTS_DIR, "accounts_db.json")
HISTORY_FILE = os.path.join(LOGS_DIR, f"history_{datetime.now().strftime('%Y%m')}.json")
