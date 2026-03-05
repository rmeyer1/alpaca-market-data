"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set mock environment variables."""
    monkeypatch.setenv("ALPACA_API_KEY", "test_api_key")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    monkeypatch.setenv("ALPACA_DATA_FEED", "iex")
