#!/usr/bin/env python3
"""
Get Options Chain CLI

Fetch complete options chain for an underlying symbol including all calls and puts.
"""

import sys
import typer
from typing import List, Optional
from datetime import datetime
from alpaca_data import AlpacaClient

app = typer.Typer(help="Fetch complete options chains with all available contracts for underlying symbols.")


def format_output(data, output_format: str = "table", verbose: bool = False):
    """Format the options chain data for output."""
    if output_format == "json":
        import json
        print(json.dumps(data, indent=2, default=str))
        return
    
    if output_format == "csv":
        import csv
        import io
        
        option_chain = data.get('option_chain')
        if not option_chain or not hasattr(option_chain, 'contracts'):
            print("No options chain found")
            return
            
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Contract Symbol', 'Type', 'Strike', 'Expiration', 'Trade Price', 'Trade Size',
            'Bid Price', 'Bid Size', 'Ask Price', 'Ask Size',
            'Delta', 'Gamma', 'Theta', 'Vega', 'Rho', 'Implied Vol', 'Open Interest'
        ])
        
        # Write data for all contracts
        contracts = option_chain.contracts
        for symbol, snapshot in contracts.items():
            # Parse option symbol for additional info
            option_type = "CALL" if option_chain._is_call_contract(symbol) else "PUT"
            
            # Extract strike price and expiration (basic parsing)
            strike = "N/A"
            expiration = "N/A"
            if len(symbol) > 10:
                try:
                    # Format: UNDERLYING + DATE + TYPE + STRIKE
                    # AAPL240119C200 -> expiration: 2024-01-19, strike: 200.0
                    date_part = symbol[-10:-6]  # "240119" -> "240119"
                    type_part = symbol[-6:-0]   # "C200" -> "C200"
                    
                    # Parse expiration (YYMMDD)
                    if len(date_part) == 6 and date_part.isdigit():
                        year = f"20{date_part[:2]}"  # "24" -> "2024"
                        month = date_part[2:4]       # "01" -> "01"
                        day = date_part[4:6]         # "19" -> "19"
                        expiration = f"{year}-{month}-{day}"
                    
                    # Parse strike price
                    if len(type_part) > 1 and type_part[1:].replace('.', '').isdigit():
                        strike = f"{float(type_part[1:]):.2f}"
                except (ValueError, IndexError):
                    pass
            
            # Get trade data
            trade_price = "N/A"
            trade_size = "N/A"
            if snapshot.latest_trade:
                trade_price = f"${snapshot.latest_trade.price:.2f}"
                trade_size = int(snapshot.latest_trade.size)
            
            # Get quote data
            bid_price = "N/A"
            bid_size = "N/A"
            ask_price = "N/A"
            ask_size = "N/A"
            if snapshot.latest_quote:
                bid_price = f"${snapshot.latest_quote.bid_price:.2f}" if snapshot.latest_quote.bid_price else "N/A"
                bid_size = int(snapshot.latest_quote.bid_size) if snapshot.latest_quote.bid_size else "N/A"
                ask_price = f"${snapshot.latest_quote.ask_price:.2f}" if snapshot.latest_quote.ask_price else "N/A"
                ask_size = int(snapshot.latest_quote.ask_size) if snapshot.latest_quote.ask_size else "N/A"
            
            # Get greeks
            delta = "N/A"
            gamma = "N/A"
            theta = "N/A"
            vega = "N/A"
            rho = "N/A"
            if snapshot.greeks:
                delta = f"{snapshot.greeks.delta:.3f}" if snapshot.greeks.delta else "N/A"
                gamma = f"{snapshot.greeks.gamma:.3f}" if snapshot.greeks.gamma else "N/A"
                theta = f"{snapshot.greeks.theta:.3f}" if snapshot.greeks.theta else "N/A"
                vega = f"{snapshot.greeks.vega:.3f}" if snapshot.greeks.vega else "N/A"
                rho = f"{snapshot.greeks.rho:.3f}" if snapshot.greeks.rho else "N/A"
            
            # Get additional metrics
            iv = "N/A"
            open_interest = "N/A"
            if snapshot.iv is not None:
                iv = f"{snapshot.iv:.3f}"
            if snapshot.open_interest is not None:
                open_interest = int(snapshot.open_interest)
            
            writer.writerow([
                symbol, option_type, strike, expiration, trade_price, trade_size,
                bid_price, bid_size, ask_price, ask_size,
                delta, gamma, theta, vega, rho, iv, open_interest
            ])
        
        print(output.getvalue())
        return
    
    # Default table format
    if verbose:
        print(f"\n🔍 Options Chain Details")
        print(f"{'='*80}")
        
        print(f"📈 Underlying Symbol: {data['underlying_symbol']}")
        print(f"📊 Feed: {data['feed']}")
        print(f"📅 Timestamp: {data['timestamp'] or 'N/A'}")
        print(f"💰 Underlying Price: ${data['underlying_price']:.2f}" if data['underlying_price'] else "💰 Underlying Price: N/A")
        print(f"📋 Total Contracts: {data['contract_count']}")
        print(f"📞 Call Contracts: {data['calls_count']}")
        print(f"📉 Put Contracts: {data['puts_count']}")
        print(f"{'='*80}\n")
    
    option_chain = data.get('option_chain')
    if not option_chain or not hasattr(option_chain, 'contracts'):
        print("❌ No options chain found")
        return
    
    contracts = option_chain.contracts
    
    # Display summary
    if not verbose:
        calls = option_chain.get_call_contracts()
        puts = option_chain.get_put_contracts()
        print(f"\n🎯 Options Chain for {data['underlying_symbol']}")
        print(f"📋 Total: {data['contract_count']} contracts ({data['calls_count']} calls, {data['puts_count']} puts)")
        if data['underlying_price']:
            print(f"💰 Underlying Price: ${data['underlying_price']:.2f}")
        if data['timestamp']:
            print(f"📅 Updated: {data['timestamp']}")
        print()
    
    # Group contracts by type and strike for better display
    calls = option_chain.get_call_contracts()
    puts = option_chain.get_put_contracts()
    
    if verbose:
        # Detailed view - show all contracts
        print("📞 CALL OPTIONS")
        print(f"{'Symbol':<20} {'Strike':<8} {'Exp':<10} {'Bid':<8} {'Ask':<8} {'Trade':<8} {'Size':<6} {'Delta':<7} {'IV':<6} {'OI':<8}")
        print("-" * 95)
        
        for symbol, snapshot in calls.items():
            # Parse strike and expiration
            strike = "N/A"
            expiration = "N/A"
            if len(symbol) > 10:
                try:
                    date_part = symbol[-10:-6]
                    type_part = symbol[-6:-0]
                    if len(date_part) == 6 and date_part.isdigit():
                        year = f"20{date_part[:2]}"
                        month = date_part[2:4]
                        day = date_part[4:6]
                        expiration = f"{year}-{month}-{day}"
                    if len(type_part) > 1 and type_part[1:].replace('.', '').isdigit():
                        strike = f"{float(type_part[1:]):.0f}"
                except (ValueError, IndexError):
                    pass
            
            # Get trade/quote data
            bid = f"${snapshot.latest_quote.bid_price:.2f}" if snapshot.latest_quote and snapshot.latest_quote.bid_price else "N/A"
            ask = f"${snapshot.latest_quote.ask_price:.2f}" if snapshot.latest_quote and snapshot.latest_quote.ask_price else "N/A"
            trade = f"${snapshot.latest_trade.price:.2f}" if snapshot.latest_trade else "N/A"
            size = int(snapshot.latest_trade.size) if snapshot.latest_trade else "N/A"
            delta = f"{snapshot.greeks.delta:.2f}" if snapshot.greeks and snapshot.greeks.delta else "N/A"
            iv = f"{snapshot.iv:.2f}" if snapshot.iv else "N/A"
            oi = int(snapshot.open_interest) if snapshot.open_interest else "N/A"
            
            print(f"{symbol:<20} {strike:<8} {expiration:<10} {bid:<8} {ask:<8} {trade:<8} {size:<6} {delta:<7} {iv:<6} {oi:<8}")
        
        print("\n📉 PUT OPTIONS")
        print(f"{'Symbol':<20} {'Strike':<8} {'Exp':<10} {'Bid':<8} {'Ask':<8} {'Trade':<8} {'Size':<6} {'Delta':<7} {'IV':<6} {'OI':<8}")
        print("-" * 95)
        
        for symbol, snapshot in puts.items():
            # Parse strike and expiration
            strike = "N/A"
            expiration = "N/A"
            if len(symbol) > 10:
                try:
                    date_part = symbol[-10:-6]
                    type_part = symbol[-6:-0]
                    if len(date_part) == 6 and date_part.isdigit():
                        year = f"20{date_part[:2]}"
                        month = date_part[2:4]
                        day = date_part[4:6]
                        expiration = f"{year}-{month}-{day}"
                    if len(type_part) > 1 and type_part[1:].replace('.', '').isdigit():
                        strike = f"{float(type_part[1:]):.0f}"
                except (ValueError, IndexError):
                    pass
            
            # Get trade/quote data
            bid = f"${snapshot.latest_quote.bid_price:.2f}" if snapshot.latest_quote and snapshot.latest_quote.bid_price else "N/A"
            ask = f"${snapshot.latest_quote.ask_price:.2f}" if snapshot.latest_quote and snapshot.latest_quote.ask_price else "N/A"
            trade = f"${snapshot.latest_trade.price:.2f}" if snapshot.latest_trade else "N/A"
            size = int(snapshot.latest_trade.size) if snapshot.latest_trade else "N/A"
            delta = f"{snapshot.greeks.delta:.2f}" if snapshot.greeks and snapshot.greeks.delta else "N/A"
            iv = f"{snapshot.iv:.2f}" if snapshot.iv else "N/A"
            oi = int(snapshot.open_interest) if snapshot.open_interest else "N/A"
            
            print(f"{symbol:<20} {strike:<8} {expiration:<10} {bid:<8} {ask:<8} {trade:<8} {size:<6} {delta:<7} {iv:<6} {oi:<8}")
    else:
        # Summary view - show key contracts only
        print("📞 CALL OPTIONS (Top 10 by Volume)")
        print(f"{'Symbol':<20} {'Strike':<8} {'Exp':<10} {'Bid':<8} {'Ask':<8} {'Delta':<7} {'IV':<6}")
        print("-" * 70)
        
        # Sort calls by open interest (descending)
        sorted_calls = sorted(calls.items(), 
                            key=lambda x: x[1].open_interest or 0, 
                            reverse=True)[:10]
        
        for symbol, snapshot in sorted_calls:
            # Parse strike and expiration
            strike = "N/A"
            expiration = "N/A"
            if len(symbol) > 10:
                try:
                    date_part = symbol[-10:-6]
                    type_part = symbol[-6:-0]
                    if len(date_part) == 6 and date_part.isdigit():
                        year = f"20{date_part[:2]}"
                        month = date_part[2:4]
                        day = date_part[4:6]
                        expiration = f"{year}-{month}-{day}"
                    if len(type_part) > 1 and type_part[1:].replace('.', '').isdigit():
                        strike = f"{float(type_part[1:]):.0f}"
                except (ValueError, IndexError):
                    pass
            
            # Get quote data
            bid = f"${snapshot.latest_quote.bid_price:.2f}" if snapshot.latest_quote and snapshot.latest_quote.bid_price else "N/A"
            ask = f"${snapshot.latest_quote.ask_price:.2f}" if snapshot.latest_quote and snapshot.latest_quote.ask_price else "N/A"
            delta = f"{snapshot.greeks.delta:.2f}" if snapshot.greeks and snapshot.greeks.delta else "N/A"
            iv = f"{snapshot.iv:.2f}" if snapshot.iv else "N/A"
            
            print(f"{symbol:<20} {strike:<8} {expiration:<10} {bid:<8} {ask:<8} {delta:<7} {iv:<6}")
        
        print("\n📉 PUT OPTIONS (Top 10 by Volume)")
        print(f"{'Symbol':<20} {'Strike':<8} {'Exp':<10} {'Bid':<8} {'Ask':<8} {'Delta':<7} {'IV':<6}")
        print("-" * 70)
        
        # Sort puts by open interest (descending)
        sorted_puts = sorted(puts.items(), 
                           key=lambda x: x[1].open_interest or 0, 
                           reverse=True)[:10]
        
        for symbol, snapshot in sorted_puts:
            # Parse strike and expiration
            strike = "N/A"
            expiration = "N/A"
            if len(symbol) > 10:
                try:
                    date_part = symbol[-10:-6]
                    type_part = symbol[-6:-0]
                    if len(date_part) == 6 and date_part.isdigit():
                        year = f"20{date_part[:2]}"
                        month = date_part[2:4]
                        day = date_part[4:6]
                        expiration = f"{year}-{month}-{day}"
                    if len(type_part) > 1 and type_part[1:].replace('.', '').isdigit():
                        strike = f"{float(type_part[1:]):.0f}"
                except (ValueError, IndexError):
                    pass
            
            # Get quote data
            bid = f"${snapshot.latest_quote.bid_price:.2f}" if snapshot.latest_quote and snapshot.latest_quote.bid_price else "N/A"
            ask = f"${snapshot.latest_quote.ask_price:.2f}" if snapshot.latest_quote and snapshot.latest_quote.ask_price else "N/A"
            delta = f"{snapshot.greeks.delta:.2f}" if snapshot.greeks and snapshot.greeks.delta else "N/A"
            iv = f"{snapshot.iv:.2f}" if snapshot.iv else "N/A"
            
            print(f"{symbol:<20} {strike:<8} {expiration:<10} {bid:<8} {ask:<8} {delta:<7} {iv:<6}")
    
    print(f"\n💡 Use --verbose for detailed view of all contracts")


@app.command()
def main(
    underlying_symbol: str = typer.Argument(..., help="Underlying stock/ETF symbol (e.g., AAPL, TSLA, SPY)"),
    feed: str = typer.Option("indicative", "--feed", help="Data feed: indicative (free, limited) or opra (requires signed agreement)"),
    format: str = typer.Option("table", "--format", help="Output format: table, json, csv"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed information for all contracts"),
):
    """Fetch complete options chain for an underlying symbol.
    
    This command retrieves all available option contracts (calls and puts) for a given underlying symbol,
    including latest trade, latest quote, and greeks for each contract.
    
    Examples:
        alpaca-option-chain AAPL
        alpaca-option-chain AAPL --feed sip
        alpaca-option-chain TSLA --format json
        alpaca-option-chain SPY --verbose
        alpaca-option-chain NVDA --format csv --output-file chain.csv
    """
    try:
        # Initialize client
        client = AlpacaClient()
        
        if verbose:
            typer.echo(f"Getting options chain for {underlying_symbol}")
            typer.echo(f"Feed: {feed}")
            typer.echo(f"Format: {format}")
        
        # Make API call
        result = client.get_option_chain(
            underlying_symbol=underlying_symbol,
            feed=feed,
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