"""Tests for AlpacaClient."""

import os
import pytest
from alpaca_data import AlpacaClient
from alpaca_data.exceptions import AlpacaAuthError


class TestAlpacaClient:
    """Test cases for AlpacaClient."""

    def test_client_initialization_with_credentials(self):
        """Test client can be initialized with explicit credentials."""
        client = AlpacaClient(
            api_key="test_api_key",
            secret_key="test_secret_key",
            base_url="https://paper-api.alpaca.markets",
        )
        assert client.api_key == "test_api_key"
        assert client.secret_key == "test_secret_key"
        assert client.base_url == "https://paper-api.alpaca.markets"

    def test_client_initialization_with_env_vars(self, monkeypatch):
        """Test client can be initialized from environment variables."""
        monkeypatch.setenv("ALPACA_API_KEY", "env_api_key")
        monkeypatch.setenv("ALPACA_API_SECRET", "env_secret_key")
        monkeypatch.setenv("ALPACA_BASE_URL", "https://api.alpaca.markets")

        client = AlpacaClient()
        assert client.api_key == "env_api_key"
        assert client.secret_key == "env_secret_key"
        assert client.base_url == "https://api.alpaca.markets"

    def test_client_initialization_without_credentials_raises_error(self, monkeypatch):
        """Test client raises error when credentials are not provided."""
        monkeypatch.delenv("ALPACA_API_KEY", raising=False)
        monkeypatch.delenv("ALPACA_SECRET_KEY", raising=False)

        with pytest.raises(ValueError, match="API credentials required"):
            AlpacaClient()

    def test_default_base_url_is_paper(self, monkeypatch):
        """Test that default base URL is paper trading."""
        monkeypatch.setenv("ALPACA_API_KEY", "test_key")
        monkeypatch.setenv("ALPACA_SECRET_KEY", "test_secret")
        monkeypatch.delenv("ALPACA_BASE_URL", raising=False)

        client = AlpacaClient()
        assert client.base_url == "https://paper-api.alpaca.markets"
