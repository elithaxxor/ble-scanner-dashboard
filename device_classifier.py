import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
from mac_vendor_lookup import MacLookup
from config import LOG_FILE, LOG_LEVEL

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeviceClassifier:
    def __init__(self):
        """Initialize the device classifier with necessary components"""
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        self.mac_lookup = MacLookup()
        self.is_trained = False
        
        # Download the latest MAC address database
        try:
            self.mac_lookup.update_vendors()
            logger.info("MAC vendor database updated successfully")
        except Exception as e:
            logger.error(f"Error updating MAC vendor database: {e}")
    
    def get_manufacturer(self, mac_address):
        """Look up the manufacturer of a device by its MAC address"""
        try:
            return self.mac_lookup.lookup(mac_address)
        except Exception as e:
            logger.warning(f"Could not lookup manufacturer for {mac_address}: {e}")
            return "Unknown"
    
    def extract_features(self, device_data):
        """Extract features from device data for classification"""
        features = {
            'rssi_mean': np.mean(device_data['rssi']),
            'rssi_std': np.std(device_data['rssi']),
            'frequency_count': device_data['frequency_count'],
            'time_span': (pd.to_datetime(device_data['last_seen']) - 
                         pd.to_datetime(device_data['first_seen'])).total_seconds(),
            'is_static': 1 if np.std(device_data['rssi']) < 5 else 0,
        }
        return features
    
    def predict_category(self, device_data):
        """Predict the category of a device based on its characteristics"""
        try:
            # Get manufacturer info
            manufacturer = self.get_manufacturer(device_data['mac_address'])
            
            # Basic rules for common device types
            name_lower = device_data['device_name'].lower()
            
            # Rule-based classification
            if any(keyword in manufacturer.lower() for keyword in ['apple', 'iphone', 'ipad']):
                if 'watch' in name_lower:
                    return 'Wearable'
                return 'Smartphone'
            
            if any(keyword in manufacturer.lower() for keyword in ['fitbit', 'garmin', 'samsung'] + 
                  ['watch' in name_lower]):
                return 'Wearable'
            
            if any(keyword in name_lower for keyword in ['speaker', 'headphone', 'airpod']):
                return 'Audio'
            
            if any(keyword in manufacturer.lower() for keyword in ['raspberry', 'arduino', 'espressif']):
                return 'IoT'
            
            # Feature-based classification for unknown devices
            features = self.extract_features(device_data)
            
            # If the classifier is not trained, use heuristics
            if not self.is_trained:
                if features['is_static']:
                    return 'IoT'
                if -60 <= features['rssi_mean'] <= -30:
                    return 'Smartphone'
                if features['rssi_std'] > 10:
                    return 'Wearable'
                return 'Unknown'
            
            # Use trained classifier if available
            feature_vector = np.array([list(features.values())])
            feature_vector_scaled = self.scaler.transform(feature_vector)
            return self.classifier.predict(feature_vector_scaled)[0]
            
        except Exception as e:
            logger.error(f"Error predicting category for device {device_data['mac_address']}: {e}")
            return 'Unknown'
    
    def train(self, training_data):
        """Train the classifier with labeled data"""
        try:
            features = []
            labels = []
            
            for device in training_data:
                feature_vector = self.extract_features(device)
                features.append(list(feature_vector.values()))
                labels.append(device['category'])
            
            X = np.array(features)
            y = np.array(labels)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train classifier
            self.classifier.fit(X_scaled, y)
            self.is_trained = True
            
            logger.info("Device classifier trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error training device classifier: {e}")
            return False

# Singleton instance
device_classifier = DeviceClassifier()
