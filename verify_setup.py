#!/usr/bin/env python3
"""
Alpaca Market Data SDK - Setup Verification Script
Verifies that the installation and basic functionality work correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all main components can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from alpaca_data import AlpacaClient
        print("  ✅ AlpacaClient imported successfully")
        
        from alpaca_data import Bar, Quote, Trade, Snapshot, News
        print("  ✅ Data models imported successfully")
        
        from alpaca_data import JSONFormatter, CSVFormatter, DataFrameFormatter
        print("  ✅ Formatters imported successfully")
        
        from alpaca_data import RateLimiter
        print("  ✅ RateLimiter imported successfully")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_client_initialization():
    """Test client initialization without credentials (should fail gracefully)."""
    print("\n🔍 Testing client initialization...")
    
    try:
        from alpaca_data import AlpacaClient
        
        # This should fail with appropriate error
        try:
            client = AlpacaClient()
            print("  ❌ Expected initialization to fail without credentials")
            return False
        except Exception as e:
            print(f"  ✅ Client initialization failed as expected: {type(e).__name__}")
            return True
            
    except Exception as e:
        print(f"  ❌ Unexpected error during client initialization test: {e}")
        return False

def test_environment_setup():
    """Check environment setup."""
    print("\n🔍 Testing environment setup...")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ .env file exists")
        
        with open(env_file) as f:
            content = f.read()
            if "your_api_key_here" in content:
                print("  ⚠️  .env file still contains placeholder values")
                print("     Remember to add your actual Alpaca API credentials")
            else:
                print("  ✅ .env file contains actual credentials")
    else:
        print("  ⚠️  .env file not found (copied from .env.example)")
    
    return True

def test_python_environment():
    """Test Python environment."""
    print("\n🔍 Testing Python environment...")
    
    print(f"  ✅ Python version: {sys.version}")
    print(f"  ✅ Working directory: {os.getcwd()}")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("  ✅ Running in virtual environment")
    else:
        print("  ⚠️  Not running in virtual environment")
    
    return True

def main():
    """Main verification function."""
    print("🚀 Alpaca Market Data SDK - Setup Verification")
    print("=" * 50)
    
    tests = [
        test_python_environment,
        test_imports,
        test_client_initialization,
        test_environment_setup,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    print(f"  ✅ Passed: {passed}/{total}")
    print(f"  ❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Alpaca Market Data SDK is ready to use.")
        print("\n📝 Next steps:")
        print("  1. Add your Alpaca API credentials to .env file")
        print("  2. Try the examples in the README.md")
        print("  3. Run the CLI tools: alpaca-bars --help")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)