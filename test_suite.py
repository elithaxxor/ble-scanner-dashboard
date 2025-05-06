import unittest
import asyncio
import logging
from unittest.mock import patch, MagicMock
from notifications import send_discord_notification, send_telegram_notification, send_whatsapp_notification
from config import HUMAN_RSSI_THRESHOLD
from app import update_device
from datetime import datetime

class TestNotifications(unittest.TestCase):
    """Test suite for notification system"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_message = "Test notification message"
        
    @patch('notifications.requests.post')
    def test_discord_notification(self, mock_post):
        """Test Discord notification sending"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status = lambda: None
        
        with patch('notifications.DISCORD_WEBHOOK_URL', 'mock_url'):
            result = send_discord_notification(self.test_message)
            self.assertTrue(result)
            mock_post.assert_called_once()
    
    @patch('notifications.requests.post')
    def test_telegram_notification(self, mock_post):
        """Test Telegram notification sending"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status = lambda: None
        
        with patch('notifications.TELEGRAM_BOT_TOKEN', 'mock_token'):
            with patch('notifications.TELEGRAM_CHAT_ID', 'mock_chat_id'):
                result = send_telegram_notification(self.test_message)
                self.assertTrue(result)
                mock_post.assert_called_once()
    
    @patch('notifications.requests.post')
    def test_whatsapp_notification(self, mock_post):
        """Test WhatsApp notification sending"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status = lambda: None
        
        with patch.multiple('notifications',
                          WHATSAPP_API_URL='mock_url',
                          WHATSAPP_AUTH_TOKEN='mock_token',
                          WHATSAPP_FROM='mock_from',
                          WHATSAPP_TO='mock_to'):
            result = send_whatsapp_notification(self.test_message)
            self.assertTrue(result)
            mock_post.assert_called_once()

class TestBLEScanner(unittest.TestCase):
    """Test suite for BLE scanning functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_device = MagicMock()
        self.mock_device.address = "00:11:22:33:44:55"
        self.mock_device.name = "Test Device"
        self.mock_device.rssi = -60
    
    @patch('sqlite3.connect')
    async def test_update_device_new(self, mock_connect):
        """Test updating a new device"""
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        await update_device(
            self.mock_device.address,
            self.mock_device.name,
            self.mock_device.rssi
        )
        
        # Verify device was inserted
        mock_cursor.execute.assert_called()
        mock_connect.return_value.commit.assert_called_once()
    
    @patch('sqlite3.connect')
    async def test_update_device_existing(self, mock_connect):
        """Test updating an existing device"""
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)  # Existing frequency count
        
        await update_device(
            self.mock_device.address,
            self.mock_device.name,
            self.mock_device.rssi
        )
        
        # Verify device was updated
        mock_cursor.execute.assert_called()
        mock_connect.return_value.commit.assert_called_once()
    
    def test_human_presence_threshold(self):
        """Test RSSI threshold for human presence"""
        self.assertIsInstance(HUMAN_RSSI_THRESHOLD, int)
        # Typical RSSI values range from -100 (far) to 0 (very close)
        self.assertTrue(-100 <= HUMAN_RSSI_THRESHOLD <= 0)

class AsyncioTestCase(unittest.TestCase):
    """Base class for asyncio test cases"""
    
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        self.loop.close()
        asyncio.set_event_loop(None)
    
    def run_async(self, coro):
        """Run a coroutine in the test loop"""
        return self.loop.run_until_complete(coro)

class TestBLEScanner(AsyncioTestCase):
    """Test suite for BLE scanning functionality"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.mock_device = MagicMock()
        self.mock_device.address = "00:11:22:33:44:55"
        self.mock_device.name = "Test Device"
        self.mock_device.rssi = -60
    
    @patch('sqlite3.connect')
    def test_update_device_new(self, mock_connect):
        """Test updating a new device"""
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        self.run_async(update_device(
            self.mock_device.address,
            self.mock_device.name,
            self.mock_device.rssi
        ))
        
        # Verify device was inserted
        mock_cursor.execute.assert_called()
        mock_connect.return_value.commit.assert_called_once()
    
    @patch('sqlite3.connect')
    def test_update_device_existing(self, mock_connect):
        """Test updating an existing device"""
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)  # Existing frequency count
        
        self.run_async(update_device(
            self.mock_device.address,
            self.mock_device.name,
            self.mock_device.rssi
        ))
        
        # Verify device was updated
        mock_cursor.execute.assert_called()
        mock_connect.return_value.commit.assert_called_once()
    
    def test_human_presence_threshold(self):
        """Test RSSI threshold for human presence"""
        self.assertIsInstance(HUMAN_RSSI_THRESHOLD, int)
        # Typical RSSI values range from -100 (far) to 0 (very close)
        self.assertTrue(-100 <= HUMAN_RSSI_THRESHOLD <= 0)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.ERROR)
    
    # Run tests
    print("Running BLE Scanner Test Suite...")
    unittest.main(verbosity=2)
