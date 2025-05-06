import asyncio
import logging
import sqlite3
from datetime import datetime
from bleak import BleakScanner
from config import (
    DB_PATH, 
    SCAN_INTERVAL, 
    LOG_FILE, 
    LOG_LEVEL,
    HUMAN_RSSI_THRESHOLD
)
from notifications import send_all_notifications
from device_classifier import device_classifier
from realtime_handler import realtime_handler

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def update_device(mac_address, device_name, rssi, device_info=None):
    """
    Update device information in the database.
    If the device is new, create a new record and check for human presence.
    If it exists, update its last_seen timestamp and increment frequency_count.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now = datetime.now()

        # Check if device exists
        cursor.execute("SELECT frequency_count FROM Devices WHERE mac_address = ?", (mac_address,))
        result = cursor.fetchone()

        if result:
            # Update existing device
            new_count = result[0] + 1
            cursor.execute("""
                UPDATE Devices 
                SET last_seen = ?, frequency_count = ?, rssi = ?, device_name = ?
                WHERE mac_address = ?
            """, (now, new_count, rssi, device_name, mac_address))
            logger.info(f"Updated device {mac_address} (Count: {new_count})")
        else:
            # Get device category and manufacturer
            if device_info is None:
                device_info = {
                    'mac_address': mac_address,
                    'device_name': device_name,
                    'rssi': rssi,
                    'first_seen': now,
                    'last_seen': now,
                    'frequency_count': 1
                }
            
            category = device_classifier.predict_category(device_info)
            manufacturer = device_classifier.get_manufacturer(mac_address)
            
            # Insert new device with category and manufacturer
            cursor.execute("""
                INSERT INTO Devices 
                (mac_address, device_name, first_seen, last_seen, frequency_count, rssi,
                 manufacturer, category_id)
                VALUES (?, ?, ?, ?, 1, ?, ?,
                    (SELECT id FROM DeviceCategories WHERE name = ?))
            """, (mac_address, device_name, now, now, rssi, manufacturer, category))
            logger.info(f"New device detected: {mac_address} ({category})")

            # Update realtime location tracking
            realtime_handler.update_device_location({
                'mac_address': mac_address,
                'device_name': device_name,
                'rssi': rssi,
                'category': category,
                'manufacturer': manufacturer
            })

            # Check if the device's RSSI and category indicate human presence
            is_human_device = category in ['Smartphone', 'Wearable']
            if rssi is not None and rssi >= HUMAN_RSSI_THRESHOLD and is_human_device:
                zone = realtime_handler.determine_zone(
                    rssi, 
                    realtime_handler.calculate_movement_pattern({'rssi_history': [rssi]})
                )
                
                notify_message = (
                    f"🚨 Human Presence Detected!\n\n"
                    f"📱 Device: {device_name or 'Unknown Device'}\n"
                    f"📍 MAC Address: {mac_address}\n"
                    f"📶 Signal Strength (RSSI): {rssi}\n"
                    f"📱 Device Type: {category}\n"
                    f"🏢 Manufacturer: {manufacturer}\n"
                    f"🗺️ Zone: {zone}\n"
                    f"⏰ Time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                # Use asyncio.to_thread for non-blocking notification
                await asyncio.to_thread(send_all_notifications, notify_message)

        conn.commit()

    except sqlite3.Error as e:
        logger.error(f"Database error for device {mac_address}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing device {mac_address}: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

async def scan_devices():
    """
    Scan for nearby BLE devices and process each discovered device.
    """
    try:
        logger.info("Starting BLE scan...")
        devices = await BleakScanner.discover()
        
        for device in devices:
            if device.address and device.rssi:  # Ensure we have valid device data
                await update_device(
                    mac_address=device.address,
                    device_name=device.name or "Unknown",
                    rssi=device.rssi
                )
                
        logger.info(f"Scan complete. Found {len(devices)} devices.")
        
    except Exception as e:
        logger.error(f"Error during BLE scan: {e}")
        print(f"Scanning error: {e}")

async def main():
    """
    Main loop that continuously scans for BLE devices at set intervals.
    """
    print(f"BLE Scanner started. Scanning every {SCAN_INTERVAL} seconds...")
    logger.info("BLE Scanner service started")
    
    while True:
        try:
            await scan_devices()
            await asyncio.sleep(SCAN_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Scanner stopped by user")
            print("\nScanner stopped by user")
            break
            
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            print(f"Error in main loop: {e}")
            await asyncio.sleep(SCAN_INTERVAL)  # Wait before retrying

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
