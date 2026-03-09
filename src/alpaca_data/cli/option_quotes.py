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

app = typer.Typer(help="Fetch option quotes with greeks data from Alpaca Market Data API.")


def format_output(data, output_format: str = "table", verbose: bool = False):
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
            # Handle both Quote objects and dictionaries
            if hasattr(quote, 'symbol'):
                # Quote object
                greeks = quote.greeks if quote.greeks else None
                timestamp_str = quote.timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(quote.timestamp, 'strftime') else str(quote.timestamp)
                iv_str = f"{quote.iv:.4f}" if quote.iv else ""
                oi_str = str(quote.open_interest) if quote.open_interest else ""
                delta_str = f"{greeks.delta:.4f}" if greeks else ""
                gamma_str = f"{greeks.gamma:.6f}" if greeks else ""
                theta_str = f"{greeks.theta:.4f}" if greeks else ""
                vega_str = f"{greeks.vega:.4f}" if greeks else ""
                rho_str = f"{greeks.rho:.4f}" if greeks else ""
                
                writer.writerow([
                    quote.symbol,
                    timestamp_str,
                    f"{quote.bid_price:.4f}",
                    f"{quote.bid_size}",
                    f"{quote.ask_price:.4f}",
                    f"{quote.ask_size}",
                    quote.bid_exchange,
                    quote.ask_exchange,
                    iv_str,
                    oi_str,
                    delta_str,
                    gamma_str,
                    theta_str,
                    vega_str,
                    rho_str,
                ])
            else:
                # Dictionary format
                greeks = quote.get('greeks') or {}
                writer.writerow([
                    quote.get('symbol', ''),
                    quote.get('timestamp', ''),
                    f"{quote.get('bid_price', 0):.4f}",
                    f"{quote.get('bid_size', 0)}",
                    f"{quote.get('ask_price', 0):.4f}",
                    f"{quote.get('ask_size', 0)}",
                    quote.get('bid_exchange', ''),
                    quote.get('ask_exchange', ''),
                    f"{quote.get('iv', 0):.4f}" if quote.get('iv') else "",
                    str(quote.get('open_interest', '')) if quote.get('open_interest') else "",
                    f"{greeks.get('delta', 0):.4f}" if greeks else "",
                    f"{greeks.get('gamma', 0):.6f}" if greeks else "",
                    f"{greeks.get('theta', 0):.4f}" if greeks else "",
                    f"{greeks.get('vega', 0):.4f}" if greeks else "",
                    f"{greeks.get('rho', 0):.4f}" if greeks else "",
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
        # Handle both Quote objects and dictionaries
        if hasattr(quote, 'symbol'):
            # Quote object
            greeks = quote.greeks if quote.greeks else None
            iv_str = f"{quote.iv:.3f}" if quote.iv else "N/A"
            delta_str = f"{greeks.delta:.3f}" if greeks else "N/A"
            exchange = quote.bid_exchange or quote.ask_exchange or "N/A"
            
            # Calculate spread for display
            if hasattr(quote, 'bid_price') and hasattr(quote, 'ask_price'):
                spread = quote.ask_price - quote.bid_price
                price_str = f"${quote.bid_price:.2f}-${quote.ask_price:.2f} (${spread:.2f})"
            else:
                price_str = "N/A"
            
            typer.echo(f"{quote.symbol:<25} {price_str:<12} {quote.bid_size if hasattr(quote, 'bid_size') else 'N/A':<8} {exchange:<8} {iv_str:<8} {delta_str:<8}")
        else:
            # Dictionary format
            greeks = quote.get('greeks') or {}
            iv_str = f"{quote.get('iv', 0):.3f}" if quote.get('iv') else "N/A"
            delta_str = f"{greeks.get('delta', 0):.3f}" if greeks else "N/A"
            exchange = quote.get('bid_exchange') or quote.get('ask_exchange') or "N/A"
            
            # Calculate spread for display
            bid_price = quote.get('bid_price', 0)
            ask_price = quote.get('ask_price', 0)
            if bid_price and ask_price:
                spread = ask_price - bid_price
                price_str = f"${bid_price:.2f}-${ask_price:.2f} (${spread:.2f})"
            else:
                price_str = "N/A"
            
            typer.echo(f"{quote.get('symbol', 'N/A'):<25} {price_str:<12} {quote.get('bid_size', 'N/A'):<8} {exchange:<8} {iv_str:<8} {delta_str:<8}")

    if verbose:
        # Show additional metadata for verbose output
        if 'count' in data:
            typer.echo(f"\nMetadata:")
            typer.echo(f"Total count: {data['count']}")
            typer.echo(f"Symbol(s): {data.get('symbol', 'N/A')}")
            if 'has_next_page' in data:
                typer.echo(f"Has next page: {data['has_next_page']}")
            if 'next_page_token' in data:
                typer.echo(f"Next page token: {data['next_page_token']}")


@app.command()
def main(
    symbols: List[str] = typer.Argument(..., help="Option symbols to query (e.g., AAPL220121C00150000)"),
    start: Optional[str] = typer.Option(None, "--start", help="Start date (YYYY-MM-DD or ISO format)"),
    end: Optional[str] = typer.Option(None, "--end", help="End date (YYYY-MM-DD or ISO format)"),
    limit: int = typer.Option(100, "--limit", min=1, max=1000, help="Maximum number of quotes"),
    sort: str = typer.Option("asc", "--sort", help="Sort order: asc or desc"),
    format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information")
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
        
        if verbose:
            typer.echo(f"Getting option quotes for symbols: {symbols}")
            typer.echo(f"Format: {format}")
            typer.echo(f"Limit: {limit}")
            typer.echo(f"Sort: {sort}")
            
            if start:
                typer.echo(f"Start: {start}")
            if end:
                typer.echo(f"End: {end}")
        
        # Make API call
        result = client.get_option_quotes(
            symbols=symbols,
            start=start,
            end=end,
            limit=limit,
            sort=sort,
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