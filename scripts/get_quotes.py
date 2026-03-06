#!/usr/bin/env python3
"""CLI script to fetch quotes."""

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
    """Main entry point for get_quotes CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch quotes from Alpaca Market Data API"
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="Stock symbols (e.g., AAPL MSFT)",
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date/time (for historical quotes)",
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date/time (for historical quotes)",
    )
    parser.add_argument(
        "--feed",
        default="iex",
        choices=["iex", "sip"],
        help="Data feed",
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
        
        # Prepare parameters
        params = {
            'symbols': args.symbols,
            'limit': args.limit,
            'feed': args.feed,
        }
        
        # Add optional parameters
        if args.start:
            params['start'] = args.start
        if args.end:
            params['end'] = args.end
            
        print(f"📊 Fetching quotes for: {', '.join(args.symbols)}")
        
        # Make the API call
        result = client.get_quotes(**params)
        
        # Display results
        print(f"✅ Retrieved {result['count']} quotes")
        
        # Convert quotes to output format
        if args.output == "json":
            if args.output_file:
                import json
                with open(args.output_file, 'w') as f:
                    json.dump(result, f, default=str, indent=2)
                print(f"💾 Saved to {args.output_file}")
            else:
                import json
                print(json.dumps(result, default=str, indent=2))
        
        elif args.output == "csv":
            if not result['quotes']:
                print("No quotes to export")
                return
                
            import csv
            import io
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            first_quote = result['quotes'][0]
            writer.writerow(['symbol', 'timestamp', 'ask_exchange', 'ask_price', 'ask_size', 'bid_exchange', 'bid_price', 'bid_size', 'conditions', 'tape'])
            
            # Write quote data
            for quote in result['quotes']:
                writer.writerow([
                    quote.symbol,
                    quote.timestamp,
                    quote.ask_exchange,
                    quote.ask_price,
                    quote.ask_size,
                    quote.bid_exchange,
                    quote.bid_price,
                    quote.bid_size,
                    '|'.join(quote.conditions) if quote.conditions else '',
                    quote.tape or ''
                ])
            
            # Output CSV
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(output.getvalue())
                print(f"💾 Saved to {args.output_file}")
            else:
                print("📄 CSV Output:")
                print(output.getvalue())
        
        # Show pagination info if available
        if result.get('has_next_page'):
            print(f"📖 More pages available. Next page token: {result['next_page_token']}")
        
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
        print("Check that your symbols are valid", file=sys.stderr)
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
