# BLE Scanner Dashboard

A modern Bluetooth Low Energy (BLE) scanner that monitors nearby devices and provides a real-time web dashboard for visualization. Perfect for tracking device frequency and movement patterns near a specific location.

## Features

- 🔍 Real-time BLE device scanning
- 📊 Modern web dashboard with real-time updates
- 📱 Device frequency tracking
- 📈 24-hour activity visualization
- 💾 SQLite database for persistent storage
- 🎨 Responsive design with Tailwind CSS
- 🚨 Human presence detection with RSSI threshold
- 🔔 Multi-channel notifications:
  - Discord integration
  - Telegram bot notifications
  - WhatsApp message alerts

## Requirements

- Python 3.7+
- Linux system with Bluetooth capability
- Bluetooth adapter (built-in or external)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ble-scanner
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python create_db.py
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your notification settings
```

## Usage

1. Start the BLE scanner:
```bash
python app.py
```
This will begin scanning for nearby Bluetooth devices and logging their presence to the database.

2. In a separate terminal, start the web dashboard:
```bash
python web_app.py
```
The dashboard will be available at http://localhost:8000

## Dashboard Features

- **Real-time Device Tracking**: View currently detected devices
- **Statistics**: Total devices, visit frequency, and last detection times
- **Activity Graph**: 24-hour visualization of device activity
- **Device History**: Detailed table of all detected devices with timestamps

## Configuration

### Core Settings
You can modify core settings in `config.py`:

- `SCAN_INTERVAL`: Time between scans (seconds)
- `WEB_PORT`: Web dashboard port (default: 8000)
- `LOG_LEVEL`: Logging detail level
- `HUMAN_RSSI_THRESHOLD`: Signal strength threshold for presence detection
- Other database and Bluetooth configurations

### Notification Setup

#### Discord Integration
1. Create a Discord webhook:
   - Open your Discord server settings
   - Navigate to Integrations > Webhooks
   - Click "Create Webhook" or use an existing one
   - Copy the webhook URL
2. Set the webhook URL in your .env:
   ```bash
   DISCORD_WEBHOOK_URL=your_webhook_url
   ```

#### Telegram Bot Setup
1. Create a Telegram bot:
   - Message @BotFather on Telegram
   - Use /newbot command and follow instructions
   - Copy the provided bot token
2. Get your chat ID:
   - Start a chat with your bot
   - Send it a message
   - Visit: https://api.telegram.org/bot<YourBOTToken>/getUpdates
   - Copy your chat_id from the response
3. Configure in .env:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

#### WhatsApp Integration
1. Set up WhatsApp Business API or Twilio:
   - Sign up for WhatsApp Business API or Twilio
   - Get your API credentials
2. Configure in .env:
   ```bash
   WHATSAPP_API_URL=your_api_url
   WHATSAPP_AUTH_TOKEN=your_auth_token
   WHATSAPP_FROM=your_whatsapp_number
   WHATSAPP_TO=recipient_whatsapp_number
   ```

### Human Presence Detection
Configure the RSSI threshold in .env:
```bash
HUMAN_RSSI_THRESHOLD=-70  # Adjust based on your environment
```
- Higher values (e.g., -50) require devices to be closer
- Lower values (e.g., -80) detect devices from further away

## Troubleshooting

### Common Issues

1. **Bluetooth Adapter Not Found**
   - Ensure your system has a Bluetooth adapter
   - Check if Bluetooth service is running:
     ```bash
     systemctl status bluetooth
     ```
   - Verify adapter is recognized:
     ```bash
     hciconfig -a
     ```
   - If you get "[Errno 2] No such file or directory", run:
     ```bash
     sudo apt-get install bluetooth bluez
     sudo systemctl start bluetooth
     ```

2. **Notification Setup Issues**
   - Ensure all required environment variables are set in your .env file
   - Test notifications individually:
     ```bash
     python test_notifications.py
     ```
   - Check ble_scanner.log for detailed error messages
   - Verify your API keys and tokens are valid
   - For Discord: Ensure webhook URL is correct and channel permissions are set
   - For Telegram: Verify bot token and chat ID by sending a test message
   - For WhatsApp: Confirm API credentials and phone numbers are properly formatted

3. **Permission Issues**
   - Ensure you have the necessary permissions:
     ```bash
     sudo setcap 'cap_net_raw,cap_net_admin+eip' $(which python3)
     ```

4. **Database Errors**
   - If database errors occur, try reinitializing:
     ```bash
     python create_db.py
     ```

### Logs

- Check `ble_scanner.log` for detailed error messages and debugging information
- Web application logs will appear in the terminal running `web_app.py`

## Testing

### Running Tests

1. Run the complete test suite:
```bash
python test_suite.py
```

2. Run individual test components:
```bash
# Test notification system
python test_notifications.py

# Test BLE scanner
python test_ble_scanner.py
```

3. Run automated test and packaging:
```bash
./test_and_package.sh
```

### Test Coverage
- Notification System: Tests for Discord, Telegram, and WhatsApp integration
- BLE Scanner: Tests for device detection and RSSI threshold
- Database: Tests for device tracking and updates
- Mock objects used for external services and hardware
- Async operation testing for BLE operations

## Security Considerations

- The web interface is currently accessible to anyone who can reach the server
- Consider implementing authentication if deployed in a sensitive environment
- Be aware of privacy implications when tracking Bluetooth devices
- Secure your notification tokens and API keys in the .env file
- Regularly update dependencies for security patches
- Monitor logs for unauthorized access attempts
- Consider network segmentation for production deployments

## Development

### Project Structure
```
ble-scanner/
├── app.py              # Main BLE scanning logic
├── web_app.py          # Web dashboard application
├── config.py           # Configuration settings
├── notifications.py    # Notification system
├── create_db.py       # Database initialization
├── test_suite.py      # Comprehensive test suite
├── test_*.py          # Individual test modules
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── templates/         # Web templates
│   ├── dashboard.html
│   ├── 404.html
│   └── 500.html
└── README.md          # Documentation
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Run tests before committing:
   ```bash
   python test_suite.py
   ```
4. Submit a pull request with:
   - Description of changes
   - Test results
   - Updated documentation

## Changelog

### Version 2.0.1 (Latest)
Released: 2024-01-21

#### 🔧 Improvements
- Added comprehensive test suite
- Enhanced error handling for Bluetooth connectivity
- Improved notification system reliability
- Added detailed troubleshooting guide
- Created automated test and packaging script

#### 🧪 New Testing Tools
- Added test_notifications.py for notification system verification
- Added test_ble_scanner.py for BLE scanning validation
- Added test_and_package.sh for automated testing and distribution

### Version 2.0.0
Released: 2024-01-20

#### ✨ New Features
- Added human presence detection using RSSI threshold
- Implemented multi-channel notification system:
  - Discord webhook integration
  - Telegram bot notifications
  - WhatsApp message alerts
- Added .env support for secure configuration
- Created notification logging system

#### 🔧 Improvements
- Enhanced error handling for notification delivery
- Added RSSI threshold configuration
- Improved logging for notification events
- Added detailed setup documentation

#### 📦 Dependencies
- Added python-dotenv for environment management
- Added requests package for API communications

### Version 1.0.0
Released: 2024-01-01

#### 🚀 Initial Release
- Basic BLE device scanning
- Real-time web dashboard
- Device frequency tracking
- 24-hour activity visualization
- SQLite database integration
- Responsive Tailwind CSS design

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Run the test suite before committing:
   ```bash
   python test_suite.py
   ```
4. Submit a pull request with:
   - Description of changes
   - Test results
   - Updated documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.
