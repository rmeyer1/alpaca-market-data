# Options Chain Feature

The `alpaca-option-chain` command provides comprehensive access to option chains for any underlying symbol, giving you complete market data for all available option contracts.

## Overview

The options chain endpoint retrieves the latest trade, latest quote, and greeks for each contract symbol of the underlying symbol from Alpaca's data feed.

**Endpoint**: `https://data.alpaca.markets/v1beta1/options/snapshots/{underlying_symbol}`

## Usage

### CLI Command

```bash
# Get options chain for AAPL
alpaca-option-chain AAPL

# Get options chain with premium data feed
alpaca-option-chain AAPL --feed sip

# Get options chain with JSON output
alpaca-option-chain TSLA --format json

# Get detailed view of all contracts
alpaca-option-chain SPY --verbose

# Get options chain with CSV output
alpaca-option-chain NVDA --format csv --output-file chain.csv
```

### Command Line Options

- `underlying_symbol`: Stock/ETF symbol (e.g., AAPL, TSLA, SPY, NVDA)
- `--feed`: Data feed selection (default: iex)
  - `iex`: Free tier data
  - `sip`: Premium data feed
- `--format`: Output format (default: table)
  - `table`: Human-readable formatted table
  - `json`: JSON format for programmatic use
  - `csv`: CSV format for spreadsheet analysis
- `--verbose`: Show detailed information for all contracts
- `--output-file`: Save CSV output to file (for csv format)

### Python API

```python
from alpaca_data import AlpacaClient

# Initialize client
client = AlpacaClient()

# Get options chain
result = client.get_option_chain(
    underlying_symbol="AAPL",
    feed="iex",
    output_format="dict"
)

# Access the chain data
option_chain = result["option_chain"]
print(f"Got {result['contract_count']} contracts for {result['underlying_symbol']}")
print(f"Calls: {result['calls_count']}, Puts: {result['puts_count']}")

# Filter contracts
calls = option_chain.get_call_contracts()
puts = option_chain.get_put_contracts()

# Get contracts by strike price
strike_200 = option_chain.get_contracts_by_strike(200.0)
for symbol, snapshot in strike_200.items():
    print(f"{symbol}: ${snapshot.latest_quote.bid_price} - ${snapshot.latest_quote.ask_price}")
```

## Data Structure

The OptionChain object contains:

- `underlying_symbol`: The underlying stock/ETF symbol
- `contracts`: Dictionary mapping contract symbols to OptionSnapshot objects
- `timestamp`: When the data was retrieved
- `underlying_price`: Current price of the underlying asset
- `feed`: Data feed used (iex or sip)

### Contract Filtering Methods

The OptionChain object provides several methods to filter contracts:

- `get_call_contracts()`: Returns all call options
- `get_put_contracts()`: Returns all put options  
- `get_contracts_by_strike(strike_price)`: Returns contracts for a specific strike price

### Contract Symbol Format

Option symbols follow this format: `UNDERLYING + DATE + TYPE + STRIKE`

Examples:
- `AAPL240119C200`: Apple call option expiring 2024-01-19 with $200 strike
- `TSLA240315P250`: Tesla put option expiring 2024-03-15 with $250 strike

## Output Examples

### Table Format (Default)
```
🎯 Options Chain for AAPL
📋 Total: 24 contracts (12 calls, 12 puts)
💰 Underlying Price: $150.25
📅 Updated: 2024-01-18T14:30:00Z

📞 CALL OPTIONS (Top 10 by Volume)
Symbol               Strike   Exp        Bid      Ask      Delta     IV    
----------------------------------------------------------------------
AAPL240119C200       200      2024-01-19 $2.40    $2.60    0.65      0.25
AAPL240119C210       210      2024-01-19 $1.80    $2.00    0.45      0.27
AAPL240119C220       220      2024-01-19 $1.20    $1.40    0.25      0.30
...
```

### JSON Format
```json
{
  "option_chain": {
    "underlying_symbol": "AAPL",
    "contracts": {
      "AAPL240119C200": {
        "symbol": "AAPL240119C200",
        "iv": 0.25,
        "open_interest": 1000,
        "latest_trade": {
          "price": 2.50,
          "size": 10,
          "timestamp": "2024-01-18T14:30:00Z"
        },
        "latest_quote": {
          "bid_price": 2.40,
          "ask_price": 2.60,
          "bid_size": 5,
          "ask_size": 15
        },
        "greeks": {
          "delta": 0.65,
          "gamma": 0.02,
          "theta": -0.03,
          "vega": 0.15,
          "rho": 0.08
        },
        "underlying_price": 150.25
      }
    },
    "timestamp": "2024-01-18T14:30:00Z",
    "underlying_price": 150.25,
    "feed": "iex"
  },
  "underlying_symbol": "AAPL",
  "feed": "iex",
  "contract_count": 24,
  "calls_count": 12,
  "puts_count": 12
}
```

### CSV Format
The CSV output includes columns: Contract Symbol, Type, Strike, Expiration, Trade Price, Trade Size, Bid Price, Bid Size, Ask Price, Ask Size, Delta, Gamma, Theta, Vega, Rho, Implied Vol, Open Interest.

## Common Use Cases

1. **Options Strategy Analysis**: Analyze entire option chains to identify trading opportunities
2. **Volatility Analysis**: Compare implied volatility across different strikes and expirations  
3. **Greeks Analysis**: Study delta, gamma, theta, and vega across the chain
4. **Risk Management**: Monitor open interest and liquidity by strike price
5. **Price Discovery**: Identify mispriced options using real-time market data

## API Rate Limits

- Rate limits apply as per your Alpaca data plan
- The endpoint provides comprehensive data for the entire chain in a single request
- Consider caching results if making frequent requests for the same symbol

## Error Handling

The API will return appropriate errors for:
- Invalid or unknown symbols
- Rate limit exceeded
- Authentication failures
- Network connectivity issues

## Related Features

- `alpaca-option-snapshot`: Get data for specific option symbols
- `alpaca-option-quotes`: Get quotes for multiple option symbols
- `alpaca-option-trades`: Get trades for multiple option symbols

This feature provides a complete view of the options market for any underlying symbol, making it ideal for options trading, analysis, and strategy development.