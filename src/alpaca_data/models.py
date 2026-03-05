"""Data models for Alpaca Market Data API responses."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class Bar:
    """OHLCV bar data.

    Attributes:
        symbol: Stock or crypto symbol.
        timestamp: Bar timestamp.
        open: Opening price.
        high: Highest price during bar period.
        low: Lowest price during bar period.
        close: Closing price.
        volume: Trading volume.
        trade_count: Number of trades (optional).
        vwap: Volume weighted average price (optional).
    """

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: Optional[int] = None
    vwap: Optional[float] = None

    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Bar":
        """Create Bar from API response dictionary."""
        return cls(
            symbol=symbol,
            timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
            open=data["o"],
            high=data["h"],
            low=data["l"],
            close=data["c"],
            volume=data["v"],
            trade_count=data.get("n"),
            vwap=data.get("vw"),
        )


@dataclass
class Quote:
    """NBBO Quote data.

    Attributes:
        symbol: Stock or crypto symbol.
        timestamp: Quote timestamp.
        ask_exchange: Exchange code for ask.
        ask_price: Ask price.
        ask_size: Ask size.
        bid_exchange: Exchange code for bid.
        bid_price: Bid price.
        bid_size: Bid size.
        conditions: Quote conditions (optional).
        tape: Tape code (optional).
    """

    symbol: str
    timestamp: datetime
    ask_exchange: str
    ask_price: float
    ask_size: float
    bid_exchange: str
    bid_price: float
    bid_size: float
    conditions: Optional[List[str]] = None
    tape: Optional[str] = None


@dataclass
class Trade:
    """Trade data.

    Attributes:
        symbol: Stock or crypto symbol.
        timestamp: Trade timestamp.
        exchange: Exchange code.
        price: Trade price.
        size: Trade size.
        conditions: Trade conditions (optional).
        id: Trade ID (optional).
        tape: Tape code (optional).
    """

    symbol: str
    timestamp: datetime
    exchange: str
    price: float
    size: float
    conditions: Optional[List[str]] = None
    id: Optional[str] = None
    tape: Optional[str] = None


@dataclass
class Snapshot:
    """Market snapshot data.

    Attributes:
        symbol: Stock or crypto symbol.
        latest_trade: Latest trade (optional).
        latest_quote: Latest quote (optional).
        minute_bar: Current minute bar (optional).
        daily_bar: Current daily bar (optional).
        prev_daily_bar: Previous day's daily bar (optional).
    """

    symbol: str
    latest_trade: Optional[Trade] = None
    latest_quote: Optional[Quote] = None
    minute_bar: Optional[Bar] = None
    daily_bar: Optional[Bar] = None
    prev_daily_bar: Optional[Bar] = None


@dataclass
class News:
    """News article data.

    Attributes:
        id: News article ID.
        headline: News headline.
        summary: News summary (optional).
        author: Author name (optional).
        created_at: Creation timestamp.
        updated_at: Update timestamp (optional).
        url: Source URL (optional).
        content: Full content (optional).
        symbols: List of related symbols.
        source: News source.
    """

    id: str
    headline: str
    created_at: datetime
    symbols: List[str]
    source: str
    summary: Optional[str] = None
    author: Optional[str] = None
    updated_at: Optional[datetime] = None
    url: Optional[str] = None
    content: Optional[str] = None
