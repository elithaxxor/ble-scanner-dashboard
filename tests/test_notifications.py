from unittest.mock import patch
from notifications import send_all_notifications


@patch("notifications.send_discord_notification", return_value=True)
@patch("notifications.send_telegram_notification", return_value=True)
@patch("notifications.send_whatsapp_notification", return_value=False)
def test_send_all(mock_wa, mock_tg, mock_dc):
    res = send_all_notifications("hi")
    assert res["discord"] is True
    assert res["telegram"] is True
    assert res["whatsapp"] is False
