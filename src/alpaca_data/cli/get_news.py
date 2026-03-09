"""CLI script for getting news from Alpaca Market Data API."""

import typer
from typing import List, Optional
from .. import AlpacaClient

app = typer.Typer(
    name="alpaca-news",
    help="Get news articles from Alpaca Market Data API"
)


@app.command()
def news(
    symbols: Optional[List[str]] = typer.Argument(None, help="Stock symbols to get news for (e.g., AAPL GOOGL)"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start date/time in ISO format (e.g., 2024-01-01T09:30:00-05:00)"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End date/time in ISO format"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of news articles to return (max 50, default 50)"),
    include_content: bool = typer.Option(False, "--include-content", help="Include full content in response"),
    format: str = typer.Option("dict", "--format", "-f", help="Output format (dict, json, csv, dataframe)"),
    output_file: Optional[str] = typer.Option(None, "--output-file", "-o", help="Output file path for CSV format"),
    sort: str = typer.Option("desc", "--sort", help="Sort order (desc for newest first, asc for oldest first)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Get news articles for specified symbols and date range.
    
    Examples:
        alpaca-news AAPL
        alpaca-news AAPL GOOGL --start 2024-01-01 --limit 100
        alpaca-news --include-content --format json --output-file news.json
        alpaca-news --format csv --output-file news.csv
        alpaca-news --format dataframe
        alpaca-news --start 2024-01-01 --end 2024-01-31
    """
    try:
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting news for symbols: {symbols or 'All symbols'}")
            typer.echo(f"Format: {format}")
            typer.echo(f"Include content: {include_content}")
            
            if start:
                typer.echo(f"Start: {start}")
            if end:
                typer.echo(f"End: {end}")
        
        # Get news from API
        result = client.get_news(
            symbols=symbols,
            start=start,
            end=end,
            limit=limit,
            include_content=include_content,
            sort=sort,
            output_format=format.lower()
        )
        
        # Handle different output formats
        if format.lower() == "dict":
            # Print dictionary output in a readable format
            print_news_dict(result, verbose)
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


def print_news_dict(result: dict, verbose: bool = False):
    """Print news dictionary in a readable format."""
    if not verbose:
        # Simple summary
        typer.echo(f"📰 Got {result.get('count', 0)} news articles")
        
        symbols = result.get('symbols', [])
        if symbols:
            typer.echo(f"Symbols: {', '.join(symbols)}")
            
        if result.get('has_next_page'):
            typer.echo(f"⚠️  More articles available (pagination required)")
            
        # Show first few news articles if available
        news_articles = result.get('news', [])
        if news_articles and len(news_articles) > 0:
            typer.echo(f"\nLatest news:")
            for i, article in enumerate(news_articles[-5:] if len(news_articles) >= 5 else news_articles):
                # Handle both News objects and dictionaries
                if hasattr(article, 'symbols'):
                    # News object
                    symbols_str = ', '.join(article.symbols)
                    headline = article.headline
                    source = article.source
                    created_at = article.created_at
                    summary = article.summary if hasattr(article, 'summary') else None
                else:
                    # Dictionary format
                    symbols_str = ', '.join(article.get('symbols', [])) if article.get('symbols') else 'N/A'
                    headline = article.get('headline', 'No headline')
                    source = article.get('source', 'Unknown')
                    created_at = article.get('created_at', 'Unknown')
                    summary = article.get('summary')
                
                typer.echo(f"  {i+1}. {headline}")
                typer.echo(f"     Source: {source} | Symbols: {symbols_str} | Time: {created_at}")
                if summary:
                    summary_preview = summary[:100] + "..." if len(summary) > 100 else summary
                    typer.echo(f"     Summary: {summary_preview}")
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