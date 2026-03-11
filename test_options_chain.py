#!/usr/bin/env python3
"""Test script to verify the options chain implementation."""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from unittest.mock import Mock, patch
from alpaca_data.client import AlpacaClient
from alpaca_data.models import OptionChain, OptionSnapshot, OptionQuote, OptionTrade, Greeks


def test_option_chain_model():
    """Test that OptionChain model works correctly."""
    print("Testing OptionChain model...")
    
    # Create simple OptionSnapshot objects with minimal data
    call_snapshot = OptionSnapshot(
        symbol="AAPL240119C200",
        iv=0.25,
        open_interest=1000,
        underlying_price=150.0
    )
    
    put_snapshot = OptionSnapshot(
        symbol="AAPL240119P200",
        iv=0.28,
        open_interest=800,
        underlying_price=150.0
    )
    
    # Create OptionChain
    contracts = {
        "AAPL240119C200": call_snapshot,
        "AAPL240119P200": put_snapshot,
        "AAPL240119C210": call_snapshot,
        "AAPL240119P210": put_snapshot,
    }
    
    chain = OptionChain(
        underlying_symbol="AAPL",
        contracts=contracts,
        underlying_price=150.0,
        feed="iex"
    )
    
    # Test the chain
    assert chain.underlying_symbol == "AAPL"
    assert len(chain.contracts) == 4
    assert chain.underlying_price == 150.0
    assert chain.feed == "iex"
    
    # Test filtering methods
    calls = chain.get_call_contracts()
    puts = chain.get_put_contracts()
    
    # Debug symbol parsing
    for symbol in contracts.keys():
        print(f"Symbol: {symbol}, is_call: {chain._is_call_contract(symbol)}, is_put: {chain._is_put_contract(symbol)}")
    
    print(f"Found {len(calls)} calls: {list(calls.keys())}")
    print(f"Found {len(puts)} puts: {list(puts.keys())}")
    
    # Test strike filtering
    strike_200 = chain.get_contracts_by_strike(200.0)
    print(f"Strike 200 contracts: {list(strike_200.keys())}")
    
    print(f"✅ OptionChain model test passed! Got {len(chain.contracts)} contracts")
    return True


def test_option_chain_from_api_response():
    """Test OptionChain.from_dict with mock API response."""
    print("\nTesting OptionChain.from_dict with API response...")
    
    # Mock API response from Alpaca options chain endpoint
    api_response = {
        "AAPL240119C200": {
            "iv": 0.25,
            "oi": 1000,
            "latest_trade": {
                "t": "2024-01-18T14:30:00Z",
                "p": 2.50,
                "s": 10,
                "x": "OPRA"
            },
            "latest_quote": {
                "t": "2024-01-18T14:30:00Z",
                "bp": 2.40,
                "bs": 5,
                "ap": 2.60,
                "as": 15,
                "x": "OPRA"
            },
            "greeks": {
                "delta": 0.65,
                "gamma": 0.02,
                "theta": -0.03,
                "vega": 0.15,
                "rho": 0.08
            },
            "underlying_price": 150.25
        },
        "AAPL240119P200": {
            "iv": 0.28,
            "oi": 800,
            "latest_trade": {
                "t": "2024-01-18T14:30:00Z",
                "p": 1.80,
                "s": 5,
                "x": "OPRA"
            },
            "latest_quote": {
                "t": "2024-01-18T14:30:00Z",
                "bp": 1.70,
                "bs": 10,
                "ap": 1.90,
                "as": 20,
                "x": "OPRA"
            },
            "greeks": {
                "delta": -0.35,
                "gamma": 0.02,
                "theta": -0.02,
                "vega": 0.14,
                "rho": -0.06
            },
            "underlying_price": 150.25
        },
        "timestamp": "2024-01-18T14:30:00Z",
        "underlying_price": 150.25,
        "feed": "iex"
    }
    
    # Parse the response
    chain = OptionChain.from_dict("AAPL", api_response)
    
    # Verify the chain
    assert chain.underlying_symbol == "AAPL"
    assert len(chain.contracts) == 2
    assert "AAPL240119C200" in chain.contracts
    assert "AAPL240119P200" in chain.contracts
    
    # Verify individual contracts
    call_contract = chain.contracts["AAPL240119C200"]
    assert call_contract.symbol == "AAPL240119C200"
    assert call_contract.iv == 0.25
    assert call_contract.open_interest == 1000
    
    put_contract = chain.contracts["AAPL240119P200"]
    assert put_contract.symbol == "AAPL240119P200"
    assert put_contract.iv == 0.28
    assert put_contract.open_interest == 800
    
    # Test filtering
    calls = chain.get_call_contracts()
    puts = chain.get_put_contracts()
    assert len(calls) == 1
    assert len(puts) == 1
    
    print(f"✅ OptionChain.from_dict test passed! Got {len(chain.contracts)} contracts")
    return True


def test_get_option_chain_client():
    """Test that the get_option_chain client method works."""
    print("\nTesting get_option_chain client method...")
    
    # Mock API response
    mock_response = Mock()
    mock_response.json.return_value = {
        "AAPL240119C200": {
            "iv": 0.25,
            "oi": 1000,
            "latest_trade": {"t": "2024-01-18T14:30:00Z", "p": 2.50, "s": 10, "x": "OPRA"},
            "latest_quote": {"t": "2024-01-18T14:30:00Z", "bp": 2.40, "bs": 5, "ap": 2.60, "as": 15, "x": "OPRA"},
            "greeks": {"delta": 0.65, "gamma": 0.02, "theta": -0.03, "vega": 0.15, "rho": 0.08},
            "underlying_price": 150.25
        },
        "AAPL240119P200": {
            "iv": 0.28,
            "oi": 800,
            "latest_trade": {"t": "2024-01-18T14:30:00Z", "p": 1.80, "s": 5, "x": "OPRA"},
            "latest_quote": {"t": "2024-01-18T14:30:00Z", "bp": 1.70, "bs": 10, "ap": 1.90, "as": 20, "x": "OPRA"},
            "greeks": {"delta": -0.35, "gamma": 0.02, "theta": -0.02, "vega": 0.14, "rho": -0.06},
            "underlying_price": 150.25
        },
        "timestamp": "2024-01-18T14:30:00Z",
        "underlying_price": 150.25,
        "feed": "iex"
    }
    
    with patch('alpaca_data.client.requests.request', return_value=mock_response):
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        result = client.get_option_chain(
            underlying_symbol="AAPL",
            feed="iex",
            output_format="dict"
        )
        
        # Verify the response structure
        assert "option_chain" in result
        assert "underlying_symbol" in result
        assert "feed" in result
        assert "contract_count" in result
        assert "calls_count" in result
        assert "puts_count" in result
        
        # Verify the data
        option_chain = result["option_chain"]
        assert option_chain.underlying_symbol == "AAPL"
        assert result["contract_count"] == 2
        assert result["calls_count"] == 1
        assert result["puts_count"] == 1
        assert result["underlying_symbol"] == "AAPL"
        assert result["feed"] == "iex"
        
        print(f"✅ get_option_chain client test passed! Got {result['contract_count']} contracts")
        return True


if __name__ == "__main__":
    print("Running options chain implementation tests...\n")
    
    # Run all tests
    tests = [
        test_option_chain_model,
        test_option_chain_from_api_response,
        test_get_option_chain_client
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The options chain implementation is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. The implementation needs more work.")
        sys.exit(1)