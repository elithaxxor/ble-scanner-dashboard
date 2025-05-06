import asyncio
import logging
from notifications import send_all_notifications
from config import LOG_FILE, LOG_LEVEL

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_notifications():
    """Test all notification channels with a test message."""
    test_message = (
        "🧪 Test Notification\n\n"
        "This is a test message from the BLE Scanner.\n"
        "If you receive this, notifications are working correctly!"
    )
    
    logger.info("Starting notification test...")
    results = await asyncio.to_thread(send_all_notifications, test_message)
    
    # Check results
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"\nTest Results ({success_count}/{total_count} channels successful):")
    print("-" * 50)
    for channel, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{channel.title()}: {status}")
    print("-" * 50)
    
    if success_count == 0:
        print("\n⚠️  All notifications failed. Please check your configuration.")
    elif success_count < total_count:
        print("\n⚠️  Some notifications failed. Check the log for details.")
    else:
        print("\n✨ All notifications working correctly!")

if __name__ == "__main__":
    print("Testing BLE Scanner Notification System...")
    asyncio.run(test_notifications())
