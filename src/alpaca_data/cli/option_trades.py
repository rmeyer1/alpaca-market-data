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

app = typer.Typer(help="Fetch option trades with greeks data from Alpaca Market Data API.")


def format_output(data, output_format: str = "table", verbose: bool = False):
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
            # Handle both Trade objects and dictionaries
            if hasattr(trade, 'symbol'):
                # Trade object
                greeks = trade.greeks if trade.greeks else None
                timestamp_str = trade.timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(trade.timestamp, 'strftime') else str(trade.timestamp)
                iv_str = f"{trade.iv:.4f}" if trade.iv else ""
                delta_str = f"{greeks.delta:.4f}" if greeks else ""
                gamma_str = f"{greeks.gamma:.6f}" if greeks else ""
                theta_str = f"{greeks.theta:.4f}" if greeks else ""
                vega_str = f"{greeks.vega:.4f}" if greeks else ""
                rho_str = f"{greeks.rho:.4f}" if greeks else ""
                
                writer.writerow([
                    trade.symbol,
                    timestamp_str,
                    f"{trade.price:.4f}",
                    f"{trade.size}",
                    trade.exchange,
                    iv_str,
                    delta_str,
                    gamma_str,
                    theta_str,
                    vega_str,
                    rho_str,
                ])
            else:
                # Dictionary format
                greeks = trade.get('greeks') or {}
                writer.writerow([
                    trade.get('symbol', ''),
                    trade.get('timestamp', ''),
                    f"{trade.get('price', 0):.4f}",
                    f"{trade.get('size', 0)}",
                    trade.get('exchange', ''),
                    f"{trade.get('iv', 0):.4f}" if trade.get('iv') else "",
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
    if not data.get('trades'):
        print("No trades found")
        return
    
    print(f"📈 Found {len(data['trades'])} option trades for {data['symbol']}")
    print("-" * 100)
    print(f"{'Symbol':<25} {'Trade':<20} {'Size':<8} {'Exchange':<8} {'IV':<8} {'Delta':<8}")
    print("-" * 100)
    
    for trade in data['trades']:
        # Handle both Trade objects and dictionaries
        if hasattr(trade, 'symbol'):
            # Trade object
            greeks = trade.greeks if trade.greeks else None
            iv_str = f"{trade.iv:.3f}" if trade.iv else "N/A"
            delta_str = f"{greeks.delta:.3f}" if greeks else "N/A"
            price_str = f"${trade.price:.4f}"
            size_str = f"{trade.size}"
            exchange_str = trade.exchange or "N/A"
            
            typer.echo(f"{trade.symbol:<25} {price_str:<20} {size_str:<8} {exchange_str:<8} {iv_str:<8} {delta_str:<8}")
        else:
            # Dictionary format
            greeks = trade.get('greeks') or {}
            iv_str = f"{trade.get('iv', 0):.3f}" if trade.get('iv') else "N/A"
            delta_str = f"{greeks.get('delta', 0):.3f}" if greeks else "N/A"
            price_str = f"${trade.get('price', 0):.4f}"
            size_str = f"{trade.get('size', 'N/A')}"
            exchange_str = trade.get('exchange', 'N/A')
            
            typer.echo(f"{trade.get('symbol', 'N/A'):<25} {price_str:<20} {size_str:<8} {exchange_str:<8} {iv_str:<8} {delta_str:<8}")

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
    limit: int = typer.Option(100, "--limit", min=1, max=1000, help="Maximum number of trades"),
    sort: str = typer.Option("asc", "--sort", help="Sort order: asc or desc"),
    format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information")
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
        
        if verbose:
            typer.echo(f"Getting option trades for symbols: {symbols}")
            typer.echo(f"Format: {format}")
            typer.echo(f"Limit: {limit}")
            typer.echo(f"Sort: {sort}")
            
            if start:
                typer.echo(f"Start: {start}")
            if end:
                typer.echo(f"End: {end}")
        
        # Make API call
        result = client.get_option_trades(
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