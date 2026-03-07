#!/usr/bin/env python3
"""
Get Option Trades CLI

Fetch latest and historical trades for options symbols including greeks data.
"""

import sys
import typer
from typing import List, Optional
from datetime import datetime
from alpaca_data import AlpacaClient

app = typer.Typer(help="Get option trades from Alpaca Market Data API")

def format_output(data, output_format: str = "table"):
    """Format the trades data for output."""
    if output_format == "json":
        import json
        print(json.dumps(data, indent=2, default=str))
        return
    
    if output_format == "csv":
        import csv
        import io
        
        if not data.get('trades'):
            print("No trades found")
            return
            
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Symbol', 'Timestamp', 'Price', 'Size', 'Exchange', 'Implied Vol',
            'Delta', 'Gamma', 'Theta', 'Vega', 'Rho'
        ])
        
        # Write data
        for trade in data['trades']:
            greeks = trade.greeks if trade.greeks else None
            writer.writerow([
                trade.symbol,
                trade.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                f"{trade.price:.4f}",
                f"{trade.size}",
                trade.exchange,
                f"{trade.iv:.4f}" if trade.iv else "",
                f"{greeks.delta:.4f}" if greeks else "",
                f"{greeks.gamma:.6f}" if greeks else "",
                f"{greeks.theta:.4f}" if greeks else "",
                f"{greeks.vega:.4f}" if greeks else "",
                f"{greeks.rho:.4f}" if greeks else "",
            ])
        
        print(output.getvalue())
        output.close()
        return
    
    # Table format (default)
    if not data.get('trades'):
        print("No trades found")
        return
    
    print(f"📈 Found {len(data['trades'])} option trades for {data['symbol']}")
    print("-" * 100)
    print(f"{'Symbol':<25} {'Trade':<20} {'Size':<8} {'Exchange':<8} {'IV':<8} {'Delta':<8}")
    print("-" * 100)
    
    for trade in data['trades']:
        greeks = trade.greeks if trade.greeks else None
        iv_str = f"{trade.iv:.3f}" if trade.iv else "N/A"
        delta_str = f"{greeks.delta:.3f}" if greeks else "N/A"
        
        print(f"{trade.symbol:<25} ${trade.price:<8.4f} x {trade.size:<8.0f} "
              f"{trade.exchange:<6} {iv_str:<8} {delta_str:<8}")

@app.command()
def main(
    symbols: List[str] = typer.Argument(..., help="Option symbols to query (e.g., AAPL220121C00150000)"),
    start: Optional[str] = typer.Option(None, "--start", help="Start date (YYYY-MM-DD or ISO format)"),
    end: Optional[str] = typer.Option(None, "--end", help="End date (YYYY-MM-DD or ISO format)"),
    limit: int = typer.Option(100, "--limit", min=1, max=1000, help="Maximum number of trades"),
    sort: str = typer.Option("asc", "--sort", help="Sort order: asc or desc"),
    output_format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information"),
):
    """Fetch option trades with greeks data from Alpaca Market Data API.
    
    Examples:
        alpaca-option-trades AAPL220121C00150000
        alpaca-option-trades AAPL220121C00150000 AAPL220121P00150000 --start 2024-01-01 --limit 50
        alpaca-option-trades AAPL220121C00150000 --format json
        alpaca-option-trades AAPL220121C00150000 --format csv --output-file trades.csv
    """
    try:
        # Initialize client
        client = AlpacaClient()
        
        # Get trades
        result = client.get_option_trades(
            symbols=symbols,
            start=start,
            end=end,
            limit=limit,
            sort=sort,
            output_format="dict"
        )
        
        # Format and display results
        format_output(result, output_format)
        
        if verbose:
            print(f"\nMetadata:")
            print(f"  Total trades: {result['count']}")
            print(f"  Has next page: {result.get('has_next_page', False)}")
            if result.get('next_page_token'):
                print(f"  Next page token: {result['next_page_token']}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    app()