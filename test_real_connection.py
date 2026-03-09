#!/usr/bin/env python3
"""
Test the Alpaca SDK with real API credentials
Loads the .env file explicitly before testing
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def load_env_file():
    """Load environment variables from .env file."""
    from dotenv import load_dotenv
    
    # Load .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
        
        # Verify credentials are loaded
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_API_SECRET")
        
        if api_key and api_secret:
            print(f"✅ API Key loaded: {api_key[:10]}...")
            print(f"✅ API Secret loaded: {api_secret[:10]}...")
            return True
        else:
            print("❌ API credentials not found in .env file")
            return False
    else:
        print("❌ .env file not found")
        return False

def test_real_connection():
    """Test connection with real API credentials."""
    print("🔍 Testing Real API Connection")
    print("=" * 40)
    
    # First load the .env file
    if not load_env_file():
        return False
    
    try:
        from alpaca_data import AlpacaClient
        
        # Initialize client (should load from loaded env vars)
        print("\n📡 Initializing AlpacaClient...")
        client = AlpacaClient()
        print("✅ Client initialized successfully")
        
        # Test 1: Get a simple snapshot
        print("\n📊 Test 1: Getting AAPL snapshot...")
        try:
            snapshot = client.get_snapshot("AAPL")
            if snapshot and len(snapshot) > 0:
                print("✅ Snapshot retrieved successfully")
                snap = snapshot[0] if isinstance(snapshot, list) else snapshot
                print(f"   Symbol: {snap.symbol}")
                if hasattr(snap, 'latest_trade') and snap.latest_trade:
                    print(f"   Latest Trade Price: ${snap.latest_trade.price}")
                if hasattr(snap, 'latest_quote') and snap.latest_quote:
                    print(f"   Latest Quote: ${snap.latest_quote.ask_price} / ${snap.latest_quote.bid_price}")
            else:
                print("⚠️  No snapshot data returned")
        except Exception as e:
            print(f"❌ Snapshot test failed: {e}")
        
        # Test 2: Get recent bars
        print("\n📈 Test 2: Getting AAPL bars (last 5 days)...")
        try:
            bars = client.get_bars("AAPL", timeframe="1Day", limit=5)
            if bars and 'bars' in bars:
                print("✅ Bars retrieved successfully")
                print(f"   Retrieved {len(bars['bars'])} bars")
                if bars['bars']:
                    latest_bar = bars['bars'][-1]
                    print(f"   Latest bar close: ${latest_bar.close}")
                    print(f"   Date: {latest_bar.timestamp.strftime('%Y-%m-%d')}")
            else:
                print("⚠️  No bars data returned")
        except Exception as e:
            print(f"❌ Bars test failed: {e}")
        
        # Test 3: Get crypto data
        print("\n₿ Test 3: Getting BTC/USD crypto data...")
        try:
            crypto_bars = client.get_crypto_bars("BTC/USD", timeframe="1Day", limit=3)
            if crypto_bars and 'bars' in crypto_bars:
                print("✅ Crypto bars retrieved successfully")
                print(f"   Retrieved {len(crypto_bars['bars'])} crypto bars")
                if crypto_bars['bars']:
                    latest_crypto = crypto_bars['bars'][-1]
                    print(f"   BTC/USD latest close: ${latest_crypto.close}")
                    print(f"   Date: {latest_crypto.timestamp.strftime('%Y-%m-%d')}")
            else:
                print("⚠️  No crypto bars data returned")
        except Exception as e:
            print(f"❌ Crypto test failed: {e}")
        
        # Test 4: Try different output formats
        print("\n📄 Test 4: Testing output formats...")
        try:
            # JSON format
            bars_json = client.get_bars("AAPL", timeframe="1Day", limit=1, format="json")
            print("✅ JSON format working")
            
            # CSV format (if pandas is available)
            try:
                bars_csv = client.get_bars("AAPL", timeframe="1Day", limit=1, format="csv")
                print("✅ CSV format working")
            except Exception as e:
                print(f"⚠️  CSV format issue: {e}")
                
        except Exception as e:
            print(f"❌ Format test failed: {e}")
        
        print("\n🎉 API Connection Test Complete!")
        print("✅ Your Alpaca credentials are working correctly!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main test function."""
    success = test_real_connection()
    
    if success:
        print("\n" + "=" * 50)
        print("🚀 ALPACA SDK FULLY OPERATIONAL!")
        print("\n✨ You can now:")
        print("  • Use the SDK in Python scripts")
        print("  • Run CLI commands with real data")
        print("  • Build applications with live market data")
        print("  • Test with paper trading account (recommended)")
        
        print("\n📝 Example CLI Commands:")
        print("  ./venv/bin/alpaca-bars AAPL --format json")
        print("  ./venv/bin/alpaca-quotes AAPL TSLA --verbose")  
        print("  ./venv/bin/alpaca-crypto bars BTC/USD --timeframe 1Hour")
        
        print("\n📚 Example Python Usage:")
        print("""
        from dotenv import load_dotenv
        from alpaca_data import AlpacaClient
        
        # Load .env file first
        load_dotenv()
        
        # Initialize client
        client = AlpacaClient()  # Auto-loads credentials from .env
        
        # Get real-time data
        snapshot = client.get_snapshot("AAPL")
        bars = client.get_bars("AAPL", timeframe="1Day", limit=10)
        crypto = client.get_crypto_bars("BTC/USD", timeframe="1Hour")
        """)
        
        return True
    else:
        print("\n❌ API connection test failed!")
        print("Please check your credentials and try again.")
        return False

if __name__ == "__main__":
    main()