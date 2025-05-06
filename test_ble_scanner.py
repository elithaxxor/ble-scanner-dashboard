import asyncio
import logging
from datetime import datetime
from bleak import BleakScanner
from config import LOG_FILE, LOG_LEVEL, HUMAN_RSSI_THRESHOLD
from notifications import send_all_notifications

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ble_scan():
    """Test BLE scanning functionality and RSSI threshold detection."""
    print("\nTesting BLE Scanner...")
    print(f"RSSI Threshold for human detection: {HUMAN_RSSI_THRESHOLD}")
    print("\nScanning for nearby devices (10 seconds)...")
    
    try:
        devices = await BleakScanner.discover(timeout=10)
        
        if not devices:
            print("❌ No BLE devices found. Please ensure Bluetooth is enabled.")
            return
        
        print(f"\n✅ Found {len(devices)} devices!")
        print("\nDevice Analysis:")
        print("-" * 70)
        print(f"{'MAC Address':<20} {'Name':<20} {'RSSI':<10} {'Human?':<10}")
        print("-" * 70)
        
        human_detected = False
        for device in devices:
            is_human = device.rssi >= HUMAN_RSSI_THRESHOLD if device.rssi else False
            status = "👤 YES" if is_human else "NO"
            print(f"{device.address:<20} {(device.name or 'Unknown'):<20} {str(device.rssi):<10} {status:<10}")
            
            if is_human and not human_detected:
                human_detected = True
                notify_message = (
                    f"🚨 Test: Human Presence Detected!\n\n"
                    f"📱 Device: {device.name or 'Unknown Device'}\n"
                    f"📍 MAC Address: {device.address}\n"
                    f"📶 Signal Strength (RSSI): {device.rssi}\n"
                    f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                print("\nSending test notification for human presence...")
                await asyncio.to_thread(send_all_notifications, notify_message)
        
        print("\nTest Summary:")
        print("-" * 30)
        print(f"Total Devices: {len(devices)}")
        print(f"Human Presence: {'Detected' if human_detected else 'Not Detected'}")
        
    except Exception as e:
        logger.error(f"Error during BLE scan test: {e}")
        print(f"\n❌ Error during test: {e}")
        return

if __name__ == "__main__":
    print("Starting BLE Scanner Test Suite...")
    asyncio.run(test_ble_scan())
