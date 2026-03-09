"""CLI script for getting crypto market data from Alpaca Market Data API."""

import typer
from typing import List, Optional

app = typer.Typer(
    name="alpaca-crypto",
    help="Get crypto market data (bars, quotes, snapshots) from Alpaca Market Data API"
)


@app.command()
def bars(
    symbols: List[str] = typer.Argument(..., help="Crypto symbols to get bars for (e.g., BTC/USD ETH/USD)"),
    timeframe: str = typer.Option("1Day", "--timeframe", "-t", help="Bar timeframe (1Min, 5Min, 15Min, 1Hour, 1Day, 1Week, 1Month)"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date/time in ISO format (e.g., 2024-01-01T09:30:00-05:00)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date/time in ISO format"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of bars to return (max 1000, default 1000)"),
    format: str = typer.Option("dict", "--format", "-f", help="Output format (dict, json, csv, dataframe)"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-o", help="Output file path for CSV format"),
    exchange: Optional[str] = typer.Option(None, "--exchange", help="Specific exchange filter (e.g., CBSE, FTX)"),
    sort: str = typer.Option("asc", "--sort", help="Sort order (asc for ascending, desc for descending)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Get historical OHLCV bars for crypto pairs.
    
    Examples:
        alpaca-crypto bars BTC/USD
        alpaca-crypto bars BTC/USD ETH/USD --timeframe 1Hour
        alpaca-crypto bars BTC/USD --format json --output-file crypto_bars.json
        alpaca-crypto bars BTC/USD --format csv --output-file crypto_bars.csv
    """
    try:
        # Import here to allow for proper mocking in tests
        from alpaca_data import AlpacaClient
        from alpaca_data.formatters import format_output
        
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting crypto bars for symbols: {symbols}")
            typer.echo(f"Timeframe: {timeframe}")
            typer.echo(f"Format: {format}")
            
            if exchange:
                typer.echo(f"Exchange filter: {exchange}")
            
            if start:
                typer.echo(f"Start: {start}")
            if end:
                typer.echo(f"End: {end}")
        
        # Get crypto bars from API
        result = client.get_crypto_bars(
            symbol_or_symbols=symbols,
            timeframe=timeframe,
            start=start,
            end=end,
            limit=limit,
            exchange=exchange,
            sort=sort,
            output_format=format.lower()
        )
        
        _handle_output_format(result, format.lower(), output_file, verbose, "crypto bars")
        
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def quotes(
    symbols: List[str] = typer.Argument(..., help="Crypto symbols to get quotes for (e.g., BTC/USD ETH/USD)"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date/time in ISO format (e.g., 2024-01-01T09:30:00-05:00)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date/time in ISO format"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of quotes to return (max 1000, default 1000)"),
    format: str = typer.Option("dict", "--format", "-f", help="Output format (dict, json, csv, dataframe)"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-o", help="Output file path for CSV format"),
    exchange: Optional[str] = typer.Option(None, "--exchange", help="Specific exchange filter (e.g., CBSE, FTX)"),
    sort: str = typer.Option("asc", "--sort", help="Sort order (asc for ascending, desc for descending)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Get quotes for crypto pairs.
    
    Examples:
        alpaca-crypto quotes BTC/USD
        alpaca-crypto quotes BTC/USD ETH/USD --start 2024-01-01
        alpaca-crypto quotes BTC/USD --format json --output-file crypto_quotes.json
        alpaca-crypto quotes BTC/USD --format csv --output-file crypto_quotes.csv
    """
    try:
        # Import here to allow for proper mocking in tests
        from alpaca_data import AlpacaClient
        from alpaca_data.formatters import format_output
        
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting crypto quotes for symbols: {symbols}")
            typer.echo(f"Format: {format}")
            
            if exchange:
                typer.echo(f"Exchange filter: {exchange}")
            
            if start:
                typer.echo(f"Start: {start}")
            if end:
                typer.echo(f"End: {end}")
        
        # Get crypto quotes from API
        result = client.get_crypto_quotes(
            symbol_or_symbols=symbols,
            start=start,
            end=end,
            limit=limit,
            exchange=exchange,
            sort=sort,
            output_format=format.lower()
        )
        
        _handle_output_format(result, format.lower(), output_file, verbose, "crypto quotes")
        
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def snapshot(
    symbols: List[str] = typer.Argument(..., help="Crypto symbols to get snapshots for (e.g., BTC/USD ETH/USD)"),
    format: str = typer.Option("dict", "--format", "-f", help="Output format (dict, json, csv, dataframe)"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-o", help="Output file path for CSV format"),
    exchange: Optional[str] = typer.Option(None, "--exchange", help="Specific exchange filter (e.g., CBSE, FTX)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Get market snapshots for crypto pairs.
    
    Examples:
        alpaca-crypto snapshot BTC/USD
        alpaca-crypto snapshot BTC/USD ETH/USD
        alpaca-crypto snapshot BTC/USD --format json --output-file crypto_snapshot.json
        alpaca-crypto snapshot BTC/USD --format csv --output-file crypto_snapshot.csv
    """
    try:
        # Import here to allow for proper mocking in tests
        from alpaca_data import AlpacaClient
        from alpaca_data.formatters import format_output
        
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting crypto snapshots for symbols: {symbols}")
            typer.echo(f"Format: {format}")
            
            if exchange:
                typer.echo(f"Exchange filter: {exchange}")
        
        # Get crypto snapshots from API
        result = client.get_crypto_snapshot(
            symbol_or_symbols=symbols,
            exchange=exchange,
            output_format=format.lower()
        )
        
        _handle_output_format(result, format.lower(), output_file, verbose, "crypto snapshots")
        
    except Exception as e:
        typer.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


def _handle_output_format(result, format_name: str, output_file: Optional[str], verbose: bool, data_type: str):
    """Handle different output formats consistently."""
    if format_name == "dict":
        # Print dictionary output in a readable format
        _print_crypto_dict(result, verbose, data_type)
    elif format_name == "json":
        # JSON is already formatted as string
        typer.echo(result)
    elif format_name == "csv":
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
    elif format_name == "dataframe":
        # DataFrame output
        import pandas as pd
        if isinstance(result, pd.DataFrame):
            typer.echo(result.to_string())
        else:
            typer.echo("❌ Error: DataFrame format requires pandas to be installed")
            raise typer.Exit(1)
    else:
        typer.echo(f"❌ Error: Unsupported format '{format_name}'. Supported formats: dict, json, csv, dataframe")
        raise typer.Exit(1)


def _print_crypto_dict(result: dict, verbose: bool = False, data_type: str = ""):
    """Print crypto data dictionary in a readable format."""
    if not verbose:
        # Simple summary
        typer.echo(f"💰 Got {result.get('count', 0)} {data_type}")
        
        if data_type == "crypto bars":
            timeframe = result.get('timeframe', 'unknown')
            typer.echo(f"Timeframe: {timeframe}")
        elif data_type == "crypto quotes":
            exchange = result.get('exchange', 'unknown')
            typer.echo(f"Exchange: {exchange}")
        elif data_type == "crypto snapshots":
            typer.echo(f"Symbols: {', '.join(result.get('symbol', [])) if isinstance(result.get('symbol'), list) else result.get('symbol', 'unknown')}")
        
        if result.get('has_next_page'):
            typer.echo(f"⚠️  More data available (pagination required)")
        
        # Show data based on type
        if data_type == "crypto bars":
            bars = result.get('bars', [])
            if bars and len(bars) > 0:
                typer.echo(f"\nLatest crypto bars:")
                for i, bar in enumerate(bars[-3:] if len(bars) >= 3 else bars):
                    # Handle both Bar objects and dictionaries
                    if hasattr(bar, 'symbol'):
                        # Bar object
                        typer.echo(f"  {i+1}. {bar.symbol} | {bar.timestamp} | O:${bar.open} H:${bar.high} L:${bar.low} C:${bar.close} V:{bar.volume}")
                    else:
                        # Dictionary format
                        typer.echo(f"  {i+1}. {bar.get('symbol', 'unknown')} | {bar.get('timestamp', 'unknown')} | O:${bar.get('open', 'N/A')} H:${bar.get('high', 'N/A')} L:${bar.get('low', 'N/A')} C:${bar.get('close', 'N/A')} V:{bar.get('volume', 'N/A')}")
                    
        elif data_type == "crypto quotes":
            quotes = result.get('quotes', [])
            if quotes and len(quotes) > 0:
                typer.echo(f"\nLatest crypto quotes:")
                for i, quote in enumerate(quotes[-3:] if len(quotes) >= 3 else quotes):
                    # Handle both Quote objects and dictionaries
                    if hasattr(quote, 'symbol'):
                        # Quote object
                        typer.echo(f"  {i+1}. {quote.symbol} | {quote.timestamp} | Bid:${quote.bid_price}@{quote.bid_size} Ask:${quote.ask_price}@{quote.ask_size}")
                    else:
                        # Dictionary format
                        typer.echo(f"  {i+1}. {quote.get('symbol', 'unknown')} | {quote.get('timestamp', 'unknown')} | Bid:${quote.get('bid_price', 'N/A')}@{quote.get('bid_size', 'N/A')} Ask:${quote.get('ask_price', 'N/A')}@{quote.get('ask_size', 'N/A')}")
                    
        elif data_type == "crypto snapshots":
            snapshots = result.get('snapshots', [])
            if snapshots and len(snapshots) > 0:
                typer.echo(f"\nCrypto market snapshots:")
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
                            typer.echo(f"     Daily: O:${daily_bar.get('open', 'N/A')} H:${daily_bar.get('high', 'N/A')} L:${daily_bar.get('low', 'N/A')} C:${daily_bar.get('close', 'N/A')} V:${daily_bar.get('volume', 'N/A')}")
                    typer.echo()
        
    else:
        # Verbose output - show all data
        import json
        typer.echo(json.dumps(result, indent=2, default=str))


def main():
    """Main entry point for CLI commands."""
    app()
