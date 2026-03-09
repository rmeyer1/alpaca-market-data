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

app = typer.Typer(help="Fetch option snapshots with greeks, implied volatility, and open interest.")


def format_output(data, output_format: str = "table", verbose: bool = False):
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
            if hasattr(snapshot, 'symbol'):
                # Snapshot object
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
            else:
                # Dictionary format
                snapshot_dict = snapshot
                symbol = snapshot_dict.get('symbol', '')
                option_type = "CALL" if "C" in symbol else "PUT"
                underlying = "Unknown"
                expiration = "Unknown"
                strike = "Unknown"
                
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
                    pass  # Keep default values
                
                # Get trade and quote data
                latest_trade = snapshot_dict.get('latest_trade') or {}
                latest_quote = snapshot_dict.get('latest_quote') or {}
                
                trade_price = f"{latest_trade.get('price', 0):.4f}" if latest_trade.get('price') else ""
                trade_size = str(latest_trade.get('size', '')) if latest_trade.get('size') else ""
                bid_price = f"{latest_quote.get('bid_price', 0):.4f}" if latest_quote.get('bid_price') else ""
                bid_size = str(latest_quote.get('bid_size', '')) if latest_quote.get('bid_size') else ""
                ask_price = f"{latest_quote.get('ask_price', 0):.4f}" if latest_quote.get('ask_price') else ""
                ask_size = str(latest_quote.get('ask_size', '')) if latest_quote.get('ask_size') else ""
                
                greeks = snapshot_dict.get('greeks') or {}
                iv_val = snapshot_dict.get('iv')
                oi_val = snapshot_dict.get('open_interest')
                
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
                    f"{greeks.get('delta', 0):.4f}" if greeks else "",
                    f"{greeks.get('gamma', 0):.6f}" if greeks else "",
                    f"{greeks.get('theta', 0):.4f}" if greeks else "",
                    f"{greeks.get('vega', 0):.4f}" if greeks else "",
                    f"{greeks.get('rho', 0):.4f}" if greeks else "",
                    f"{iv_val:.4f}" if iv_val else "",
                    str(oi_val) if oi_val else "",
                ])
        
        print(output.getvalue())
        output.close()
        return
    
    # Table format (default)
    if not data.get('snapshots'):
        print("No snapshots found")
        return
    
    print(f"📈 Found {len(data['snapshots'])} option snapshots for {data['symbol']}")
    print("-" * 100)
    print(f"{'Symbol':<25} {'Type':<4} {'Strike':<8} {'Price':<12} {'IV':<8} {'Delta':<8} {'OI':<8}")
    print("-" * 100)
    
    for snapshot in data['snapshots']:
        # Handle both Snapshot objects and dictionaries
        if hasattr(snapshot, 'symbol'):
            # Snapshot object
            symbol = snapshot.symbol
            option_type = "CALL" if "C" in symbol else "PUT"
            
            # Extract strike price (basic parsing)
            try:
                if len(symbol) >= 21:
                    strike = symbol[10:-1] if symbol[-1] in "CP" else symbol[10:]
                else:
                    strike = "N/A"
            except:
                strike = "N/A"
            
            # Get latest price
            if snapshot.latest_trade:
                price_str = f"${snapshot.latest_trade.price:.4f}"
            elif snapshot.latest_quote:
                price_str = f"${snapshot.latest_quote.bid_price:.4f}"
            else:
                price_str = "N/A"
            
            iv_str = f"{snapshot.iv:.3f}" if snapshot.iv else "N/A"
            delta_str = f"{snapshot.greeks.delta:.3f}" if snapshot.greeks else "N/A"
            oi_str = str(snapshot.open_interest) if snapshot.open_interest else "N/A"
            
            typer.echo(f"{symbol:<25} {option_type:<4} {strike:<8} {price_str:<12} {iv_str:<8} {delta_str:<8} {oi_str:<8}")
        else:
            # Dictionary format
            snapshot_dict = snapshot
            symbol = snapshot_dict.get('symbol', 'N/A')
            option_type = "CALL" if "C" in symbol else "PUT"
            strike = "N/A"
            
            # Extract strike price (basic parsing)
            try:
                if len(symbol) >= 21:
                    strike = symbol[10:-1] if symbol[-1] in "CP" else symbol[10:]
            except:
                pass  # Keep default value
            
            # Get latest price
            latest_trade = snapshot_dict.get('latest_trade') or {}
            latest_quote = snapshot_dict.get('latest_quote') or {}
            
            if latest_trade.get('price'):
                price_str = f"${latest_trade.get('price', 0):.4f}"
            elif latest_quote.get('bid_price'):
                price_str = f"${latest_quote.get('bid_price', 0):.4f}"
            else:
                price_str = "N/A"
            
            iv_val = snapshot_dict.get('iv')
            delta_val = snapshot_dict.get('greeks', {}).get('delta', 0) if snapshot_dict.get('greeks') else 0
            oi_val = snapshot_dict.get('open_interest', 0)
            
            iv_str = f"{iv_val:.3f}" if iv_val else "N/A"
            delta_str = f"{delta_val:.3f}" if delta_val != 0 else "N/A"
            oi_str = str(oi_val) if oi_val else "N/A"
            
            typer.echo(f"{symbol:<25} {option_type:<4} {strike:<8} {price_str:<12} {iv_str:<8} {delta_str:<8} {oi_str:<8}")

    if verbose:
        # Show additional metadata for verbose output
        if 'count' in data:
            typer.echo(f"\nMetadata:")
            typer.echo(f"Total snapshots: {data['count']}")
            typer.echo(f"Symbol(s): {data.get('symbol', 'N/A')}")


@app.command()
def main(
    symbols: List[str] = typer.Argument(..., help="Option symbols to query (e.g., AAPL220121C00150000)"),
    format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information")
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
        
        if verbose:
            typer.echo(f"Getting option snapshots for symbols: {symbols}")
            typer.echo(f"Format: {format}")
        
        # Make API call
        result = client.get_option_snapshot(
            symbols=symbols,
            output_format="dict"
        )
        
        # Format and display results
        format_output(result, format, verbose)
        
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


def main():
    """Main entry point for CLI commands."""
    app()


if __name__ == "__main__":
    import os
    # Check for API credentials
    if not os.getenv("ALPACA_API_KEY") or not os.getenv("ALPACA_API_SECRET"):
        print("❌ Error: API credentials required. Provide api_key and secret_key or set ALPACA_API_KEY and ALPACA_API_SECRET environment variables.")
        raise typer.Exit(1)
    
    app()