"""
Options Data Examples for Alpaca Market Data SDK

This file demonstrates how to use the Alpaca SDK to access options data
including quotes, trades, snapshots, and Greeks calculations.
"""

import json
from alpaca_data import AlpacaClient

def main():
    """
    Demonstrates options market data patterns.
    """
    client = AlpacaClient()
    
    print("=== Options Market Data Examples ===")
    
    # Example 1: Get option quotes with greeks
    print("\n1. Option Quotes with Greeks")
    print("-" * 50)
    
    try:
        # Example option symbols (format: UNDERLYING + EXPIRATION + TYPE + STRIKE)
        # AAPL220121C00150000 = Apple Jan 21, 2022 Call $150
        option_symbols = [
            "AAPL230120C00150000",  # AAPL Call $150 Jan 20, 2023
            "AAPL230120P00150000",  # AAPL Put $150 Jan 20, 2023
        ]
        
        quotes = client.get_option_quotes(
            symbols=option_symbols,
            limit=10
        )
        
        print(f"Retrieved {len(quotes['quotes'])} option quotes")
        
        for quote in quotes['quotes']:
            option_type = "CALL" if "C" in quote.symbol else "PUT"
            print(f"  {quote.symbol} ({option_type}):")
            print(f"    Bid/Ask: ${quote.bid_price:.2f} x {quote.bid_size} / ${quote.ask_price:.2f} x {quote.ask_size}")
            
            if quote.greeks:
                print(f"    Greeks: Δ={quote.greeks.delta:.3f}, Γ={quote.greeks.gamma:.4f}")
                print(f"           Θ={quote.greeks.theta:.3f}, ν={quote.greeks.vega:.3f}, ρ={quote.greeks.rho:.3f}")
            
            if quote.iv:
                print(f"    Implied Vol: {quote.iv:.2%}")
            
            if quote.open_interest:
                print(f"    Open Interest: {quote.open_interest}")
    
    except Exception as e:
        print(f"Error getting option quotes: {e}")
    
    # Example 2: Get option trades with greeks
    print("\n2. Option Trades with Greeks")
    print("-" * 50)
    
    try:
        trades = client.get_option_trades(
            symbols=option_symbols,
            limit=5
        )
        
        print(f"Retrieved {len(trades['trades'])} option trades")
        
        for trade in trades['trades']:
            option_type = "CALL" if "C" in trade.symbol else "PUT"
            print(f"  {trade.symbol} ({option_type}): {trade.size} @ ${trade.price:.2f}")
            
            if trade.greeks:
                print(f"    Greeks at time of trade: Δ={trade.greeks.delta:.3f}, Γ={trade.greeks.gamma:.4f}")
            
            if trade.iv:
                print(f"    Implied Vol at trade: {trade.iv:.2%}")
    
    except Exception as e:
        print(f"Error getting option trades: {e}")
    
    # Example 3: Get option snapshots
    print("\n3. Option Snapshots")
    print("-" * 50)
    
    try:
        snapshots = client.get_option_snapshot(
            symbols=option_symbols
        )
        
        print(f"Retrieved {len(snapshots['snapshots'])} option snapshots")
        
        for snapshot in snapshots['snapshots']:
            option_type = "CALL" if "C" in snapshot.symbol else "PUT"
            print(f"  {snapshot.symbol} ({option_type}):")
            
            if snapshot.latest_trade:
                print(f"    Latest trade: ${snapshot.latest_trade.price:.2f} x {snapshot.latest_trade.size}")
            
            if snapshot.latest_quote:
                print(f"    Current quote: ${snapshot.latest_quote.bid_price:.2f} - ${snapshot.latest_quote.ask_price:.2f}")
            
            if snapshot.greeks:
                print(f"    Current Greeks:")
                print(f"      Delta (Δ): {snapshot.greeks.delta:.3f}")
                print(f"      Gamma (Γ): {snapshot.greeks.gamma:.6f}")
                print(f"      Theta (Θ): {snapshot.greeks.theta:.3f}")
                print(f"      Vega (ν):  {snapshot.greeks.vega:.3f}")
                print(f"      Rho (ρ):   {snapshot.greeks.rho:.3f}")
            
            if snapshot.iv:
                print(f"    Implied Volatility: {snapshot.iv:.2%}")
            
            if snapshot.open_interest:
                print(f"    Open Interest: {snapshot.open_interest}")
    
    except Exception as e:
        print(f"Error getting option snapshots: {e}")

