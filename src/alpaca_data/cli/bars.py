"""CLI script for getting historical OHLCV bars from Alpaca Market Data API."""

import typer
from typing import List, Optional

app = typer.Typer(
    name="alpaca-bars",
    help="Get historical OHLCV bars for stocks from Alpaca Market Data API"
)


@app.command()
def bars(
    symbols: List[str] = typer.Argument(..., help="Stock symbols to get bars for (e.g., AAPL GOOGL)"),
    timeframe: str = typer.Option("1Day", "--timeframe", "-t", help="Bar timeframe (1Min, 5Min, 15Min, 1Hour, 1Day, 1Week, 1Month)"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date/time in ISO format (e.g., 2024-01-01T09:30:00-05:00)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date/time in ISO format"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of bars to return (max 1000, default 1000)"),
    adjustment: str = typer.Option("all", "--adjustment", "-a", help="Split adjustment (all, raw, splits_only, dividends_only)"),
    sort: str = typer.Option("asc", "--sort", help="Sort order (asc for ascending, desc for descending)"),
    format: str = typer.Option("dict", "--format", "-f", help="Output format (dict, json, csv, dataframe)"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-o", help="Output file path for CSV format"),

    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Get historical OHLCV bars for one or more stock symbols.
    
    Examples:
        alpaca-bars AAPL
        alpaca-bars AAPL GOOGL --timeframe 1Hour --start 2024-01-01
        alpaca-bars AAPL --format json --output-file bars.json
        alpaca-bars AAPL --format csv --output-file bars.csv
        alpaca-bars AAPL --format dataframe
    """
    try:
        # Import here to allow for proper mocking in tests
        from alpaca_data import AlpacaClient
        from alpaca_data.formatters import format_output
        
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting bars for symbols: {symbols}")
            typer.echo(f"Timeframe: {timeframe}")
            typer.echo(f"Format: {format}")
            
            if start:
                typer.echo(f"Start: {start}")
            if end:
                typer.echo(f"End: {end}")
        
        # Get bars from API
        result = client.get_bars(
            symbols=symbols,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit,
            adjustment=adjustment,
            sort=sort,
            output_format=format.lower()
        )
        
        # Handle different output formats
        if format.lower() == "dict":
            # Print dictionary output in a readable format
            print_bars_dict(result, verbose)
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


def print_bars_dict(result: dict, verbose: bool = False):
    """Print bars dictionary in a readable format."""
    if not verbose:
        # Simple summary
        typer.echo(f"📊 Got {result.get('count', 0)} bars for {result.get('symbol', 'unknown')}")
        typer.echo(f"Timeframe: {result.get('timeframe', 'unknown')}")
        
        if result.get('has_next_page'):
            typer.echo(f"⚠️  More data available (pagination required)")
            
        # Show first few bars if available
        bars = result.get('bars', [])
        if bars and len(bars) > 0:
            typer.echo(f"\nLatest bars:")
            for i, bar in enumerate(bars[-3:] if len(bars) >= 3 else bars):
                # Handle both Bar objects and dictionaries
                if hasattr(bar, 'symbol'):
                    # Bar object
                    typer.echo(f"  {i+1}. {bar.symbol} | {bar.timestamp} | O:{bar.open} H:{bar.high} L:{bar.low} C:{bar.close} V:{bar.volume}")
                else:
                    # Dictionary format
                    typer.echo(f"  {i+1}. {bar.get('symbol', 'unknown')} | {bar.get('timestamp', 'unknown')} | O:{bar.get('open', 'N/A')} H:{bar.get('high', 'N/A')} L:{bar.get('low', 'N/A')} C:{bar.get('close', 'N/A')} V:{bar.get('volume', 'N/A')}")
        
    else:
        # Verbose output - show all data
        import json
        typer.echo(json.dumps(result, indent=2, default=str))



def main():
    """Main entry point for CLI commands."""
    app()