import serial
import numpy as np
import joblib
import time
import ast
from collections import deque
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

class RealTimeGestureDetector:
    def __init__(self, port='COM3', baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
            
            # Load trained model
            self.model = joblib.load('realtime/gesture_model.pkl')
            
            # Filter
            self.sos_filter = signal.butter(4, 0.1, 'lowpass', output='sos')
            
            # Detection state
            self.gesture_history = deque(maxlen=5)
            self.last_detection_time = 0
            self.detection_cooldown = 3.0
            
            print("✅ Real-time detector initialized!")
            print(f"📊 Model classes: {self.model.classes_}")
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            raise
    
    def parse_realtime_data(self, data_line):
        """Parse real-time data from ESP32 (DATA, format)"""
        try:
            if data_line.startswith('DATA,'):
                parts = data_line.split(',', 3)
                if len(parts) >= 4:
                    rssi = float(parts[2])
                    csi_str = parts[3]
                    csi_data = ast.literal_eval(csi_str)
                    
                    return {
                        'rssi': rssi,
                        'csi_data': np.array(csi_data, dtype=float)
                    }
            return None
        except:
            return None
    
    def csi_to_amplitude(self, csi_data):
        """Convert CSI to amplitude"""
        if csi_data is None or len(csi_data) % 2 != 0:
            return None
            
        amplitudes = []
        for i in range(0, len(csi_data), 2):
            real = csi_data[i]
            imag = csi_data[i+1]
            amplitude = np.sqrt(real**2 + imag**2)
            amplitudes.append(amplitude)
            
        return np.array(amplitudes)
    
    def apply_filter(self, data):
        """Apply low-pass filter"""
        try:
            return signal.sosfiltfilt(self.sos_filter, data)
        except:
            return data
    
    def extract_features(self, data_point):
        """Extract features from data point (SAME as training)"""
        if data_point is None:
            return None
            
        csi_amplitude = self.csi_to_amplitude(data_point['csi_data'])
        if csi_amplitude is None:
            return None
        
        features = []
        csi_filtered = self.apply_filter(csi_amplitude)
        
        # Same 14 features as training
        features.extend([
            np.mean(csi_filtered),      # Mean amplitude
            np.std(csi_filtered),       # Standard deviation
            np.min(csi_filtered),       # Minimum
            np.max(csi_filtered),       # Maximum
            np.median(csi_filtered),    # Median
            np.percentile(csi_filtered, 25),  # 25th percentile
            np.percentile(csi_filtered, 75),  # 75th percentile
            data_point['rssi'],         # RSSI
            abs(data_point['rssi']),    # RSSI magnitude
            np.sum(csi_filtered),       # Total energy
            np.mean(np.diff(csi_filtered)), # Average difference
            np.std(np.diff(csi_filtered)),  # Std of differences
        ])
        
        # Subcarrier correlation features
        if len(csi_filtered) >= 30:
            group1 = csi_filtered[:10]
            group2 = csi_filtered[10:20]
            group3 = csi_filtered[20:30]
            
            if len(group1) == len(group2) == len(group3) == 10:
                corr12 = np.corrcoef(group1, group2)[0,1] if not np.isnan(np.corrcoef(group1, group2)[0,1]) else 0
                corr13 = np.corrcoef(group1, group3)[0,1] if not np.isnan(np.corrcoef(group1, group3)[0,1]) else 0
                features.extend([corr12, corr13])
            else:
                features.extend([0, 0])
        else:
            features.extend([0, 0])
            
        return features
    
    def run_detection(self):
        """Main detection loop"""
        print("\n" + "="*60)
        print("🎯 REAL-TIME GESTURE DETECTION")
        print("="*60)
        print("Gestures: circleclockwise, waveright, upanddown")
        print("Perform gestures between ESP32 devices")
        print("Press Ctrl+C to stop")
        print("-"*60)
        
        sample_count = 0
        last_status_time = time.time()
        
        try:
            while True:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    
                    if line:
                        data_point = self.parse_realtime_data(line)
                        
                        if data_point:
                            features = self.extract_features(data_point)
                            
                            if features is not None:
                                prediction = self.model.predict([features])[0]
                                confidence = np.max(self.model.predict_proba([features]))
                                
                                current_time = time.time()
                                
                                # High confidence detection
                                if confidence > 0.7 and prediction != "no_gesture":
                                    # Cooldown check
                                    if current_time - self.last_detection_time > self.detection_cooldown:
                                        self.gesture_history.append(prediction)
                                        
                                        # Require consistency (2 out of 3)
                                        if len(self.gesture_history) >= 3:
                                            recent = list(self.gesture_history)[-3:]
                                            if recent.count(prediction) >= 2:
                                                print(f"🎯 GESTURE DETECTED: {prediction.upper()}! (confidence: {confidence:.3f})")
                                                self.last_detection_time = current_time
                                                self.gesture_history.clear()
                                
                                sample_count += 1
                                
                                # Status update every 3 seconds
                                if current_time - last_status_time > 3.0:
                                    proba = self.model.predict_proba([features])[0]
                                    class_names = self.model.classes_
                                    status = " | ".join([f"{name}:{proba[i]:.2f}" for i, name in enumerate(class_names)])
                                    print(f"📊 Monitoring... [{status}] | Samples: {sample_count}")
                                    last_status_time = current_time
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n🛑 Detection stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.ser.close()

def main():
    try:
        # Change port to your ESP32 RX COM port
        detector = RealTimeGestureDetector(port='COM3')
        detector.run_detection()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        print("Make sure to:")
        print("1. Train the model first (run 2_train_model.py)")
        print("2. Check COM port")
        print("3. Ensure ESP32 receiver is connected and sending data")

if __name__ == "__main__":
    main()