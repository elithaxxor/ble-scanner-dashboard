from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime
import logging
from config import DB_PATH, WEB_HOST, WEB_PORT, DEBUG_MODE, LOG_FILE, LOG_LEVEL

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_db_connection():
    """Create a database connection and return it with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_timestamp(timestamp_str):
    """Format timestamp string to a more readable format"""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

@app.template_filter('datetime')
def datetime_filter(timestamp_str):
    """Template filter for formatting timestamps"""
    return format_timestamp(timestamp_str)

@app.route('/')
def dashboard():
    """Main dashboard route"""
    try:
        conn = get_db_connection()
        
        # Get device statistics
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_devices,
                SUM(frequency_count) as total_visits,
                MAX(last_seen) as last_detection
            FROM Devices
        """).fetchone()
        
        # Get recent devices with their details
        devices = conn.execute("""
            SELECT * FROM Devices 
            ORDER BY last_seen DESC, frequency_count DESC 
            LIMIT 50
        """).fetchall()
        
        conn.close()
        
        return render_template('dashboard.html', 
                             devices=devices, 
                             stats=stats)
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('error.html', error=str(e))

@app.route('/api/devices')
def get_devices():
    """API endpoint for getting device data"""
    try:
        conn = get_db_connection()
        
        # Get device details
        devices = conn.execute("""
            SELECT 
                mac_address,
                device_name,
                first_seen,
                last_seen,
                frequency_count,
                rssi,
                last_location
            FROM Devices
            ORDER BY last_seen DESC, frequency_count DESC
            LIMIT 100
        """).fetchall()
        
        # Get overall statistics
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total_devices,
                SUM(frequency_count) as total_visits,
                MAX(last_seen) as last_detection
            FROM Devices
        """).fetchone()
        
        # Get hourly activity for the last 24 hours
        hourly_stats = conn.execute("""
            SELECT 
                strftime('%Y-%m-%d %H:00:00', last_seen) as hour,
                COUNT(DISTINCT mac_address) as unique_devices,
                SUM(frequency_count) as total_detections
            FROM Devices
            WHERE last_seen >= datetime('now', '-24 hours')
            GROUP BY strftime('%Y-%m-%d %H:00:00', last_seen)
            ORDER BY hour DESC
        """).fetchall()
        
        conn.close()
        
        return jsonify({
            'devices': [dict(row) for row in devices],
            'overall': dict(stats),
            'hourly': [dict(row) for row in hourly_stats]
        })
    
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    print(f"Starting web interface on {WEB_HOST}:{WEB_PORT}")
    app.run(host=WEB_HOST, port=WEB_PORT, debug=DEBUG_MODE)
