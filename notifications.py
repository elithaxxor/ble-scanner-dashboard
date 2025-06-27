import requests
import logging
from config import (
    DISCORD_WEBHOOK_URL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    WHATSAPP_API_URL,
    WHATSAPP_AUTH_TOKEN,
    WHATSAPP_FROM,
    WHATSAPP_TO,
    LOG_FILE,
    LOG_LEVEL,
)

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def send_discord_notification(message):
    """Send notification to Discord using webhook."""
    try:
        if not DISCORD_WEBHOOK_URL:
            logger.warning("Discord webhook URL not configured")
            return False

        payload = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Discord notification sent successfully")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Discord notification: {e}")
        return False


def send_telegram_notification(message):
    """Send notification via Telegram bot."""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.warning("Telegram bot token or chat ID not configured")
            return False

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Telegram notification sent successfully")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Telegram notification: {e}")
        return False


def send_whatsapp_notification(message):
    """Send notification via WhatsApp Business API."""
    try:
        if not all([WHATSAPP_API_URL, WHATSAPP_AUTH_TOKEN, WHATSAPP_FROM, WHATSAPP_TO]):
            logger.warning("WhatsApp configuration incomplete")
            return False

        headers = {
            "Authorization": f"Bearer {WHATSAPP_AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        payload = {"from": WHATSAPP_FROM, "to": WHATSAPP_TO, "text": {"body": message}}

        response = requests.post(
            WHATSAPP_API_URL, json=payload, headers=headers, timeout=10
        )
        response.raise_for_status()
        logger.info("WhatsApp notification sent successfully")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending WhatsApp notification: {e}")
        return False


def send_all_notifications(message):
    """Send notifications to all configured channels."""
    results = {
        "discord": send_discord_notification(message),
        "telegram": send_telegram_notification(message),
        "whatsapp": send_whatsapp_notification(message),
    }

    successful = sum(1 for result in results.values() if result)
    total = len(results)

    if successful == 0:
        logger.error("Failed to send notifications to any channel")
    elif successful < total:
        logger.warning(f"Sent notifications to {successful}/{total} channels")
    else:
        logger.info("Successfully sent notifications to all channels")

    return results
