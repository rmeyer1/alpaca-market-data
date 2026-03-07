#!/usr/bin/env python3
"""
Get Option Snapshots CLI

Fetch latest market data snapshots for options symbols including greeks and implied volatility.
"""

import sys
import typer
from typing import List, Optional
from datetime import datetime
from alpaca_data import AlpacaClient

app = typer.Typer(help="Get option snapshots from Alpaca Market Data API")

def format_output(data, output_format: str = "table"):
    """Format the snapshots data for output."""
    if output_format == "json":
        import json
        print(json.dumps(data, indent=2, default=str))
        return
    
    if output_format == "csv":
        import csv
        import io
        
        if not data.get('snapshots'):
            print("No snapshots found")
            return
            
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Symbol', 'Type', 'Strike', 'Expiration', 'Trade Price', 'Trade Size',
            'Bid Price', 'Bid Size', 'Ask Price', 'Ask Size',
            'Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'Implied Vol', 'Open Interest'
        ])
        
        # Write data
        for snapshot in data['snapshots']:
            # Parse option symbol for additional info
            symbol = snapshot.symbol
            option_type = "CALL" if "C" in symbol else "PUT"
            
            # Extract strike price and expiration (basic parsing)
            try:
                if len(symbol) >= 21:  # Standard option symbol length
                    underlying = symbol[:4] if not symbol.startswith("VIX") else symbol[:6]
                    if symbol.startswith("VIX"):
                        expiration = symbol[6:12]
                        strike = symbol[12:]
                    else:
                        expiration = symbol[4:10]
                        strike = symbol[10:-1] if symbol[-1] in "CP" else symbol[10:]
            except:
                underlying = "Unknown"
                expiration = "Unknown"
                strike = "Unknown"
            
            # Get trade and quote data
            trade_price = f"{snapshot.latest_trade.price:.4f}" if snapshot.latest_trade else ""
            trade_size = str(snapshot.latest_trade.size) if snapshot.latest_trade else ""
            bid_price = f"{snapshot.latest_quote.bid_price:.4f}" if snapshot.latest_quote else ""
            bid_size = str(snapshot.latest_quote.bid_size) if snapshot.latest_quote else ""
            ask_price = f"{snapshot.latest_quote.ask_price:.4f}" if snapshot.latest_quote else ""
            ask_size = str(snapshot.latest_quote.ask_size) if snapshot.latest_quote else ""
            
            greeks = snapshot.greeks
            writer.writerow([
                symbol,
                option_type,
                strike,
                expiration,
                trade_price,
                trade_size,
                bid_price,
                bid_size,
                ask_price,
                ask_size,
                f"{greeks.delta:.4f}" if greeks else "",
                f"{greeks.gamma:.6f}" if greeks else "",
                f"{greeks.theta:.4f}" if greeks else "",
                f"{greeks.vega:.4f}" if greeks else "",
                f"{greeks.rho:.4f}" if greeks else "",
                f"{snapshot.iv:.4f}" if snapshot.iv else "",
                str(snapshot.open_interest) if snapshot.open_interest else "",
            ])
        
        print(output.getvalue())
        output.close()
        return
    
    # Table format (default)
    if not data.get('snapshots'):
        print("No snapshots found")
        return
    
    print(f"📈 Found {len(data['snapshots'])} option snapshots for {data['symbol']}")
    print("-" * 130)
    print(f"{'Symbol':<25} {'Type':<6} {'Strike':<8} {'Price Range':<20} {'IV':<10} {'Delta':<8} {'Open Interest':<12}")
    print("-" * 130)
    
    for snapshot in data['snapshots']:
        symbol = snapshot.symbol
        option_type = "CALL" if "C" in symbol else "PUT"
        
        # Extract strike price (basic parsing)
        try:
            if len(symbol) >= 21:  # Standard option symbol length
                if symbol.startswith("VIX"):
                    strike = symbol[12:]
                else:
                    strike = symbol[10:-1] if symbol[-1] in "CP" else symbol[10:]
        except:
            strike = "Unknown"
        
        # Get price range
        if snapshot.latest_quote:
            price_range = f"${snapshot.latest_quote.bid_price:.2f}-{snapshot.latest_quote.ask_price:.2f}"
        elif snapshot.latest_trade:
            price_range = f"${snapshot.latest_trade.price:.2f}"
        else:
            price_range = "No data"
        
        greeks = snapshot.greeks
        iv_str = f"{snapshot.iv:.3f}" if snapshot.iv else "N/A"
        delta_str = f"{greeks.delta:.3f}" if greeks else "N/A"
        oi_str = str(snapshot.open_interest) if snapshot.open_interest else "N/A"
        
        print(f"{symbol:<25} {option_type:<6} {strike:<8} {price_range:<20} {iv_str:<10} {delta_str:<8} {oi_str:<12}")

@app.command()
def main(
    symbols: List[str] = typer.Argument(..., help="Option symbols to query (e.g., AAPL220121C00150000)"),
    output_format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information"),
):
    """Fetch option snapshots with greeks, implied volatility, and open interest.
    
    Examples:
        alpaca-option-snapshot AAPL220121C00150000
        alpaca-option-snapshot AAPL220121C00150000 AAPL220121P00150000
        alpaca-option-snapshot AAPL220121C00150000 --format json
        alpaca-option-snapshot AAPL220121C00150000 --format csv --output-file snapshots.csv
    """
    try:
        # Initialize client
        client = AlpacaClient()
        
        # Get snapshots
        result = client.get_option_snapshot(
            symbols=symbols,
            output_format="dict"
        )
        
        # Format and display results
        format_output(result, output_format)
        
        if verbose:
            print(f"\nMetadata:")
            print(f"  Total snapshots: {result['count']}")
            for snapshot in result['snapshots']:
                print(f"  {snapshot.symbol}:")
                if snapshot.latest_trade:
                    print(f"    Latest trade: ${snapshot.latest_trade.price} x {snapshot.latest_trade.size}")
                if snapshot.greeks:
                    print(f"    Greeks: Δ={snapshot.greeks.delta:.3f}, Γ={snapshot.greeks.gamma:.4f}, Θ={snapshot.greeks.theta:.3f}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    app()