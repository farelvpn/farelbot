import os
import sys
import sqlite3
import logging
import datetime as DT
import requests, time, subprocess, re, random, base64, json, math
from telethon import TelegramClient, events, Button
from dotenv import load_dotenv
from pathlib import Path

# ====================================================================
# PERUBAHAN UTAMA: Menentukan path absolut dan setup logging
# ====================================================================
HOME_DIR = Path.home()
BOT_MODULE_DIR = Path(__file__).parent
ENV_PATH = HOME_DIR / ".env"
DB_PATH = HOME_DIR / "database.db"
LOG_FILE_PATH = "/tmp/farelbot.log"

# Setup logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

# Memuat variabel environment dari path yang ditentukan
load_dotenv(dotenv_path=ENV_PATH)
# ====================================================================

uptime = DT.datetime.now()

# Get configuration from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS")
CONTACT_USERNAME = os.getenv("CONTACT_USERNAME", "your_username")
CONTACT_LINK = os.getenv("CONTACT_LINK", "https://t.me/your_username")
API_ID = "6"
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"

# Validasi konfigurasi
if not BOT_TOKEN or not ADMIN_IDS_STR:
    logging.error(f"BOT_TOKEN dan ADMIN_IDS harus diatur di file {ENV_PATH}")
    sys.exit(1)

# Konversi string ADMIN_IDS menjadi list of integer
try:
    ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(',')]
except ValueError:
    logging.error("Format ADMIN_IDS salah. Harusnya daftar ID numerik dipisahkan koma.")
    sys.exit(1)

# Initialize Telegram client
SESSION_PATH = HOME_DIR / "farelbot"
bot = TelegramClient(str(SESSION_PATH), API_ID, API_HASH).start(bot_token=BOT_TOKEN)
logging.info("Bot started successfully.")

# Database setup
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS admin (user_id INTEGER PRIMARY KEY)")
cursor.execute("DELETE FROM admin")
for admin_id in ADMIN_IDS:
    cursor.execute("INSERT OR IGNORE INTO admin (user_id) VALUES (?)", (admin_id,))
conn.commit()
conn.close()

def get_db():
	x = sqlite3.connect(DB_PATH)
	x.row_factory = sqlite3.Row
	return x

def valid(user_id_str):
	try:
		user_id = int(user_id_str)
		db = get_db()
		result = db.execute("SELECT 1 FROM admin WHERE user_id = ?", (user_id,)).fetchone()
		db.close()
		return "true" if result else "false"
	except (ValueError, TypeError):
		return "false"

def convert_size(size_bytes):
   if size_bytes == 0: return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def run_script(command, input_text=None):
    try:
        process = subprocess.run(
            command, input=input_text, text=True,
            capture_output=True, shell=True, check=True
        )
        logging.info(f"Successfully executed: {command}")
        return process.stdout.strip()
    except FileNotFoundError:
        logging.error(f"Script not found: {command}")
        return f"ERROR: Skrip `{command}` tidak ditemukan."
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() if e.stderr else 'Skrip gagal.'
        logging.error(f"Error executing '{command}': {error_output}")
        return f"ERROR: {error_output}"