def greeks_analysis_example():
    """
    Example of analyzing Greeks for risk management.
    """
    client = AlpacaClient()
    
    print("\n=== Greeks Analysis Example ===")
    
    # Get multiple option strikes for volatility surface analysis
    option_symbols = [
        "AAPL230120C00145000",  # ITM Call
        "AAPL230120C00150000",  # ATM Call
        "AAPL230120C00155000",  # OTM Call
        "AAPL230120P00145000",  # ITM Put
        "AAPL230120P00150000",  # ATM Put
        "AAPL230120P00155000",  # OTM Put
    ]
    
    try:
        snapshots = client.get_option_snapshot(symbols=option_symbols)
        
        print("Greeks Analysis for Risk Management:")
        print("-" * 60)
        
        calls = [s for s in snapshots['snapshots'] if "C" in s.symbol]
        puts = [s for s in snapshots['snapshots'] if "P" in s.symbol]
        
        print("\nCALL OPTIONS:")
        print(f"{'Symbol':<25} {'Delta':<8} {'Gamma':<10} {'Theta':<10} {'Vega':<8}")
        print("-" * 65)
        
        for call in calls:
            if call.greeks:
                print(f"{call.symbol:<25} {call.greeks.delta:<8.3f} {call.greeks.gamma:<10.6f} "
                      f"{call.greeks.theta:<10.3f} {call.greeks.vega:<8.3f}")
        
        print("\nPUT OPTIONS:")
        print(f"{'Symbol':<25} {'Delta':<8} {'Gamma':<10} {'Theta':<10} {'Vega':<8}")
        print("-" * 65)
        
        for put in puts:
            if put.greeks:
                print(f"{put.symbol:<25} {put.greeks.delta:<8.3f} {put.greeks.gamma:<10.6f} "
                      f"{put.greeks.theta:<10.3f} {put.greeks.vega:<8.3f}")
        
        # Calculate net position Greeks (example portfolio)
        print("\nPortfolio Greeks (example long 1x AAPL230120C00150000):")
        if calls:
            atm_call = next((c for c in calls if "C00150000" in c.symbol), None)
            if atm_call and atm_call.greeks:
                print(f"  Delta: {atm_call.greeks.delta:.3f}")
                print(f"  Gamma: {atm_call.greeks.gamma:.6f}")
                print(f"  Theta: {atm_call.greeks.theta:.3f}")
                print(f"  Vega:  {atm_call.greeks.vega:.3f}")
    
    except Exception as e:
        print(f"Error in Greeks analysis: {e}")

def option_chain_example():
    """
    Example of building an option chain for a given underlying.
    """
    client = AlpacaClient()
    
    print("\n=== Option Chain Example ===")
    
    # Note: In practice, you'd get the actual expiration dates and strikes
    # For this example, we'll use a few sample option symbols
    underlying = "AAPL"
    expiration = "230120"  # Jan 20, 2023
    strikes = [145, 150, 155]
    
    option_symbols = []
    for strike in strikes:
        call_symbol = f"{underlying}{expiration}C{str(strike).zfill(5)}000"
        put_symbol = f"{underlying}{expiration}P{str(strike).zfill(5)}000"
        option_symbols.extend([call_symbol, put_symbol])
    
    try:
        quotes = client.get_option_quotes(symbols=option_symbols, limit=len(option_symbols))
        
        print(f"Option Chain for {underlying} (Expiration: {expiration[:2]}/{expiration[2:4]}/20{expiration[4:6]})")
        print("-" * 80)
        print(f"{'Strike':<8} {'Call Bid':<8} {'Call Ask':<8} {'Call IV':<8} {'Put Bid':<8} {'Put Ask':<8} {'Put IV':<8}")
        print("-" * 80)
        
        for strike in strikes:
            call_symbol = f"{underlying}{expiration}C{str(strike).zfill(5)}000"
            put_symbol = f"{underlying}{expiration}P{str(strike).zfill(5)}000"
            
            call_quote = next((q for q in quotes['quotes'] if q.symbol == call_symbol), None)
            put_quote = next((q for q in quotes['quotes'] if q.symbol == put_symbol), None)
            
            call_bid = f"${call_quote.bid_price:.2f}" if call_quote else "N/A"
            call_ask = f"${call_quote.ask_price:.2f}" if call_quote else "N/A"
            call_iv = f"{call_quote.iv:.2%}" if call_quote and call_quote.iv else "N/A"
            put_bid = f"${put_quote.bid_price:.2f}" if put_quote else "N/A"
            put_ask = f"${put_quote.ask_price:.2f}" if put_quote else "N/A"
            put_iv = f"{put_quote.iv:.2%}" if put_quote and put_quote.iv else "N/A"
            
            print(f"{strike:<8} {call_bid:<8} {call_ask:<8} {call_iv:<8} {put_bid:<8} {put_ask:<8} {put_iv:<8}")
    
    except Exception as e:
        print(f"Error building option chain: {e}")

if __name__ == "__main__":
    main()
    greeks_analysis_example()
    option_chain_example()