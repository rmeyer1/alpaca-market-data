"""Test get_news method implementation."""

import pytest
from unittest.mock import Mock, patch
from alpaca_data import AlpacaClient, News
from alpaca_data.exceptions import AlpacaAPIError


class TestGetNews:
    """Test cases for the get_news method."""

    @patch('alpaca_data.client.requests.request')
    def test_get_news_basic(self, mock_request):
        """Test get_news with basic parameters."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "news": [
                {
                    "id": "news_123",
                    "headline": "AAPL Reports Strong Quarterly Earnings",
                    "summary": "Apple Inc. exceeded analyst expectations...",
                    "author": "John Smith",
                    "created_at": "2024-01-01T15:30:00Z",
                    "updated_at": "2024-01-01T16:00:00Z",
                    "url": "https://example.com/news/123",
                    "content": "Full article content here...",
                    "symbols": ["AAPL"],
                    "source": "Reuters"
                }
            ],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_news
        result = client.get_news()

        # Verify results
        assert result["count"] == 1
        assert len(result["news"]) == 1
        assert result["has_next_page"] is False
        
        article = result["news"][0]
        assert isinstance(article, News)
        assert article.id == "news_123"
        assert article.headline == "AAPL Reports Strong Quarterly Earnings"
        assert article.summary == "Apple Inc. exceeded analyst expectations..."
        assert article.author == "John Smith"
        assert article.symbols == ["AAPL"]
        assert article.source == "Reuters"
        assert article.url == "https://example.com/news/123"
        assert article.content == "Full article content here..."
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "news" in call_args[1]["url"]
        params = call_args[1]["params"]
        assert params["limit"] == 50  # default limit
        assert params["include_content"] is False  # default
        assert params["sort"] == "desc"  # default

    @patch('alpaca_data.client.requests.request')
    def test_get_news_with_symbols(self, mock_request):
        """Test get_news with symbol filtering."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "news": [
                {
                    "id": "news_456",
                    "headline": "GOOGL Announces New AI Initiative",
                    "created_at": "2024-01-01T14:00:00Z",
                    "symbols": ["GOOGL"],
                    "source": "TechCrunch"
                }
            ],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_news with symbols
        result = client.get_news(symbols=["GOOGL", "AAPL"], limit=10)

        # Verify results
        assert result["count"] == 1
        assert result["symbols"] == ["GOOGL", "AAPL"]
        
        article = result["news"][0]
        assert article.id == "news_456"
        assert article.headline == "GOOGL Announces New AI Initiative"
        assert article.symbols == ["GOOGL"]
        
        # Verify API call with symbols parameter
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert "GOOGL,AAPL" in params["symbols"]
        assert params["limit"] == 10

    @patch('alpaca_data.client.requests.request')
    def test_get_news_with_date_range(self, mock_request):
        """Test get_news with date range parameters."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "news": [],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_news with date range
        result = client.get_news(
            start="2024-01-01T00:00:00-05:00",
            end="2024-01-02T00:00:00-05:00",
            include_content=True,
            sort="asc"
        )

        # Verify result structure
        assert result["count"] == 0
        assert result["start"] == "2024-01-01T00:00:00-05:00"
        assert result["end"] == "2024-01-02T00:00:00-05:00"
        
        # Verify API call parameters
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["start"] == "2024-01-01T00:00:00-05:00"
        assert params["end"] == "2024-01-02T00:00:00-05:00"
        assert params["include_content"] is True
        assert params["sort"] == "asc"

    @patch('alpaca_data.client.requests.request')
    def test_get_news_pagination(self, mock_request):
        """Test get_news with pagination."""
        # Mock response with next page token
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "news": [
                {
                    "id": "news_789",
                    "headline": "MSFT Cloud Revenue Grows",
                    "created_at": "2024-01-01T13:00:00Z",
                    "symbols": ["MSFT"],
                    "source": "Bloomberg"
                }
            ],
            "next_page_token": "next_page_token_abc"
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_news
        result = client.get_news()

        # Verify pagination info
        assert result["count"] == 1
        assert result["has_next_page"] is True
        assert result["next_page_token"] == "next_page_token_abc"

    @patch('alpaca_data.client.requests.request')
    def test_get_news_with_page_token(self, mock_request):
        """Test get_news with page token (ignores other params)."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "news": [],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_news with page token
        result = client.get_news(
            symbols=["AAPL"],
            start="2024-01-01",
            end="2024-01-02",
            page_token="existing_token"
        )

        # Verify API call includes page token
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["page_token"] == "existing_token"

    @patch('alpaca_data.client.requests.request')
    def test_get_news_multiple_articles(self, mock_request):
        """Test get_news with multiple articles."""
        # Mock successful response with multiple articles
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "news": [
                {
                    "id": "news_1",
                    "headline": "Tech Stocks Rally",
                    "created_at": "2024-01-01T12:00:00Z",
                    "symbols": ["AAPL", "GOOGL", "MSFT"],
                    "source": "CNBC"
                },
                {
                    "id": "news_2",
                    "headline": "Market Analysis: Q4 Earnings Preview",
                    "created_at": "2024-01-01T11:00:00Z",
                    "symbols": ["SPY", "QQQ"],
                    "source": "MarketWatch"
                }
            ],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_news
        result = client.get_news(limit=20)

        # Verify results
        assert result["count"] == 2
        assert len(result["news"]) == 2
        
        # Verify first article
        article1 = result["news"][0]
        assert article1.id == "news_1"
        assert article1.headline == "Tech Stocks Rally"
        assert article1.symbols == ["AAPL", "GOOGL", "MSFT"]
        
        # Verify second article
        article2 = result["news"][1]
        assert article2.id == "news_2"
        assert article2.headline == "Market Analysis: Q4 Earnings Preview"
        assert article2.symbols == ["SPY", "QQQ"]

    def test_news_from_dict_full_data(self):
        """Test News.from_dict with complete data."""
        news_data = {
            "id": "news_123",
            "headline": "Breaking: Major Company Acquisition Announced",
            "summary": "In a surprising move, Company X announced the acquisition of...",
            "author": "Jane Doe",
            "created_at": "2024-01-01T15:30:00Z",
            "updated_at": "2024-01-01T16:00:00Z",
            "url": "https://example.com/news/123",
            "content": "Full article content with all the details about the acquisition...",
            "symbols": ["AAPL", "MSFT"],
            "source": "Financial Times"
        }
        
        article = News.from_dict(news_data)
        
        assert article.id == "news_123"
        assert article.headline == "Breaking: Major Company Acquisition Announced"
        assert article.summary == "In a surprising move, Company X announced the acquisition of..."
        assert article.author == "Jane Doe"
        assert article.url == "https://example.com/news/123"
        assert article.content == "Full article content with all the details about the acquisition..."
        assert article.symbols == ["AAPL", "MSFT"]
        assert article.source == "Financial Times"
        # Verify timestamps are parsed correctly
        assert article.created_at.year == 2024
        assert article.updated_at is not None

    def test_news_from_dict_minimal_data(self):
        """Test News.from_dict with minimal required data."""
        news_data = {
            "id": "news_456",
            "headline": "Stock Price Update",
            "created_at": "2024-01-01T10:00:00Z",
            "symbols": ["AAPL"],
            "source": "Reuters"
        }
        
        article = News.from_dict(news_data)
        
        assert article.id == "news_456"
        assert article.headline == "Stock Price Update"
        assert article.symbols == ["AAPL"]
        assert article.source == "Reuters"
        # Optional fields should be None
        assert article.summary is None
        assert article.author is None
        assert article.updated_at is None
        assert article.url is None
        assert article.content is None

    def test_news_from_dict_no_updated_at(self):
        """Test News.from_dict when updated_at is not provided."""
        news_data = {
            "id": "news_789",
            "headline": "Market Opens Lower",
            "created_at": "2024-01-01T09:30:00Z",
            "symbols": ["SPY"],
            "source": "Associated Press"
        }
        
        article = News.from_dict(news_data)
        
        assert article.id == "news_789"
        assert article.headline == "Market Opens Lower"
        assert article.created_at is not None
        assert article.updated_at is None  # Should handle missing updated_at

    def test_news_multiple_symbols(self):
        """Test News.from_dict with multiple symbols."""
        news_data = {
            "id": "multi_123",
            "headline": "Tech Sector Shows Mixed Results",
            "created_at": "2024-01-01T14:15:00Z",
            "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
            "source": "TechCrunch"
        }
        
        article = News.from_dict(news_data)
        
        assert article.symbols == ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        assert len(article.symbols) == 5