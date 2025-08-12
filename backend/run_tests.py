#!/usr/bin/env python3
"""
Simple test runner script.
"""
import subprocess
import sys

def run_tests():
    """Run the test suite"""
    print("🧪 Running POI API Tests...")
    print("=" * 40)
    
    try:
        # Install test dependencies if needed
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "httpx"], 
                      capture_output=True, check=True)
        
        # Run tests
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=False, check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code: {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
