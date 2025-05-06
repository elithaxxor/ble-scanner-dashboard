import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DB_PATH = os.path.join(BASE_DIR, "bluetooth_devices.db")

# Bluetooth scanning configuration
SCAN_INTERVAL = 5  # seconds between each scan
BLUETOOTH_INTERFACE = 'hci0'  # default Bluetooth interface
HUMAN_RSSI_THRESHOLD = int(os.getenv("HUMAN_RSSI_THRESHOLD", "-70"))  # RSSI threshold for human presence

# Web interface configuration
WEB_HOST = '0.0.0.0'
WEB_PORT = 8000
DEBUG_MODE = True

# Logging configuration
LOG_FILE = os.path.join(BASE_DIR, "ble_scanner.log")
LOG_LEVEL = "INFO"

# Notification configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
WHATSAPP_AUTH_TOKEN = os.getenv("WHATSAPP_AUTH_TOKEN", "")
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM", "")
WHATSAPP_TO = os.getenv("WHATSAPP_TO", "")
