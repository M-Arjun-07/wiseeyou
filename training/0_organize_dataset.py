import os
import shutil
import glob

def organize_dataset():
    """Organize dataset files and fix extensions"""
    dataset_path = "dataset"
    
    # Define gesture folders and their correct file extensions
    gestures = {
        'circleclockwise': ['circleclockwise.cs', 'circleclockwise1.c', 'circleclockwise2.c'],
        'waveright': ['waveright'],  # This folder might have files inside
        'upanddown': ['upanddown.csv', 'upanddown1.csv', 'upanddown2.csv']
    }
    
    print("=== DATASET ORGANIZATION ===")
    
    for gesture, files in gestures.items():
        gesture_path = os.path.join(dataset_path, gesture)
        
        # Create gesture folder if it doesn't exist
        if not os.path.exists(gesture_path):
            os.makedirs(gesture_path)
            print(f"📁 Created folder: {gesture_path}")
        
        # Process each file
        for file_pattern in files:
            # Search for files with this pattern
            matching_files = []
            
            # Check if it's a file in root dataset directory
            if os.path.isfile(os.path.join(dataset_path, file_pattern)):
                matching_files.append(os.path.join(dataset_path, file_pattern))
            
            # Also check for files with similar patterns
            for root, dirs, all_files in os.walk(dataset_path):
                for f in all_files:
                    if file_pattern in f and not f.endswith('.py'):
                        matching_files.append(os.path.join(root, f))
            
            # Move and rename files
            for file_path in matching_files:
                if os.path.isfile(file_path):
                    # Get the base filename
                    filename = os.path.basename(file_path)
                    
                    # Create new filename with .csv extension
                    new_filename = filename
                    if not new_filename.endswith('.csv'):
                        new_filename = os.path.splitext(filename)[0] + '.csv'
                    
                    new_filepath = os.path.join(gesture_path, new_filename)
                    
                    # Only move if source and destination are different
                    if file_path != new_filepath:
                        shutil.copy2(file_path, new_filepath)
                        print(f"📄 Copied: {filename} -> {gesture}/{new_filename}")
    
    print("\n✅ Dataset organization complete!")
    
    # Verify the structure
    verify_structure()

def verify_structure():
    """Verify the dataset structure"""
    print("\n=== VERIFYING DATASET STRUCTURE ===")
    
    dataset_path = "dataset"
    gestures = ['circleclockwise', 'waveright', 'upanddown']
    
    for gesture in gestures:
        gesture_path = os.path.join(dataset_path, gesture)
        
        if os.path.exists(gesture_path):
            csv_files = [f for f in os.listdir(gesture_path) if f.endswith('.csv')]
            other_files = [f for f in os.listdir(gesture_path) if not f.endswith('.csv') and not f.endswith('.py')]
            
            print(f"📁 {gesture}:")
            print(f"   ✅ CSV files: {len(csv_files)}")
            if other_files:
                print(f"   ⚠️  Other files: {len(other_files)}")
                
            # Show file list
            for csv_file in csv_files[:5]:  # Show first 5 files
                print(f"      📄 {csv_file}")
            if len(csv_files) > 5:
                print(f"      ... and {len(csv_files) - 5} more")
                
        else:
            print(f"❌ {gesture}: Folder not found")
    
    total_files = sum([len([f for f in os.listdir(os.path.join(dataset_path, g)) if f.endswith('.csv')]) 
                      for g in gestures if os.path.exists(os.path.join(dataset_path, g))])
    print(f"\n📊 Total CSV files: {total_files}")

if __name__ == "__main__":
    organize_dataset()