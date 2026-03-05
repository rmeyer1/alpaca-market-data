#!/usr/bin/env python3
"""CLI script to fetch news."""

import argparse
import os
import sys


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

    print(f"Fetching news...")
    if args.symbols:
        print(f"Symbols: {', '.join(args.symbols)}")
    print("Note: Placeholder implementation. Full implementation coming in TASK-10.")


if __name__ == "__main__":
    main()
