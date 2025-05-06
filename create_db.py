import sqlite3
import logging
from config import DB_PATH, LOG_FILE, LOG_LEVEL

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_db():
    """
    Initialize the SQLite database with the Devices table.
    Creates the table if it doesn't exist.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create the Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DeviceCategories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS Devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac_address TEXT UNIQUE,
                device_name TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                frequency_count INTEGER DEFAULT 1,
                rssi INTEGER,
                last_location TEXT DEFAULT 'bedroom',
                category_id INTEGER,
                manufacturer TEXT,
                is_known BOOLEAN DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (category_id) REFERENCES DeviceCategories(id)
            );

            -- Insert default device categories
            INSERT OR IGNORE INTO DeviceCategories (name, description) VALUES
                ('Smartphone', 'Mobile phones and smartphones'),
                ('Wearable', 'Smartwatches, fitness trackers, and other wearables'),
                ('Audio', 'Headphones, speakers, and other audio devices'),
                ('Computer', 'Laptops, desktops, and tablets'),
                ('IoT', 'Smart home devices and IoT sensors'),
                ('Unknown', 'Unidentified devices')
        ''')
        
        # Create index on mac_address for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_mac_address 
            ON Devices(mac_address)
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        print("Database initialized successfully at:", DB_PATH)
        
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        print(f"Error initializing database: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        print(f"Unexpected error: {e}")
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    initialize_db()
