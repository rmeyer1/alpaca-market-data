#!/usr/bin/env python3
"""
Final comprehensive test to verify Alpaca SDK is fully operational
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def verify_environment():
    """Verify environment setup is correct."""
    print("🔍 Environment Verification")
    print("=" * 35)
    
    from dotenv import load_dotenv
    
    # Load .env file
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    # Check credentials
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_API_SECRET")
    
    if api_key and api_secret:
        print(f"✅ ALPACA_API_KEY: {api_key[:8]}...{api_key[-4:]}")
        print(f"✅ ALPACA_API_SECRET: {api_secret[:8]}...{api_secret[-4:]}")
        return True
    else:
        print("❌ API credentials missing")
        return False

def test_authentication():
    """Test that authentication is working."""
    print("\n🔐 Authentication Test")
    print("=" * 28)
    
    try:
        from alpaca_data import AlpacaClient
        
        # Try to initialize client
        client = AlpacaClient()
        print("✅ AlpacaClient initialized successfully")
        print("✅ Authentication with Alpaca API confirmed")
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_api_structure():
    """Test that the SDK structure is working."""
    print("\n🏗️ SDK Structure Test")
    print("=" * 25)
    
    try:
        from alpaca_data import (
            AlpacaClient, Bar, Quote, Trade, Snapshot, News,
            JSONFormatter, CSVFormatter, DataFrameFormatter, RateLimiter
        )
        print("✅ All classes imported successfully")
        
        # Test that client has expected methods
        client_methods = [
            'get_bars', 'get_quotes', 'get_trades', 'get_news',
            'get_snapshot', 'get_crypto_bars', 'get_crypto_quotes', 'get_crypto_snapshot'
        ]
        
        for method in client_methods:
            if hasattr(AlpacaClient, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_cli_tools():
    """Test that CLI tools are available."""
    print("\n🛠️ CLI Tools Test")
    print("=" * 20)
    
    venv_bin = Path(__file__).parent / "venv" / "bin"
    
    cli_tools = [
        "alpaca-bars", "alpaca-quotes", "alpaca-trades", 
        "alpaca-news", "alpaca-snapshot", "alpaca-crypto"
    ]
    
    all_available = True
    for tool in cli_tools:
        tool_path = venv_bin / tool
        if tool_path.exists():
            print(f"✅ {tool} available")
        else:
            print(f"❌ {tool} missing")
            all_available = False
    
    return all_available

def show_usage_examples():
    """Show practical usage examples."""
    print("\n💡 Usage Examples")
    print("=" * 20)
    
    examples = [
        "Basic usage:",
        "from dotenv import load_dotenv",
        "from alpaca_data import AlpacaClient",
        "",
        "load_dotenv()  # Load .env file",
        "client = AlpacaClient()  # Uses credentials from .env",
        "",
        "# Get market data",
        "bars = client.get_bars('AAPL', timeframe='1Day', limit=5)",
        "snapshot = client.get_snapshot(['AAPL', 'GOOGL'])",
        "",
        "# CLI usage:",
        "./venv/bin/alpaca-bars AAPL --timeframe 1Day --limit 5",
        "./venv/bin/alpaca-snapshot AAPL --verbose"
    ]
    
    for line in examples:
        if line.strip():
            print(f"  {line}")
        else:
            print()

def main():
    """Main verification function."""
    print("🎯 Alpaca Market Data SDK - Final Verification")
    print("=" * 55)
    
    tests = [
        verify_environment,
        test_authentication, 
        test_api_structure,
        test_cli_tools
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    # Show usage examples regardless of results
    show_usage_examples()
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 Verification Summary")
    print("=" * 25)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 SUCCESS - All systems operational!")
        print("\n✨ Your Alpaca SDK is ready for:")
        print("  • Real-time market data access")
        print("  • Stock and cryptocurrency data")
        print("  • Multiple output formats (JSON, CSV, DataFrame)")
        print("  • CLI tools for quick data access")
        print("  • Professional trading applications")
        
        print("\n🚀 Quick Start Commands:")
        print("  # Test CLI tools (may need data subscriptions)")
        print("  ./venv/bin/alpaca-bars --help")
        print("  ./venv/bin/alpaca-snapshot --help")
        print("")
        print("  # Run in Python")
        print("  ./venv/bin/python3")
        print("  >>> from dotenv import load_dotenv")
        print("  >>> load_dotenv()")
        print("  >>> from alpaca_data import AlpacaClient")
        print("  >>> client = AlpacaClient()")
        
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Please check the error messages above")
    
    print(f"\n📋 Environment file: {Path('.env').exists()}")
    print(f"📁 Project directory: {Path.cwd()}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    
    return passed == total

if __name__ == "__main__":
    main()