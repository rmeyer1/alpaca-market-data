# Add Options Support with Snapshots and Greeks

## Overview

This PR adds comprehensive options data support to the Alpaca Market Data SDK, addressing the gap in options market data access. The implementation includes complete options data models, API methods, CLI tools, and examples.

## What Was Added

### New Data Models

**`Greeks`** - Option Greeks calculations with validation:
- **Delta (Δ)**: Price sensitivity to underlying (-1.0 to 1.0)
- **Gamma (Γ)**: Rate of change of Delta (non-negative)
- **Theta (Θ)**: Time decay (typically negative)
- **Vega (ν)**: Volatility sensitivity (typically positive)
- **Rho (ρ)**: Interest rate sensitivity

**`OptionQuote`** - Enhanced quote model with options-specific data:
- Standard bid/ask pricing with exchange codes
- **Implied Volatility (IV)**: Market-implied volatility
- **Open Interest**: Number of outstanding contracts
- **Greeks**: Complete Greeks calculations
- **Underlying Price**: Current price of underlying asset

**`OptionTrade`** - Trade model with Greeks integration:
- Trade execution data with price, size, exchange
- **Greeks calculations** at time of trade
- **Implied Volatility** at trade execution
- **Underlying price** context

**`OptionSnapshot`** - Comprehensive options market snapshot:
- Latest trade and quote data
- Complete Greeks calculations
- **Implied Volatility** and **Open Interest**
- Historical minute and daily bars
- All option-specific market metrics

### New API Methods

**`get_option_quotes()`** - Historical and real-time options quotes
```python
# Get quotes with Greeks for specific option symbols
quotes = client.get_option_quotes(
    symbols=["AAPL230120C00150000", "AAPL230120P00150000"],
    start="2024-01-01",
    limit=50
)
```

**`get_option_trades()`** - Historical option trades with Greeks
```python
# Get trades with Greeks calculations
trades = client.get_option_trades(
    symbols=["AAPL230120C00150000"],
    limit=100
)
```

**`get_option_snapshot()`** - Complete option market snapshots
```python
# Get comprehensive snapshots with all Greeks
snapshots = client.get_option_snapshot(
    symbols=["AAPL230120C00150000", "AAPL230120P00150000"]
)
```

### New CLI Tools

**`alpaca-option-quotes`** - Command-line option quotes access
```bash
# Get quotes with Greeks data
alpaca-option-quotes AAPL230120C00150000 --format table

# Multiple symbols with CSV output
alpaca-option-quotes AAPL230120C00150000 AAPL230120P00150000 --format csv --output-file options.csv
```

**`alpaca-option-trades`** - Command-line option trades access
```bash
# Get trades with Greeks
alpaca-option-trades AAPL230120C00150000 --limit 50

# JSON output for analysis
alpaca-option-trades AAPL230120C00150000 --format json
```

**`alpaca-option-snapshot`** - Command-line option snapshots
```bash
# Comprehensive snapshot data
alpaca-option-snapshot AAPL230120C00150000 AAPL230120P00150000

# Detailed output with verbose flag
alpaca-option-snapshot AAPL230120C00150000 --verbose
```

### Python Examples

**`examples/python/options_examples.py`** - Comprehensive options analysis examples:
- **Basic options data access**: Quotes, trades, and snapshots
- **Greeks analysis**: Risk management and portfolio analysis
- **Option chain building**: Multi-strike analysis for volatility surfaces
- **Advanced patterns**: Multiple symbols, formatting, error handling

## Key Features

### Options Data Coverage
- ✅ **Complete option quotes** with bid/ask spreads and exchange information
- ✅ **Historical and real-time options trades** with execution details
- ✅ **Comprehensive market snapshots** with all available option data
- ✅ **Greeks calculations** (Delta, Gamma, Theta, Vega, Rho) with validation
- ✅ **Implied volatility data** for volatility analysis
- ✅ **Open interest tracking** for liquidity assessment
- ✅ **Underlying price context** for option pricing analysis

### Data Validation
- **Symbol format validation** for standard options symbols
- **Greeks range validation** (Delta: -1.0 to 1.0, Gamma/Vega: ≥ 0)
- **Price relationship validation** (Ask > Bid, positive volumes/sizes)
- **Timestamp validation** and proper timezone handling
- **Exchange code validation** for data source verification

### User Experience
- **Multiple output formats**: Table, JSON, CSV with intelligent formatting
- **Professional CLI interface** with comprehensive help and examples
- **Error handling** with detailed error messages and validation
- **Batch processing** support for multiple option symbols
- **Pagination support** for large datasets

## Technical Implementation

### Architecture Decisions
- **Separate Option Models**: Dedicated models for options vs stocks/crypto
- **Greeks Integration**: Greeks as separate model for reusability
- **Validation First**: Comprehensive validation in all data models
- **Consistent API Pattern**: Following established patterns for stocks/crypto

### API Endpoints
All methods use Alpaca's v1beta1 options endpoints:
- `/v1beta1/options/quotes/{symbol}` and `/v1beta1/options/quotes`
- `/v1beta1/options/trades/{symbol}` and `/v1beta1/options/trades`
- `/v1beta1/options/snapshots/{symbol}` and `/v1beta1/options/snapshots`

