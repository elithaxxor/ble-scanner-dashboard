# Changelog

All notable changes to the BLE Scanner project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-01-21

### Added
- Comprehensive unit test suite (test_suite.py)
- Automated test runner with mock objects
- Unit tests for notification system
- Unit tests for BLE scanning functionality
- Integration tests for database operations

### Changed
- Enhanced error handling in notification system
- Improved RSSI threshold validation
- Updated documentation with testing instructions
- Reorganized project structure for better maintainability

### Fixed
- Error handling in BLE device detection
- Notification system reliability improvements
- Database connection handling
- RSSI threshold validation

## [2.0.0] - 2024-01-20

### Added
- Human presence detection using RSSI threshold
- Multi-channel notification system:
  - Discord webhook integration
  - Telegram bot notifications
  - WhatsApp message alerts
- Environment variable support
- Notification logging system

### Changed
- Enhanced error handling
- Improved logging system
- Updated configuration system
- Added detailed setup documentation

### Dependencies
- Added python-dotenv for environment management
- Added requests package for API communications

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Basic BLE device scanning
- Real-time web dashboard
- Device frequency tracking
- 24-hour activity visualization
- SQLite database integration
- Responsive Tailwind CSS design

### Dependencies
- Flask for web interface
- Bleak for BLE scanning
- SQLite for data storage
