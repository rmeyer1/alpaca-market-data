#!/usr/bin/env python3
"""CLI script to fetch news."""

import argparse
import os
import sys

# Import SDK modules
try:
    from alpaca_data import AlpacaClient
    from alpaca_data.exceptions import (
        AlpacaAuthError,
        AlpacaNotFoundError,
        AlpacaRateLimitError,
        AlpacaAPIError,
    )
except ImportError as e:
    print(f"Error importing Alpaca SDK: {e}", file=sys.stderr)
    print("Make sure the package is installed: pip install -e .", file=sys.stderr)
    sys.exit(1)


def main():
    """Main entry point for get_news CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch news from Alpaca Market Data API"
    )
    parser.add_argument(
        "--symbols",
        nargs="*",
        help="Filter by symbols (optional)",
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date",
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of articles",
    )
    parser.add_argument(
        "--include-content",
        action="store_true",
        help="Include full article content",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="Output format",
    )
    parser.add_argument(
        "--output-file",
        "-f",
        type=str,
        help="Output file path",
    )

    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("ALPACA_API_KEY") or not os.getenv("ALPACA_SECRET_KEY"):
        print("Error: API credentials required", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize client
        client = AlpacaClient()
        
        print(f"Testing connection to Alpaca API...")
        if not client.test_connection():
            print("Error: Failed to connect to Alpaca API. Check your credentials.", file=sys.stderr)
            sys.exit(1)
            
        print("✅ Connected successfully!")
        
        # TODO: Implement actual get_news call when TASK-10 is ready
        print(f"Fetching news...")
        if args.symbols:
            print(f"Symbols: {', '.join(args.symbols)}")
        print("Note: Full implementation coming in TASK-10.")
        
    except AlpacaAuthError as e:
        print(f"Authentication Error: {e}", file=sys.stderr)
        print("Check your API credentials in .env file", file=sys.stderr)
        sys.exit(1)
    except AlpacaRateLimitError as e:
        print(f"Rate Limit Error: {e}", file=sys.stderr)
        if e.retry_after:
            print(f"Retry after: {e.retry_after} seconds", file=sys.stderr)
        sys.exit(1)
    except AlpacaNotFoundError as e:
        print(f"Not Found Error: {e}", file=sys.stderr)
        sys.exit(1)
    except AlpacaAPIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        if e.status_code:
            print(f"HTTP Status: {e.status_code}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