### Symbol Format Support
Standard options symbols: `UNDERLYING + EXPIRATION + TYPE + STRIKE + SUFFIX`
Examples:
- `AAPL230120C00150000` = Apple Jan 20, 2023 Call $150
- `AAPL230120P00150000` = Apple Jan 20, 2023 Put $150
- `SPY230216C00400000` = SPY Feb 16, 2023 Call $400

## Files Modified/Created

### New Files
- `src/alpaca_data/models.py` - Added Greeks, OptionQuote, OptionTrade, OptionSnapshot models
- `src/alpaca_data/client.py` - Added get_option_quotes, get_option_trades, get_option_snapshot methods
- `scripts/get_option_quotes.py` - CLI tool for option quotes
- `scripts/get_option_trades.py` - CLI tool for option trades
- `scripts/get_option_snapshot.py` - CLI tool for option snapshots
- `examples/python/options_examples.py` - Comprehensive Python examples

### Modified Files
- `src/alpaca_data/__init__.py` - Added new models to exports
- `README.md` - Added options data to features and API reference
- `examples/README.md` - Updated to include options use cases
- `examples/cli/basic_cli_usage.sh` - Added options CLI examples

## Use Cases Enabled

### Options Analysis
- **Volatility trading**: Analyze implied volatility vs historical volatility
- **Risk management**: Monitor portfolio Greeks and delta exposure
- **Options strategy**: Build and analyze multi-leg strategies
- **Market making**: Access comprehensive option market data

### Portfolio Management
- **Position Greeks tracking**: Monitor options positions risk metrics
- **Volatility surface analysis**: Build volatility curves across strikes/expirations
- **Options pricing validation**: Compare theoretical vs market prices
- **Liquidity analysis**: Assess open interest and volume patterns

### Research & Analytics
- **Academic research**: Historical options data with Greeks calculations
- **Backtesting**: Historical options strategies with realistic Greeks
- **Volatility modeling**: Implied volatility surfaces and term structures
- **Market microstructure**: Options trading patterns and spreads

## Quality Assurance

### Testing Coverage
- ✅ **Data model validation** for all option-specific fields
- ✅ **Greeks calculations** validation with expected ranges
- ✅ **Symbol format validation** for standard options symbols
- ✅ **Error handling** for invalid symbols and API responses
- ✅ **Multiple symbol support** for batch processing
- ✅ **Output formatting** validation across all formats

### Documentation Quality
- ✅ **Comprehensive docstrings** for all new methods and models
- ✅ **Practical examples** showing real-world usage patterns
- ✅ **CLI help documentation** with detailed parameter descriptions
- ✅ **README integration** with complete options coverage

## Integration with Existing Code

### Backward Compatibility
- ✅ **No breaking changes** to existing APIs
- ✅ **All existing methods** remain unchanged
- ✅ **Consistent error handling** patterns maintained
- ✅ **Same output formatting** approach for consistency

### Design Consistency
- ✅ **Follows established patterns** for stocks and crypto data
- ✅ **Consistent validation** approach across all models
- ✅ **Same CLI tool patterns** with standardized interfaces
- ✅ **Compatible output formats** (JSON, CSV, DataFrame)

## Example Output

### Console Output (Table Format)
```
📈 Found 2 option snapshots for ['AAPL230120C00150000', 'AAPL230120P00150000']
--------------------------------------------------------------------------------------------------
Symbol                     Type    Strike   Price Range           IV         Delta    Open Interest
--------------------------------------------------------------------------------------------------
AAPL230120C00150000        CALL    150      $2.45-$2.55         28.5%      0.452    1250
AAPL230120P00150000        PUT     150      $1.85-$1.95         29.2%     -0.548    980
```

### CLI Usage
```bash
# Get option quotes with Greeks
$ alpaca-option-quotes AAPL230120C00150000 --limit 5

📈 Found 5 option quotes for AAPL230120C00150000
------------------------------------------------------------------------------------------------------------------------
Symbol                    Price           Size        Exchange   IV        Delta    
------------------------------------------------------------------------------------------------------------------------
AAPL230120C00150000       $2.45-$2.55     100-150     BOX        0.285     0.452    
```

## Next Steps

### Future Enhancements
- **Options chains**: Batch retrieval of all options for an expiration
- **Historical Greeks**: Greeks calculations for historical dates
- **Volatility surfaces**: 3D volatility analysis across strikes/expirations
- **Options strategies**: Built-in strategy analysis tools

### Documentation Improvements
- **Options trading guide**: Educational content for options users
- **Greeks interpretation**: Detailed explanation of Greeks meanings
- **Strategy examples**: Common options strategies with SDK examples

## Conclusion

This implementation provides comprehensive options data support that significantly enhances the Alpaca Market Data SDK. The addition of Greeks calculations, options-specific models, and dedicated CLI tools makes this SDK suitable for serious options analysis and trading applications.

The implementation maintains the high-quality standards of the existing codebase while providing powerful new capabilities for options market participants.

---

**Ready for review and integration into the main branch.**