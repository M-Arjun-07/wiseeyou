import os
import re
import ast

def debug_file_structure(file_path):
    """Debug the exact structure of a CSV file"""
    print(f"\n🔍 DEBUGGING: {file_path}")
    print("=" * 60)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        print(f"Total lines: {len(lines)}")
        
        # Find CSI_DATA lines
        csi_lines = [i for i, line in enumerate(lines) if line.startswith('CSI_DATA')]
        print(f"CSI_DATA lines found: {len(csi_lines)}")
        
        if csi_lines:
            # Analyze first few CSI lines
            for i in csi_lines[:3]:
                line = lines[i]
                print(f"\n--- Line {i+1} ---")
                print(f"Full line: {line[:200]}...")
                
                # Count commas
                comma_count = line.count(',')
                print(f"Comma count: {comma_count}")
                
                # Try to parse as CSV
                parts = line.split(',')
                print(f"Part count: {len(parts)}")
                
                # Show first 10 parts
                print("First 10 parts:")
                for j, part in enumerate(parts[:10]):
                    print(f"  {j}: '{part}'")
                
                # Look for CSI data
                csi_found = False
                for j, part in enumerate(parts):
                    if '[' in part and ']' in part:
                        print(f"✅ CSI data found in part {j}")
                        csi_found = True
                        # Try to extract and parse
                        try:
                            csi_str = part.strip().strip('"')
                            csi_data = ast.literal_eval(csi_str)
                            print(f"   CSI data length: {len(csi_data)}")
                            print(f"   First 5 values: {csi_data[:5]}")
                        except Exception as e:
                            print(f"   Error parsing CSI: {e}")
                
                if not csi_found:
                    print("❌ No complete CSI array found in this line")
                    # Check if CSI data spans multiple lines
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if '[' in line and ']' not in line and ']' in next_line:
                            print("⚠️  CSI data appears to span multiple lines!")
                            combined = line + next_line
                            print(f"Combined: {combined[:200]}...")
        
        else:
            print("❌ No CSI_DATA lines found!")
            print("First 3 lines of file:")
            for i, line in enumerate(lines[:3]):
                print(f"  {i+1}: {line}")
                
    except Exception as e:
        print(f"Error: {e}")

def main():
    dataset_path = "dataset"
    
    # Check one file from each gesture
    gestures = ['circleclockwise', 'waveright', 'upanddown']
    
    for gesture in gestures:
        gesture_path = os.path.join(dataset_path, gesture)
        if os.path.exists(gesture_path):
            csv_files = [f for f in os.listdir(gesture_path) if f.endswith('.csv')]
            if csv_files:
                sample_file = os.path.join(gesture_path, csv_files[0])
                debug_file_structure(sample_file)
                
                # Only check one file per gesture to avoid too much output
                break

if __name__ == "__main__":
    main()