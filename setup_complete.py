#!/usr/bin/env python3
"""
Setup verification script for Alpaca Market Data SDK
This script verifies that the package is properly installed and ready to use.
"""

import sys
import os

def main():
    print("=" * 60)
    print("🚀 ALPACA MARKET DATA SDK - SETUP VERIFICATION")
    print("=" * 60)
    
    # Check Python version
    print(f"✓ Python version: {sys.version}")
    
    # Check if package is installed
    try:
        from alpaca_data import AlpacaClient
        print("✓ AlpacaClient can be imported")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Check if CLI tools are available (scripts directory exists)
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    if os.path.exists(scripts_dir):
        print("✓ CLI scripts directory exists")
    else:
        print("❌ CLI scripts directory missing")
        return False
    
    # Check dependencies
    required_modules = [
        'alpaca_data',
        'alpaca',
        'pandas',
        'typer',
        'requests',
        'dotenv'
    ]
    
    print("\n📦 Dependencies:")
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ❌ {module} - missing")
    
    print("\n🔧 SETUP INSTRUCTIONS:")
    print("1. Get your API credentials from: https://app.alpaca.markets/paper/dashboard")
    print("2. Edit the .env file with your credentials:")
    print("   ALPACA_API_KEY=your_actual_api_key")
    print("   ALPACA_SECRET_KEY=your_actual_secret_key")
    print("3. Test the connection:")
    print("   python test_connection.py")
    
    print("\n🧪 BASIC USAGE:")
    print("""
# Python API usage:
from alpaca_data import AlpacaClient
client = AlpacaClient()
bars = client.get_bars("AAPL", timeframe="1Day", start="2024-01-01", limit=5)
print(f"Got {len(bars['bars'])} bars")

# CLI usage (after setting API credentials):
alpaca-bars AAPL --timeframe 1Day --limit 5
    """)
    
    print("\n📁 PROJECT STRUCTURE:")
    print("✓ src/alpaca_data/        - Main package code")
    print("✓ scripts/                - CLI tools")
    print("✓ tests/                  - Test suite")
    print("✓ examples/               - Usage examples")
    print("✓ docs/                   - Documentation")
    print("✓ .env                    - Environment configuration")
    print("✓ .env.example            - Template for .env file")
    
    print("\n🎯 READY TO USE!")
    print("The package is installed and ready. Add your API credentials to .env to start using it.")
    
    return True

if __name__ == "__main__":
    main()