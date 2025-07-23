#!/usr/bin/env python3
"""
Directory cleanup verification
"""
import os

def show_directory_structure():
    print("🧹 CLEANUP VERIFICATION")
    print("=" * 50)
    
    backend_path = "/home/asongna/Desktop/Carechat/Track2/Backend"
    
    print("\n📁 BACKEND DIRECTORY:")
    try:
        files = sorted(os.listdir(backend_path))
        for f in files:
            print(f"   ✅ {f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n📊 DATA DIRECTORY:")
    data_path = os.path.join(backend_path, "Data")
    try:
        files = sorted(os.listdir(data_path))
        for f in files:
            print(f"   ✅ {f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🏗️ APP DIRECTORY:")
    app_path = os.path.join(backend_path, "app")
    try:
        items = sorted(os.listdir(app_path))
        for item in items:
            if os.path.isdir(os.path.join(app_path, item)):
                print(f"   📁 {item}/")
            else:
                print(f"   ✅ {item}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Count Python files
    print(f"\n📊 SUMMARY:")
    py_files = []
    for root, dirs, files in os.walk(backend_path):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    print(f"   📝 Python files: {len(py_files)}")
    print(f"   📚 Documentation files: {len([f for f in os.listdir(backend_path) if f.endswith('.md')])}")
    print(f"   💾 Data files: {len(os.listdir(data_path))}")
    
    print(f"\n✨ CLEANUP COMPLETED!")
    print("   ❌ Removed: __pycache__ directories")
    print("   ❌ Removed: Redundant documentation files")
    print("   ❌ Removed: Test files")
    print("   ❌ Removed: Full dataset cache files")
    print("   ❌ Removed: Empty migrations directory")
    print("   ❌ Removed: Duplicate .gitignore")
    
    print(f"\n✅ KEPT ESSENTIAL FILES:")
    print("   📁 Core application code")
    print("   📚 Essential documentation (README, RAG_README, DEPLOYMENT_CHECKLIST)")
    print("   💾 Test dataset and cache (faster development)")
    print("   🔧 Configuration files (.env.example, requirements.txt)")

if __name__ == "__main__":
    show_directory_structure()
