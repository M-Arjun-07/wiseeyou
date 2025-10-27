import pandas as pd
import numpy as np
import os
import glob
import ast
from scipy import signal
import joblib
import warnings
warnings.filterwarnings('ignore')

class DatasetProcessor:
    def __init__(self):
        self.sos_filter = signal.butter(4, 0.1, 'lowpass', output='sos')
        
    def parse_csi_line(self, line):
        """Parse CSI data line where CSI array is split across columns"""
        try:
            line = line.strip()
            if not line:
                return None
                
            # Skip header line
            if line.startswith('type,seq,timestamp'):
                return None
                
            # Only process CSI_DATA lines
            if not line.startswith('CSI_DATA'):
                return None
                
            # Split the line
            parts = line.split(',')
            
            # We expect at least 28 columns + 104 CSI values = 132 parts
            if len(parts) < 28:
                return None
                
            # Extract RSSI (index 6)
            rssi = int(parts[6])
            
            # The CSI data starts from column 27 (index 27) onwards
            # We need to extract parts[27] to parts[27+103] for the 104 CSI values
            csi_parts = parts[27:27+104]
            
            # Convert to float array
            csi_data = []
            for val in csi_parts:
                # Remove any quotes or brackets
                clean_val = val.strip().strip('"').strip('[').strip(']')
                if clean_val:
                    try:
                        csi_data.append(float(clean_val))
                    except:
                        # If conversion fails, skip this value
                        continue
            
            if len(csi_data) != 104:
                # print(f"Debug: Expected 104 CSI values, got {len(csi_data)}")
                return None
                
            return {
                'rssi': rssi,
                'csi_data': np.array(csi_data, dtype=float)
            }
            
        except Exception as e:
            # print(f"Debug parse error: {e}")
            return None
    
    def csi_to_amplitude(self, csi_data):
        """Convert CSI real/imaginary pairs to amplitude"""
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
    
    def extract_features(self, csi_amplitudes, rssi):
        """Extract features from CSI data"""
        if csi_amplitudes is None or len(csi_amplitudes) == 0:
            return None
            
        features = []
        
        # CSI statistical features
        csi_filtered = self.apply_filter(csi_amplitudes)
        
        # Basic statistical features
        features.extend([
            np.mean(csi_filtered),      # Mean amplitude
            np.std(csi_filtered),       # Standard deviation
            np.min(csi_filtered),       # Minimum
            np.max(csi_filtered),       # Maximum
            np.median(csi_filtered),    # Median
            np.percentile(csi_filtered, 25),  # 25th percentile
            np.percentile(csi_filtered, 75),  # 75th percentile
        ])
        
        # RSSI features
        features.extend([
            rssi,
            abs(rssi)  # RSSI magnitude
        ])
        
        # Additional CSI features
        features.extend([
            np.sum(csi_filtered),           # Total energy
            np.mean(np.diff(csi_filtered)), # Average difference
            np.std(np.diff(csi_filtered)),  # Std of differences
        ])
        
        # Subcarrier correlation features
        if len(csi_filtered) >= 30:
            # Split into 3 groups for correlation
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
    
    def process_csv_file(self, file_path, gesture_label):
        """Process a single CSV file"""
        features_list = []
        labels_list = []
        
        try:
            print(f"   Processing: {os.path.basename(file_path)}")
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            sample_count = 0
            line_count = 0
            
            for line in lines:
                line_count += 1
                
                # Parse the data line
                data_point = self.parse_csi_line(line)
                
                if data_point is not None:
                    # Convert CSI to amplitude
                    csi_amplitude = self.csi_to_amplitude(data_point['csi_data'])
                    
                    if csi_amplitude is not None:
                        # Extract features
                        features = self.extract_features(csi_amplitude, data_point['rssi'])
                        
                        if features is not None:
                            features_list.append(features)
                            labels_list.append(gesture_label)
                            sample_count += 1
            
            print(f"      Total lines: {line_count}")
            print(f"      Samples extracted: {sample_count}")
            
        except Exception as e:
            print(f"      Error processing {file_path}: {e}")
            
        return features_list, labels_list
    
    def process_all_gestures(self, dataset_path):
        """Process all gestures in the dataset"""
        gestures = {
            'circleclockwise': 'circleclockwise',
            'waveright': 'waveright', 
            'upanddown': 'upanddown'
        }
        
        all_features = []
        all_labels = []
        
        for folder_name, gesture_label in gestures.items():
            gesture_path = os.path.join(dataset_path, folder_name)
            
            if not os.path.exists(gesture_path):
                print(f"❌ Folder not found: {gesture_path}")
                continue
                
            print(f"\n📁 Processing {gesture_label}...")
            
            # Find all CSV files in the folder
            csv_files = glob.glob(os.path.join(gesture_path, "*.csv"))
            
            if not csv_files:
                print(f"   ⚠️  No CSV files found in {gesture_path}")
                continue
            
            total_samples = 0
            for csv_file in csv_files:
                features, labels = self.process_csv_file(csv_file, gesture_label)
                all_features.extend(features)
                all_labels.extend(labels)
                total_samples += len(features)
                
            print(f"   ✅ {gesture_label}: {total_samples} total samples")
        
        print(f"\n📊 TOTAL DATASET: {len(all_features)} samples")
        
        if len(all_features) > 0:
            # Print class distribution
            unique_labels, counts = np.unique(all_labels, return_counts=True)
            print("\n📈 Class Distribution:")
            for label, count in zip(unique_labels, counts):
                print(f"   {label}: {count} samples ({count/len(all_features)*100:.1f}%)")
                
            print(f"\n📐 Feature vector shape: {np.array(all_features).shape}")
        else:
            print("❌ No data processed!")
            print("The CSI data format might be different than expected.")
        
        return np.array(all_features), np.array(all_labels)

def main():
    processor = DatasetProcessor()
    
    print("=== CSI GESTURE DATASET PROCESSING ===")
    print("Processing: circleclockwise, waveright, upanddown")
    print("Using parser for split CSI data (131 columns)...")
    
    # Process dataset
    features, labels = processor.process_all_gestures('dataset')
    
    if len(features) == 0:
        return
    
    # Save processed data
    os.makedirs('training/models', exist_ok=True)
    processed_data = {
        'features': features,
        'labels': labels
    }
    
    joblib.dump(processed_data, 'training/models/processed_dataset.pkl')
    print(f"\n💾 Saved processed data to 'training/models/processed_dataset.pkl'")

if __name__ == "__main__":
    main()