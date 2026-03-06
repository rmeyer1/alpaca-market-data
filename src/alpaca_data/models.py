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

    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Quote":
        """Create Quote from API response dictionary."""
        return cls(
            symbol=symbol,
            timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
            ask_exchange=data["ax"],
            ask_price=data["ap"],
            ask_size=data["as"],
            bid_exchange=data["bx"],
            bid_price=data["bp"],
            bid_size=data["bs"],
            conditions=data.get("c"),
            tape=data.get("z"),
        )


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

    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Trade":
        """Create Trade from API response dictionary."""
        return cls(
            symbol=symbol,
            timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
            exchange=data["x"],
            price=data["p"],
            size=data["s"],
            conditions=data.get("c"),
            id=data.get("i"),
            tape=data.get("z"),
        )


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

    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Snapshot":
        """Create Snapshot from API response dictionary."""
        latest_trade_data = data.get("latest_trade")
        latest_quote_data = data.get("latest_quote")
        minute_bar_data = data.get("minute_bar")
        daily_bar_data = data.get("daily_bar")
        prev_daily_bar_data = data.get("prev_daily_bar")

        return cls(
            symbol=symbol,
            latest_trade=Trade.from_dict(symbol, latest_trade_data) if latest_trade_data else None,
            latest_quote=Quote.from_dict(symbol, latest_quote_data) if latest_quote_data else None,
            minute_bar=Bar.from_dict(symbol, minute_bar_data) if minute_bar_data else None,
            daily_bar=Bar.from_dict(symbol, daily_bar_data) if daily_bar_data else None,
            prev_daily_bar=Bar.from_dict(symbol, prev_daily_bar_data) if prev_daily_bar_data else None,
        )


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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "News":
        """Create News from API response dictionary."""
        return cls(
            id=data["id"],
            headline=data["headline"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            symbols=data["symbols"],
            source=data["source"],
            summary=data.get("summary"),
            author=data.get("author"),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")) if data.get("updated_at") else None,
            url=data.get("url"),
            content=data.get("content"),
        )
