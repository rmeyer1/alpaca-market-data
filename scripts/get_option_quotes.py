#!/usr/bin/env python3
"""
Get Option Quotes CLI

Fetch latest and historical quotes for options symbols including greeks data.
"""

import sys
import typer
from typing import List, Optional
from datetime import datetime
from alpaca_data import AlpacaClient

app = typer.Typer(help="Get option quotes from Alpaca Market Data API")

def format_output(data, output_format: str = "table"):
    """Format the quotes data for output."""
    if output_format == "json":
        import json
        print(json.dumps(data, indent=2, default=str))
        return
    
    if output_format == "csv":
        import csv
        import io
        
        if not data.get('quotes'):
            print("No quotes found")
            return
            
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Symbol', 'Timestamp', 'Bid Price', 'Bid Size', 'Ask Price', 'Ask Size',
            'Bid Exchange', 'Ask Exchange', 'Implied Vol', 'Open Interest',
            'Delta', 'Gamma', 'Theta', 'Vega', 'Rho'
        ])
        
        # Write data
        for quote in data['quotes']:
            greeks = quote.greeks if quote.greeks else None
            writer.writerow([
                quote.symbol,
                quote.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                f"{quote.bid_price:.4f}",
                f"{quote.bid_size}",
                f"{quote.ask_price:.4f}",
                f"{quote.ask_size}",
                quote.bid_exchange,
                quote.ask_exchange,
                f"{quote.iv:.4f}" if quote.iv else "",
                str(quote.open_interest) if quote.open_interest else "",
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
    if not data.get('quotes'):
        print("No quotes found")
        return
    
    print(f"📈 Found {len(data['quotes'])} option quotes for {data['symbol']}")
    print("-" * 120)
    print(f"{'Symbol':<25} {'Price':<12} {'Size':<8} {'Exchange':<8} {'IV':<8} {'Delta':<8}")
    print("-" * 120)
    
    for quote in data['quotes']:
        greeks = quote.greeks if quote.greeks else None
        iv_str = f"{quote.iv:.3f}" if quote.iv else "N/A"
        delta_str = f"{greeks.delta:.3f}" if greeks else "N/A"
        
        print(f"{quote.symbol:<25} ${quote.bid_price:<7.3f}-{quote.ask_price:<7.3f} "
              f"{quote.bid_size:<4.0f}-{quote.ask_size:<4.0f} {quote.bid_exchange:<6} "
              f"{iv_str:<8} {delta_str:<8}")

@app.command()
def main(
    symbols: List[str] = typer.Argument(..., help="Option symbols to query (e.g., AAPL220121C00150000)"),
    start: Optional[str] = typer.Option(None, "--start", help="Start date (YYYY-MM-DD or ISO format)"),
    end: Optional[str] = typer.Option(None, "--end", help="End date (YYYY-MM-DD or ISO format)"),
    limit: int = typer.Option(100, "--limit", min=1, max=1000, help="Maximum number of quotes"),
    sort: str = typer.Option("asc", "--sort", help="Sort order: asc or desc"),
    output_format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information"),
):
    """Fetch option quotes with greeks data from Alpaca Market Data API.
    
    Examples:
        alpaca-option-quotes AAPL220121C00150000
        alpaca-option-quotes AAPL220121C00150000 AAPL220121P00150000 --start 2024-01-01 --limit 50
        alpaca-option-quotes AAPL220121C00150000 --format json
        alpaca-option-quotes AAPL220121C00150000 --format csv --output-file quotes.csv
    """
    try:
        # Initialize client
        client = AlpacaClient()
        
        # Get quotes
        result = client.get_option_quotes(
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
            print(f"  Total quotes: {result['count']}")
            print(f"  Has next page: {result.get('has_next_page', False)}")
            if result.get('next_page_token'):
                print(f"  Next page token: {result['next_page_token']}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    app()