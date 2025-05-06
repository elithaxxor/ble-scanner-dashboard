from flask_socketio import SocketIO, emit
import json
import logging
from datetime import datetime
from shapely.geometry import Point, Polygon
from config import LOG_FILE, LOG_LEVEL

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize SocketIO
socketio = SocketIO()

# Geofencing zones (example: rectangular areas defined by coordinates)
GEOFENCE_ZONES = {
    'entrance': Polygon([
        (-70, 2), (-70, 5),  # RSSI values as coordinates
        (-50, 5), (-50, 2)
    ]),
    'living_room': Polygon([
        (-65, 8), (-65, 12),
        (-45, 12), (-45, 8)
    ]),
    'bedroom': Polygon([
        (-75, 15), (-75, 18),
        (-55, 18), (-55, 15)
    ])
}

class RealtimeHandler:
    def __init__(self):
        """Initialize the realtime handler"""
        self.connected_clients = set()
        self.device_locations = {}
        self.setup_socketio_handlers()
    
    def setup_socketio_handlers(self):
        """Set up WebSocket event handlers"""
        
        @socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid
            self.connected_clients.add(client_id)
            logger.info(f"Client connected: {client_id}")
            
            # Send initial state
            emit('device_locations', self.device_locations)
        
        @socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid
            self.connected_clients.remove(client_id)
            logger.info(f"Client disconnected: {client_id}")
    
    def determine_zone(self, rssi, movement_pattern):
        """Determine which zone a device is in based on RSSI and movement"""
        try:
            # Create a point from RSSI and movement pattern
            point = Point(rssi, movement_pattern)
            
            # Check each zone
            for zone_name, zone_polygon in GEOFENCE_ZONES.items():
                if zone_polygon.contains(point):
                    return zone_name
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Error determining zone: {e}")
            return 'unknown'
    
    def calculate_movement_pattern(self, device_data):
        """Calculate a movement pattern score based on RSSI history"""
        try:
            rssi_values = device_data.get('rssi_history', [])
            if len(rssi_values) < 2:
                return 0
            
            # Calculate rate of RSSI change
            changes = [abs(rssi_values[i] - rssi_values[i-1]) 
                      for i in range(1, len(rssi_values))]
            
            # Return average change as movement score
            return sum(changes) / len(changes)
            
        except Exception as e:
            logger.error(f"Error calculating movement pattern: {e}")
            return 0
    
    def update_device_location(self, device_data):
        """Update device location and notify connected clients"""
        try:
            mac_address = device_data['mac_address']
            rssi = device_data['rssi']
            
            # Update device history
            if mac_address not in self.device_locations:
                self.device_locations[mac_address] = {
                    'rssi_history': [],
                    'zone_history': [],
                    'last_update': None
                }
            
            device_info = self.device_locations[mac_address]
            device_info['rssi_history'].append(rssi)
            
            # Keep last 10 readings
            if len(device_info['rssi_history']) > 10:
                device_info['rssi_history'].pop(0)
            
            # Calculate movement pattern
            movement_pattern = self.calculate_movement_pattern(device_info)
            
            # Determine zone
            current_zone = self.determine_zone(rssi, movement_pattern)
            device_info['zone_history'].append(current_zone)
            
            # Keep last 5 zone readings
            if len(device_info['zone_history']) > 5:
                device_info['zone_history'].pop(0)
            
            # Update timestamp
            device_info['last_update'] = datetime.now().isoformat()
            
            # Prepare update data
            update_data = {
                'mac_address': mac_address,
                'device_name': device_data.get('device_name', 'Unknown'),
                'current_zone': current_zone,
                'rssi': rssi,
                'movement_pattern': movement_pattern,
                'last_update': device_info['last_update']
            }
            
            # Notify all connected clients
            socketio.emit('device_update', update_data)
            
            logger.info(f"Device {mac_address} location updated: {current_zone}")
            
        except Exception as e:
            logger.error(f"Error updating device location: {e}")
    
    def get_zone_statistics(self):
        """Get statistics about devices in each zone"""
        try:
            stats = {zone: 0 for zone in GEOFENCE_ZONES.keys()}
            stats['unknown'] = 0
            
            for device_info in self.device_locations.values():
                if device_info['zone_history']:
                    current_zone = device_info['zone_history'][-1]
                    stats[current_zone] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting zone statistics: {e}")
            return {}

# Create singleton instance
realtime_handler = RealtimeHandler()
