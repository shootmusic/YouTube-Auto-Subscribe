# config.py
import os

# ===== KONFIGURASI =====
TARGET_CHANNEL = "https://www.youtube.com/@remass62"
CHANNEL_NAME = "@remass62"

# Telegram (ambil dari environment variable / secrets)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# Jadwal dan target
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
