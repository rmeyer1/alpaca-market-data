"""CLI script for getting quotes from Alpaca Market Data API."""

import typer
from typing import List, Optional

app = typer.Typer(
    name="alpaca-quotes",
    help="Get NBBO quotes for stocks from Alpaca Market Data API"
)


@app.command()
def quotes(
    symbols: List[str] = typer.Argument(..., help="Stock symbols to get quotes for (e.g., AAPL GOOGL)"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date/time in ISO format (e.g., 2024-01-01T09:30:00-05:00)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date/time in ISO format"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of quotes to return (max 1000, default 1000)"),
    format: str = typer.Option("dict", "--format", "-f", help="Output format (dict, json, csv, dataframe)"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-o", help="Output file path for CSV format"),
    feed: str = typer.Option("iex", "--feed", help="Data feed (iex for free tier, sip for premium)"),
    sort: str = typer.Option("asc", "--sort", help="Sort order (asc for ascending, desc for descending)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Get NBBO quotes for one or more stock symbols.
    
    Examples:
        alpaca-quotes AAPL
        alpaca-quotes AAPL GOOGL --start 2024-01-01
        alpaca-quotes AAPL --format json --output-file quotes.json
        alpaca-quotes AAPL --format csv --output-file quotes.csv
        alpaca-quotes AAPL --format dataframe
    """
    try:
        # Import here to allow for proper mocking in tests
        from src.alpaca_data import AlpacaClient
        from src.alpaca_data.formatters import format_output
        
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting quotes for symbols: {symbols}")
            typer.echo(f"Format: {format}")
            typer.echo(f"Feed: {feed}")
            
            if start:
                typer.echo(f"Start: {start}")
            if end:
                typer.echo(f"End: {end}")
        
        # Get quotes from API
        result = client.get_quotes(
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
            print_quotes_dict(result, verbose)
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


def print_quotes_dict(result: dict, verbose: bool = False):
    """Print quotes dictionary in a readable format."""
    if not verbose:
        # Simple summary
        typer.echo(f"📊 Got {result.get('count', 0)} quotes for {result.get('symbol', 'unknown')}")
        typer.echo(f"Feed: {result.get('feed', 'unknown')}")
        
        if result.get('has_next_page'):
            typer.echo(f"⚠️  More data available (pagination required)")
            
        # Show first few quotes if available
        quotes = result.get('quotes', [])
        if quotes and len(quotes) > 0:
            typer.echo(f"\nLatest quotes:")
            for i, quote in enumerate(quotes[-3:] if len(quotes) >= 3 else quotes):
                # Handle both Quote objects and dictionaries
                if hasattr(quote, 'symbol'):
                    # Quote object
                    typer.echo(f"  {i+1}. {quote.symbol} | {quote.timestamp} | Bid:{quote.bid_price}@{quote.bid_size} Ask:{quote.ask_price}@{quote.ask_size}")
                else:
                    # Dictionary format
                    typer.echo(f"  {i+1}. {quote.get('symbol', 'unknown')} | {quote.get('timestamp', 'unknown')} | Bid:{quote.get('bid_price', 'N/A')}@{quote.get('bid_size', 'N/A')} Ask:{quote.get('ask_price', 'N/A')}@{quote.get('ask_size', 'N/A')}")
        
    else:
        # Verbose output - show all data
        import json
        typer.echo(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    app()