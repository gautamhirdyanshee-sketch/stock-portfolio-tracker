"""Unit tests for Stock Portfolio Tracker."""

import pytest
import os
import sqlite3
from src.portfolio_tracker import (
    PortfolioDatabase,
    StockPriceFetcher,
    PortfolioAnalyzer
)


@pytest.fixture
def test_db():
    """Create test database."""
    db_file = "test_portfolio.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    db = PortfolioDatabase(db_file)
    yield db
    
    # Cleanup
    if os.path.exists(db_file):
        os.remove(db_file)


def test_portfolio_database_initialization(test_db):
    """Test database initialization."""
    assert os.path.exists("test_portfolio.db")
    
    with sqlite3.connect("test_portfolio.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='portfolio'")
        assert cursor.fetchone() is not None


def test_add_stock(test_db):
    """Test adding stock to portfolio."""
    test_db.add_stock("AAPL", 10, 150.0)
    portfolio = test_db.get_portfolio()
    
    assert "AAPL" in portfolio
    assert portfolio["AAPL"][0] == 10
    assert portfolio["AAPL"][1] == 150.0


def test_add_multiple_stocks(test_db):
    """Test adding multiple stocks."""
    test_db.add_stock("AAPL", 10, 150.0)
    test_db.add_stock("GOOGL", 5, 100.0)
    test_db.add_stock("MSFT", 8, 300.0)
    
    portfolio = test_db.get_portfolio()
    assert len(portfolio) == 3


def test_update_stock_quantity(test_db):
    """Test updating stock quantity."""
    test_db.add_stock("AAPL", 10, 150.0)
    test_db.add_stock("AAPL", 5, 155.0)
    
    portfolio = test_db.get_portfolio()
    assert portfolio["AAPL"][0] == 15


def test_remove_stock(test_db):
    """Test removing stock from portfolio."""
    test_db.add_stock("AAPL", 10, 150.0)
    test_db.remove_stock("AAPL")
    
    portfolio = test_db.get_portfolio()
    assert "AAPL" not in portfolio


def test_transaction_history(test_db):
    """Test transaction history."""
    test_db.add_stock("AAPL", 10, 150.0)
    test_db.add_stock("GOOGL", 5, 100.0)
    
    history = test_db.get_transaction_history()
    assert len(history) >= 2
    assert history[0]['ticker'] in ['AAPL', 'GOOGL']


def test_validate_ticker():
    """Test ticker validation."""
    # These should be valid tickers
    assert StockPriceFetcher.validate_ticker("AAPL") is True
    
    # Invalid ticker
    assert StockPriceFetcher.validate_ticker("XYZABC123") is False


def test_get_current_price():
    """Test fetching current price."""
    price = StockPriceFetcher.get_current_price("AAPL")
    assert price is not None
    assert price > 0


def test_portfolio_analyzer_calculate_total_value(test_db):
    """Test total portfolio value calculation."""
    test_db.add_stock("AAPL", 10, 150.0)
    analyzer = PortfolioAnalyzer(test_db)
    
    total_value, stock_values = analyzer.calculate_total_value()
    assert "AAPL" in stock_values
    assert stock_values["AAPL"] > 0


def test_portfolio_analyzer_empty_portfolio(test_db):
    """Test analyzer with empty portfolio."""
    analyzer = PortfolioAnalyzer(test_db)
    
    total_value, stock_values = analyzer.calculate_total_value()
    assert total_value == 0.0
    assert len(stock_values) == 0


def test_get_asset_allocation(test_db):
    """Test asset allocation calculation."""
    test_db.add_stock("AAPL", 10, 150.0)
    test_db.add_stock("GOOGL", 5, 100.0)
    
    analyzer = PortfolioAnalyzer(test_db)
    allocation = analyzer.get_asset_allocation()
    
    if allocation:
        total_pct = sum(allocation.values())
        assert abs(total_pct - 100.0) < 1  # Allow small rounding error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
