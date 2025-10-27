from flask import Flask, render_template, jsonify
import serial
import numpy as np
import joblib
import time
import ast
from scipy import signal
import threading
from collections import deque
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Global variables for real-time detection
current_gesture = "No Gesture"
confidence = 0.0
is_detecting = False
serial_connection = None
detection_count = 0

class WebGestureDetector:
    def __init__(self, port='COM3'):
        self.port = port
        self.model = joblib.load('../realtime/gesture_model.pkl')
        self.sos_filter = signal.butter(4, 0.1, 'lowpass', output='sos')
        self.gesture_history = deque(maxlen=5)
        
    def parse_realtime_data(self, data_line):
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
        try:
            return signal.sosfiltfilt(self.sos_filter, data)
        except:
            return data
    
    def extract_features(self, data_point):
        if data_point is None:
            return None
            
        csi_amplitude = self.csi_to_amplitude(data_point['csi_data'])
        if csi_amplitude is None:
            return None
        
        features = []
        csi_filtered = self.apply_filter(csi_amplitude)
        
        features.extend([
            np.mean(csi_filtered), np.std(csi_filtered), np.min(csi_filtered),
            np.max(csi_filtered), np.median(csi_filtered), np.percentile(csi_filtered, 25),
            np.percentile(csi_filtered, 75), data_point['rssi'], abs(data_point['rssi']),
            np.sum(csi_filtered), np.mean(np.diff(csi_filtered)), np.std(np.diff(csi_filtered)),
        ])
        
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
    
    def start_detection(self):
        global current_gesture, confidence, is_detecting, serial_connection, detection_count
        
        try:
            serial_connection = serial.Serial(self.port, 115200, timeout=1)
            time.sleep(2)
            is_detecting = True
            detection_count = 0
            
            print("🌐 Web detection started...")
            
            while is_detecting:
                if serial_connection.in_waiting > 0:
                    line = serial_connection.readline().decode('utf-8').strip()
                    
                    if line:
                        data_point = self.parse_realtime_data(line)
                        
                        if data_point:
                            features = self.extract_features(data_point)
                            
                            if features is not None:
                                prediction = self.model.predict([features])[0]
                                current_confidence = np.max(self.model.predict_proba([features]))
                                
                                # Update global variables
                                current_gesture = prediction
                                confidence = current_confidence
                                
                                if current_confidence > 0.7 and prediction != "No Gesture":
                                    detection_count += 1
                                    print(f"🌐 Detection: {prediction} (confidence: {current_confidence:.3f})")
                                
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Detection error: {e}")
        finally:
            if serial_connection:
                serial_connection.close()
            is_detecting = False

detector = WebGestureDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gesture')
def get_gesture():
    return jsonify({
        'gesture': current_gesture,
        'confidence': round(confidence, 3),
        'detection_count': detection_count
    })

@app.route('/api/start_detection')
def start_detection():
    global is_detecting
    if not is_detecting:
        thread = threading.Thread(target=detector.start_detection)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/api/stop_detection')
def stop_detection():
    global is_detecting
    is_detecting = False
    return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    print("🌐 Starting Web Interface...")
    print("📱 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)