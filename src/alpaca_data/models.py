"""Data models for Alpaca Market Data API responses."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from decimal import Decimal
import re


@dataclass(frozen=True)
class Bar:
    """OHLCV bar data with validation.

    Attributes:
        symbol: Stock or crypto symbol.
        timestamp: Bar timestamp.
        open: Opening price (must be positive).
        high: Highest price during bar period (must be ≥ open).
        low: Lowest price during bar period (must be ≤ open).
        close: Closing price (must be between low and high).
        volume: Trading volume (must be non-negative).
        trade_count: Number of trades (optional, must be non-negative).
        vwap: Volume weighted average price (optional, must be positive).
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

    def __post_init__(self):
        """Validate Bar data after initialization."""
        # Validate symbol format
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        
        # Validate price relationships
        if self.high < self.open:
            raise ValueError(f"High price ({self.high}) cannot be less than open price ({self.open})")
        if self.low > self.open:
            raise ValueError(f"Low price ({self.low}) cannot be greater than open price ({self.open})")
        if self.close < self.low or self.close > self.high:
            raise ValueError(f"Close price ({self.close}) must be between low ({self.low}) and high ({self.high})")
        
        # Validate positive prices
        for price_field, value in [("open", self.open), ("high", self.high), ("low", self.low), ("close", self.close)]:
            if value < 0:
                raise ValueError(f"{price_field} price must be non-negative, got {value}")
        
        # Validate volume
        if self.volume < 0:
            raise ValueError(f"Volume must be non-negative, got {self.volume}")
        
        # Validate optional fields
        if self.trade_count is not None and self.trade_count < 0:
            raise ValueError(f"Trade count must be non-negative, got {self.trade_count}")
        
        if self.vwap is not None and self.vwap < 0:
            raise ValueError(f"Vwap must be non-negative, got {self.vwap}")

    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Bar":
        """Create Bar from API response dictionary with validation."""
        # Validate required fields
        required_fields = ["t", "o", "h", "l", "c", "v"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' missing from API response")
        
        try:
            return cls(
                symbol=symbol,
                timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
                open=float(data["o"]),
                high=float(data["h"]),
                low=float(data["l"]),
                close=float(data["c"]),
                volume=float(data["v"]),
                trade_count=data.get("n"),
                vwap=data.get("vwap"),
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data format in API response: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert Bar to dictionary format."""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "trade_count": self.trade_count,
            "vwap": self.vwap,
        }


@dataclass(frozen=True)
class Quote:
    """NBBO Quote data with validation.

    Attributes:
        symbol: Stock or crypto symbol.
        timestamp: Quote timestamp.
        ask_exchange: Exchange code for ask.
        ask_price: Ask price (must be > bid_price).
        ask_size: Ask size (must be positive).
        bid_exchange: Exchange code for bid.
        bid_price: Bid price (must be positive).
        bid_size: Bid size (must be positive).
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

    def __post_init__(self):
        """Validate Quote data after initialization."""
        # Validate symbol format
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        
        # Validate exchange codes
        if not isinstance(self.ask_exchange, str) or not self.ask_exchange.strip():
            raise ValueError("Ask exchange must be a non-empty string")
        if not isinstance(self.bid_exchange, str) or not self.bid_exchange.strip():
            raise ValueError("Bid exchange must be a non-empty string")
        
        # Validate price relationships
        if self.ask_price <= self.bid_price:
            raise ValueError(f"Ask price ({self.ask_price}) must be greater than bid price ({self.bid_price})")
        
        # Validate positive values
        for field, value in [("ask_price", self.ask_price), ("bid_price", self.bid_price), 
                           ("ask_size", self.ask_size), ("bid_size", self.bid_size)]:
            if value <= 0:
                raise ValueError(f"{field} must be positive, got {value}")
        
        # Validate optional fields
        if self.conditions is not None and not isinstance(self.conditions, list):
            raise ValueError("Conditions must be a list")
        
        if self.tape is not None and not isinstance(self.tape, str):
            raise ValueError("Tape must be a string")

    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Quote":
        """Create Quote from API response dictionary with validation."""
        # Validate required fields
        required_fields = ["t", "ax", "ap", "as", "bx", "bp", "bs"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' missing from API response")
        
        try:
            return cls(
                symbol=symbol,
                timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
                ask_exchange=data["ax"],
                ask_price=float(data["ap"]),
                ask_size=float(data["as"]),
                bid_exchange=data["bx"],
                bid_price=float(data["bp"]),
                bid_size=float(data["bs"]),
                conditions=data.get("c"),
                tape=data.get("z"),
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data format in API response: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert Quote to dictionary format."""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "ask_exchange": self.ask_exchange,
            "ask_price": self.ask_price,
            "ask_size": self.ask_size,
            "bid_exchange": self.bid_exchange,
            "bid_price": self.bid_price,
            "bid_size": self.bid_size,
            "conditions": self.conditions,
            "tape": self.tape,
        }


@dataclass(frozen=True)
class Trade:
    """Trade data with validation.

    Attributes:
        symbol: Stock or crypto symbol.
        timestamp: Trade timestamp.
        exchange: Exchange code.
        price: Trade price (must be positive).
        size: Trade size (must be positive).
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

    def __post_init__(self):
        """Validate Trade data after initialization."""
        # Validate symbol format
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        
        # Validate exchange code
        if not isinstance(self.exchange, str) or not self.exchange.strip():
            raise ValueError("Exchange must be a non-empty string")
        
        # Validate positive values
        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")
        if self.size <= 0:
            raise ValueError(f"Size must be positive, got {self.size}")
        
        # Validate optional fields
        if self.conditions is not None and not isinstance(self.conditions, list):
            raise ValueError("Conditions must be a list")
        
        if self.id is not None and not isinstance(self.id, str):
            raise ValueError("ID must be a string")
        
        if self.tape is not None and not isinstance(self.tape, str):
            raise ValueError("Tape must be a string")

    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Trade":
        """Create Trade from API response dictionary with validation."""
        # Validate required fields
        required_fields = ["t", "x", "p", "s"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' missing from API response")
        
        try:
            return cls(
                symbol=symbol,
                timestamp=datetime.fromisoformat(data["t"].replace("Z", "+00:00")),
                exchange=data["x"],
                price=float(data["p"]),
                size=float(data["s"]),
                conditions=data.get("c"),
                id=data.get("i"),
                tape=data.get("z"),
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data format in API response: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert Trade to dictionary format."""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "exchange": self.exchange,
            "price": self.price,
            "size": self.size,
            "conditions": self.conditions,
            "id": self.id,
            "tape": self.tape,
        }


@dataclass(frozen=True)
class Snapshot:
    """Market snapshot data with validation.

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

    def __post_init__(self):
        """Validate Snapshot data after initialization."""
        # Validate symbol format
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        
        # Validate that at least one data component is present
        if not any([self.latest_trade, self.latest_quote, self.minute_bar, self.daily_bar, self.prev_daily_bar]):
            raise ValueError("Snapshot must contain at least one data component")

    @classmethod
    def from_dict(cls, symbol: str, data: Dict[str, Any]) -> "Snapshot":
        """Create Snapshot from API response dictionary with validation."""
        try:
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
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data format in API response: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert Snapshot to dictionary format."""
        return {
            "symbol": self.symbol,
            "latest_trade": self.latest_trade.to_dict() if self.latest_trade else None,
            "latest_quote": self.latest_quote.to_dict() if self.latest_quote else None,
            "minute_bar": self.minute_bar.to_dict() if self.minute_bar else None,
            "daily_bar": self.daily_bar.to_dict() if self.daily_bar else None,
            "prev_daily_bar": self.prev_daily_bar.to_dict() if self.prev_daily_bar else None,
        }


@dataclass(frozen=True)
class News:
    """News article data with validation.

    Attributes:
        id: News article ID.
        headline: News headline (must be non-empty).
        summary: News summary (optional).
        author: Author name (optional).
        created_at: Creation timestamp.
        updated_at: Update timestamp (optional).
        url: Source URL (optional).
        content: Full content (optional).
        symbols: List of related symbols (must be non-empty list).
        source: News source (must be non-empty).
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

    def __post_init__(self):
        """Validate News data after initialization."""
        # Validate required string fields
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("ID must be a non-empty string")
        
        if not isinstance(self.headline, str) or not self.headline.strip():
            raise ValueError("Headline must be a non-empty string")
        
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("Source must be a non-empty string")
        
        # Validate symbols list
        if not isinstance(self.symbols, list) or len(self.symbols) == 0:
            raise ValueError("Symbols must be a non-empty list")
        
        if not all(isinstance(s, str) and s.strip() for s in self.symbols):
            raise ValueError("All symbols must be non-empty strings")
        
        # Validate optional string fields
        if self.summary is not None and not isinstance(self.summary, str):
            raise ValueError("Summary must be a string or None")
        
        if self.author is not None and not isinstance(self.author, str):
            raise ValueError("Author must be a string or None")
        
        if self.url is not None and not isinstance(self.url, str):
            raise ValueError("URL must be a string or None")
        
        if self.content is not None and not isinstance(self.content, str):
            raise ValueError("Content must be a string or None")
        
        # Validate timestamps
        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime object")
        
        if self.updated_at is not None and not isinstance(self.updated_at, datetime):
            raise ValueError("updated_at must be a datetime object or None")
        
        # Validate timestamp order
        if self.updated_at and self.updated_at < self.created_at:
            raise ValueError("updated_at cannot be earlier than created_at")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "News":
        """Create News from API response dictionary with validation."""
        # Validate required fields
        required_fields = ["id", "headline", "created_at", "symbols", "source"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Required field '{field}' missing from API response")
        
        try:
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
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid data format in API response: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert News to dictionary format."""
        return {
            "id": self.id,
            "headline": self.headline,
            "summary": self.summary,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "url": self.url,
            "content": self.content,
            "symbols": self.symbols,
            "source": self.source,
        }
