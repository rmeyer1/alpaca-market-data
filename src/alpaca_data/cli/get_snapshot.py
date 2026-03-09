"""CLI script for getting market snapshots from Alpaca Market Data API."""

import typer
from typing import List, Optional
from .. import AlpacaClient
from ..formatters import format_output

app = typer.Typer(
    name="alpaca-snapshot",
    help="Get market snapshots for stocks from Alpaca Market Data API"
)


@app.command()
def snapshot(
    symbols: List[str] = typer.Argument(..., help="Stock symbols to get snapshots for (e.g., AAPL GOOGL)"),
    format: str = typer.Option("dict", "--format", "-f", help="Output format (dict, json, csv, dataframe)"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-o", help="Output file path for CSV format"),
    feed: str = typer.Option("iex", "--feed", help="Data feed (iex for free tier, sip for premium)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Get market snapshots for one or more stock symbols.
    
    Examples:
        alpaca-snapshot AAPL
        alpaca-snapshot AAPL GOOGL MSFT
        alpaca-snapshot AAPL --format json --output-file snapshot.json
        alpaca-snapshot AAPL --format csv --output-file snapshot.csv
        alpaca-snapshot AAPL --format dataframe
    """
    try:
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting snapshots for symbols: {symbols}")
            typer.echo(f"Format: {format}")
            typer.echo(f"Feed: {feed}")
        
        # Get snapshots from API
        result = client.get_snapshot(
            symbols=symbols,
            feed=feed,
            output_format=format.lower()
        )
        
        # Handle different output formats
        if format.lower() == "dict":
            # Print dictionary output in a readable format
            print_snapshot_dict(result, verbose)
        elif format.lower() == "json":
            # JSON is already formatted as string
            typer.echo(result)
        elif format.lower() == "csv":
            # CSV output
            if output_file:
                # If output file specified, write to file
                typer.echo(f"Writing CSV to {output_file}", err=True)
                import os
                os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
                with open(output_file, "w") as f:
                    f.write(result)
                typer.echo(f"✅ CSV written to {output_file}")
            else:
                # Print to stdout
                typer.echo(result)
        elif format.lower() == "dataframe":
            # DataFrame output
            import pandas as pd
            if isinstance(result, pd.DataFrame):
                typer.echo(result.to_string())
            else:
                typer.echo("❌ Error: DataFrame format requires pandas to be installed")
                raise typer.Exit(1)
        else:
            typer.echo(f"❌ Error: Unsupported format '{format}'. Supported formats: dict, json, csv, dataframe")
            raise typer.Exit(1)
            
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


def print_snapshot_dict(result: dict, verbose: bool = False):
    """Print snapshots dictionary in a readable format."""
    if not verbose:
        # Simple summary
        typer.echo(f"📊 Got {result.get('count', 0)} snapshots")
        typer.echo(f"Symbols: {', '.join(result.get('symbol', [])) if isinstance(result.get('symbol'), list) else result.get('symbol', 'unknown')}")
        
        # Show snapshots if available
        snapshots = result.get('snapshots', [])
        if snapshots and len(snapshots) > 0:
            typer.echo(f"\nMarket snapshots:")
            for i, snapshot in enumerate(snapshots):
                # Handle both Snapshot objects and dictionaries
                if hasattr(snapshot, 'symbol'):
                    # Snapshot object
                    symbol = snapshot.symbol
                    
                    # Show latest trade if available
                    if snapshot.latest_trade:
                        trade = snapshot.latest_trade
                        typer.echo(f"  {i+1}. {symbol} | Trade: ${trade.price} x {trade.size} @ {trade.timestamp}")
                    else:
                        typer.echo(f"  {i+1}. {symbol} | No recent trades")
                    
                    # Show latest quote if available
                    if snapshot.latest_quote:
                        quote = snapshot.latest_quote
                        typer.echo(f"     Quote: Bid ${quote.bid_price}@{quote.bid_size} | Ask ${quote.ask_price}@{quote.ask_size}")
                    
                    # Show daily bar if available
                    if snapshot.daily_bar:
                        bar = snapshot.daily_bar
                        typer.echo(f"     Daily: O:${bar.open} H:${bar.high} L:${bar.low} C:${bar.close} V:{bar.volume}")
                else:
                    # Dictionary format
                    symbol = snapshot.get('symbol', 'unknown')
                    
                    # Show latest trade if available
                    latest_trade = snapshot.get('latest_trade')
                    if latest_trade:
                        if hasattr(latest_trade, 'price'):
                            # Trade object
                            typer.echo(f"  {i+1}. {symbol} | Trade: ${latest_trade.price} x {latest_trade.size} @ {latest_trade.timestamp}")
                        else:
                            # Dictionary
                            typer.echo(f"  {i+1}. {symbol} | Trade: ${latest_trade.get('price', 'N/A')} x {latest_trade.get('size', 'N/A')} @ {latest_trade.get('timestamp', 'N/A')}")
                    else:
                        typer.echo(f"  {i+1}. {symbol} | No recent trades")
                    
                    # Show latest quote if available
                    latest_quote = snapshot.get('latest_quote')
                    if latest_quote:
                        if hasattr(latest_quote, 'bid_price'):
                            # Quote object
                            typer.echo(f"     Quote: Bid ${latest_quote.bid_price}@{latest_quote.bid_size} | Ask ${latest_quote.ask_price}@{latest_quote.ask_size}")
                        else:
                            # Dictionary
                            typer.echo(f"     Quote: Bid ${latest_quote.get('bid_price', 'N/A')}@{latest_quote.get('bid_size', 'N/A')} | Ask ${latest_quote.get('ask_price', 'N/A')}@{latest_quote.get('ask_size', 'N/A')}")
                    
                    # Show daily bar if available
                    daily_bar = snapshot.get('daily_bar')
                    if daily_bar:
                        if hasattr(daily_bar, 'open'):
                            # Bar object
                            typer.echo(f"     Daily: O:${daily_bar.open} H:${daily_bar.high} L:${daily_bar.low} C:${daily_bar.close} V:{daily_bar.volume}")
                        else:
                            # Dictionary
                            typer.echo(f"     Daily: O:${daily_bar.get('open', 'N/A')} H:${daily_bar.get('high', 'N/A')} L:${daily_bar.get('low', 'N/A')} C:${daily_bar.get('close', 'N/A')} V:{daily_bar.get('volume', 'N/A')}")
                typer.echo()
        
    else:
        # Verbose output - show all data
        import json
        typer.echo(json.dumps(result, indent=2, default=str))


def main():
    """Main entry point for CLI commands."""
    app()


if __name__ == "__main__":
    main()