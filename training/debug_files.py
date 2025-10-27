import os
import csv

def debug_files():
    dataset_path = "dataset"
    
    print("=== DEBUGGING DATASET FILES ===")
    
    for gesture in ['circleclockwise', 'waveright', 'upanddown']:
        gesture_path = os.path.join(dataset_path, gesture)
        
        if os.path.exists(gesture_path):
            print(f"\n{'='*50}")
            print(f"GESTURE: {gesture}")
            print(f"{'='*50}")
            
            files = [f for f in os.listdir(gesture_path) if f.endswith('.csv')]
            
            for file in files[:2]:  # Check first 2 files
                file_path = os.path.join(gesture_path, file)
                print(f"\n📄 FILE: {file}")
                print("-" * 40)
                
                try:
                    # Try different reading methods
                    print("Method 1: Read as text file:")
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    if lines:
                        print(f"Total lines: {len(lines)}")
                        print("First 3 lines:")
                        for i, line in enumerate(lines[:3]):
                            print(f"  Line {i+1}: {repr(line.strip())}")
                        
                        # Check if it has CSI_DATA format
                        if lines[0].startswith('type,seq,timestamp'):
                            print("✅ Header detected: type,seq,timestamp")
                        elif 'CSI_DATA' in lines[0]:
                            print("✅ CSI_DATA format detected")
                        else:
                            print("❌ Unknown format")
                            
                        # Check for CSI data pattern
                        for i, line in enumerate(lines[:5]):
                            if '[' in line and ']' in line:
                                print(f"✅ CSI array found in line {i+1}")
                                # Extract just the array part to see structure
                                start = line.find('[')
                                end = line.find(']') + 1
                                if start != -1 and end != -1:
                                    csi_part = line[start:end]
                                    print(f"   CSI data sample: {csi_part[:100]}...")
                    
                    print("\nMethod 2: Read as CSV:")
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        reader = csv.reader(f)
                        try:
                            first_row = next(reader)
                            print(f"First row has {len(first_row)} columns")
                            print(f"Column names/sample: {first_row[:5]}...")  # First 5 columns
                            
                            # Try to read a data row
                            try:
                                second_row = next(reader)
                                print(f"Second row sample: {second_row[:5]}...")
                            except StopIteration:
                                print("Only one row in file (probably header only)")
                                
                        except Exception as e:
                            print(f"Error reading CSV: {e}")
                            
                except Exception as e:
                    print(f"❌ Error reading file: {e}")

def check_specific_file(file_path):
    """Check a specific file in detail"""
    print(f"\n🔍 DETAILED CHECK: {file_path}")
    print("-" * 50)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        lines = content.split('\n')
        print(f"Total lines: {len(lines)}")
        
        # Find lines with CSI data
        csi_lines = [i for i, line in enumerate(lines) if '[' in line and ']' in line]
        print(f"Lines with CSI data: {len(csi_lines)}")
        
        if csi_lines:
            sample_line = lines[csi_lines[0]]
            print(f"\nSample CSI line (line {csi_lines[0] + 1}):")
            print(repr(sample_line))
            
            # Try to parse the CSI data
            try:
                import ast
                start = sample_line.find('[')
                end = sample_line.find(']') + 1
                if start != -1 and end != -1:
                    csi_str = sample_line[start:end]
                    csi_data = ast.literal_eval(csi_str)
                    print(f"✅ Successfully parsed CSI data: {len(csi_data)} values")
                    print(f"   First 10 values: {csi_data[:10]}")
            except Exception as e:
                print(f"❌ Error parsing CSI data: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_files()
    
    # Check a specific file if you want
    # check_specific_file("dataset/circleclockwise/circleclockwise.csv")