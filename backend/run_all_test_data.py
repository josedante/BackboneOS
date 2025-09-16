#!/usr/bin/env python3
"""
Script to run all existing test data creation scripts in the correct order
"""

import os
import sys
import subprocess
import django

# Configure Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, script_name
        ], capture_output=True, text=True, cwd='/app')
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {str(e)}")
        return False
    
    return True

def main():
    """Run all test data scripts in order"""
    print("🚀 BACKBONEOS TEST DATA SETUP")
    print("Running all existing test data creation scripts...")
    
    # List of scripts to run in order
    scripts = [
        ('create_divisions_data.py', 'Creating Divisions Data'),
        ('populate_products.py', 'Creating Products Data'),
        ('enhance_products_data.py', 'Enhancing Products Data'),
        ('entities/create_test_data.py', 'Creating Entities Data'),
        ('create_campaigns_data.py', 'Creating Campaigns Data'),
        ('create_offers_data.py', 'Creating Offers Data'),
    ]
    
    success_count = 0
    total_scripts = len(scripts)
    
    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
        else:
            print(f"⚠️ Continuing with next script...")
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successfully completed: {success_count}/{total_scripts} scripts")
    
    if success_count == total_scripts:
        print("🎉 All test data created successfully!")
        print("\n🌐 You can now test the frontend with comprehensive data")
    else:
        print("⚠️ Some scripts failed, but you can still proceed with frontend development")
    
    return success_count == total_scripts

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
