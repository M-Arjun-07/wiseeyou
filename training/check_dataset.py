import os
import glob

def inspect_dataset():
    """Inspect the dataset structure and file contents"""
    dataset_path = "dataset"
    
    print("=== DATASET INSPECTION ===")
    
    gestures = ['circleclockwise', 'waveright', 'upanddown']
    
    for gesture in gestures:
        gesture_path = os.path.join(dataset_path, gesture)
        
        print(f"\n📁 {gesture}:")
        
        if not os.path.exists(gesture_path):
            print("   ❌ Folder does not exist")
            continue
        
        # Count files by extension
        all_files = os.listdir(gesture_path)
        csv_files = [f for f in all_files if f.endswith('.csv')]
        cs_files = [f for f in all_files if f.endswith('.cs')]
        c_files = [f for f in all_files if f.endswith('.c')]
        other_files = [f for f in all_files if not f.endswith(('.csv', '.cs', '.c', '.py'))]
        
        print(f"   📄 CSV files: {len(csv_files)}")
        print(f"   📄 CS files: {len(cs_files)}")
        print(f"   📄 C files: {len(c_files)}")
        print(f"   📄 Other files: {len(other_files)}")
        
        # Show first few files
        if csv_files:
            print("   CSV files:")
            for f in csv_files[:3]:
                print(f"      {f}")
            if len(csv_files) > 3:
                print(f"      ... and {len(csv_files) - 3} more")
        
        # Check file contents
        if csv_files:
            sample_file = os.path.join(gesture_path, csv_files[0])
            print(f"\n   Sample of first CSV file ({csv_files[0]}):")
            try:
                with open(sample_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:5]  # First 5 lines
                    for i, line in enumerate(lines):
                        print(f"      Line {i+1}: {line.strip()[:100]}...")
            except Exception as e:
                print(f"      Error reading file: {e}")

def check_sample_data():
    """Check if sample data matches expected format"""
    print("\n=== CHECKING DATA FORMAT ===")
    
    # Test with the real-time data format we know works
    test_line = "DATA,2817,-54,[-18,-12,-30,-9,-9,-3,-1,-23,-7,22,24,-4,1,0,23,9,10,2,-19,23,25,-23,11,-4,-1,-9,-26,21,-19,19,11,-21,-24,2,-6,-27,23,22,-8,-25,11,-9,9,13,-21,7,-17,9,-28,8,-23,0,27,22,-29,23,-2,-2,-14,-7,-28,-16,-12,-3,-9,19,-13,-3,-6,-12,17,-7,-22,2,9,-22,1,24,0,-14,7,-28,0,-18,-30,6,8,-7,4,7,-7,-26,-15,-30,7,-19,-8,-20,-29,-29,28,6,11,3]"
    
    print("Testing with known good format:")
    print(f"Sample: {test_line[:100]}...")
    
    if test_line.startswith('DATA,'):
        print("✅ Format matches real-time data")
    else:
        print("❌ Format doesn't match")

if __name__ == "__main__":
    inspect_dataset()
    check_sample_data()