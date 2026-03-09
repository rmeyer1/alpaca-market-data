"""CLI script for getting trades from Alpaca Market Data API."""

import typer
from typing import List, Optional
from .. import AlpacaClient
from ..formatters import format_output

app = typer.Typer(
    name="alpaca-trades",
    help="Get trade data for stocks from Alpaca Market Data API"
)


@app.command()
def trades(
    symbols: List[str] = typer.Argument(..., help="Stock symbols to get trades for (e.g., AAPL GOOGL)"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date/time in ISO format (e.g., 2024-01-01T09:30:00-05:00)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date/time in ISO format"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of trades to return (max 1000, default 1000)"),
    format: str = typer.Option("dict", "--format", "-f", help="Output format (dict, json, csv, dataframe)"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-o", help="Output file path for CSV format"),
    feed: str = typer.Option("iex", "--feed", help="Data feed (iex for free tier, sip for premium)"),
    sort: str = typer.Option("asc", "--sort", help="Sort order (asc for ascending, desc for descending)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Get trade data for one or more stock symbols.
    
    Examples:
        alpaca-trades AAPL
        alpaca-trades AAPL GOOGL --start 2024-01-01
        alpaca-trades AAPL --format json --output-file trades.json
        alpaca-trades AAPL --format csv --output-file trades.csv
        alpaca-trades AAPL --format dataframe
    """
    try:
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting trades for symbols: {symbols}")
            typer.echo(f"Format: {format}")
            typer.echo(f"Feed: {feed}")
            
            if start:
                typer.echo(f"Start: {start}")
            if end:
                typer.echo(f"End: {end}")
        
        # Get trades from API
        result = client.get_trades(
            symbols=symbols,
            start=start,
            end=end,
            limit=limit,
            feed=feed,
            sort=sort,
            output_format=format.lower()
        )
        
        # Handle different output formats
        if format.lower() == "dict":
            # Print dictionary output in a readable format
            print_trades_dict(result, verbose)
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


def print_trades_dict(result: dict, verbose: bool = False):
    """Print trades dictionary in a readable format."""
    if not verbose:
        # Simple summary
        typer.echo(f"📊 Got {result.get('count', 0)} trades for {result.get('symbol', 'unknown')}")
        typer.echo(f"Feed: {result.get('feed', 'unknown')}")
        
        if result.get('has_next_page'):
            typer.echo(f"⚠️  More data available (pagination required)")
            
        # Show first few trades if available
        trades = result.get('trades', [])
        if trades and len(trades) > 0:
            typer.echo(f"\nLatest trades:")
            for i, trade in enumerate(trades[-5:] if len(trades) >= 5 else trades):
                # Handle both Trade objects and dictionaries
                if hasattr(trade, 'symbol'):
                    # Trade object
                    typer.echo(f"  {i+1}. {trade.symbol} | {trade.timestamp} | ${trade.price} x {trade.size} @ {trade.exchange}")
                else:
                    # Dictionary format
                    typer.echo(f"  {i+1}. {trade.get('symbol', 'unknown')} | {trade.get('timestamp', 'unknown')} | ${trade.get('price', 'N/A')} x {trade.get('size', 'N/A')} @ {trade.get('exchange', 'N/A')}")
        
    else:
        # Verbose output - show all data
        import json
        typer.echo(json.dumps(result, indent=2, default=str))


def main():
    """Main entry point for CLI commands."""
    app()


if __name__ == "__main__":
    main()