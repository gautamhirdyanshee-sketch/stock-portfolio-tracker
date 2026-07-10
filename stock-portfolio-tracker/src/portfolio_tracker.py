"""
Stock Portfolio Tracker - Tracks and analyzes your stock portfolio.
Features:
  - Real-time stock price updates using yfinance
  - Portfolio performance metrics (gains/losses)
  - Data persistence with SQLite
  - Portfolio analysis and visualization
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import yfinance as yf


class PortfolioDatabase:
    """Manages portfolio data persistence using SQLite."""
    
    def __init__(self, db_file: str = "portfolio.db"):
        """Initialize database connection."""
        self.db_file = db_file
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Create necessary database tables."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY,
                    ticker TEXT UNIQUE NOT NULL,
                    quantity INTEGER NOT NULL,
                    purchase_price REAL NOT NULL,
                    purchase_date TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    ticker TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    transaction_date TEXT NOT NULL
                )
            ''')
            conn.commit()
    
    def add_stock(self, ticker: str, quantity: int, purchase_price: float) -> None:
        """Add or update stock in portfolio."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                'SELECT quantity FROM portfolio WHERE ticker = ?', (ticker,)
            )
            existing = cursor.fetchone()
            
            if existing:
                new_quantity = existing[0] + quantity
                cursor.execute(
                    'UPDATE portfolio SET quantity = ?, purchase_price = ?, purchase_date = ? WHERE ticker = ?',
                    (new_quantity, purchase_price, purchase_date, ticker)
                )
            else:
                cursor.execute(
                    'INSERT INTO portfolio (ticker, quantity, purchase_price, purchase_date) VALUES (?, ?, ?, ?)',
                    (ticker, quantity, purchase_price, purchase_date)
                )
            
            # Log transaction
            cursor.execute(
                'INSERT INTO transactions (ticker, quantity, price, transaction_type, transaction_date) VALUES (?, ?, ?, ?, ?)',
                (ticker, quantity, purchase_price, 'BUY', purchase_date)
            )
            conn.commit()
    
    def get_portfolio(self) -> Dict[str, Tuple[int, float]]:
        """Retrieve entire portfolio."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT ticker, quantity, purchase_price FROM portfolio')
            return {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    def remove_stock(self, ticker: str) -> None:
        """Remove stock from portfolio."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM portfolio WHERE ticker = ?', (ticker,))
            conn.commit()
    
    def get_transaction_history(self) -> List[Dict]:
        """Get transaction history."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT ticker, quantity, price, transaction_type, transaction_date FROM transactions ORDER BY transaction_date DESC'
            )
            return [
                {
                    'ticker': row[0],
                    'quantity': row[1],
                    'price': row[2],
                    'type': row[3],
                    'date': row[4]
                }
                for row in cursor.fetchall()
            ]


class StockPriceFetcher:
    """Fetches real-time stock prices using yfinance."""
    
    @staticmethod
    def get_current_price(ticker: str) -> Optional[float]:
        """Fetch current price for a ticker."""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d')
            if data.empty:
                return None
            return float(data['Close'].iloc[-1])
        except Exception as e:
            print(f"❌ Error fetching price for {ticker}: {e}")
            return None
    
    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """Validate if ticker exists."""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period='1d')
            return not data.empty
        except Exception:
            return False


class PortfolioAnalyzer:
    """Analyzes portfolio performance and metrics."""
    
    def __init__(self, portfolio_db: PortfolioDatabase):
        """Initialize analyzer."""
        self.db = portfolio_db
    
    def calculate_total_value(self) -> Tuple[float, Dict[str, float]]:
        """Calculate current portfolio value and individual stock values."""
        portfolio = self.db.get_portfolio()
        total_value = 0.0
        stock_values = {}
        
        for ticker, (quantity, _) in portfolio.items():
            current_price = StockPriceFetcher.get_current_price(ticker)
            if current_price:
                stock_value = quantity * current_price
                stock_values[ticker] = stock_value
                total_value += stock_value
        
        return total_value, stock_values
    
    def calculate_gains_losses(self) -> Tuple[float, float, Dict[str, Tuple[float, float]]]:
        """Calculate total gains/losses and individual stock performance."""
        portfolio = self.db.get_portfolio()
        total_invested = 0.0
        total_current = 0.0
        stock_performance = {}
        
        for ticker, (quantity, purchase_price) in portfolio.items():
            invested = quantity * purchase_price
            total_invested += invested
            
            current_price = StockPriceFetcher.get_current_price(ticker)
            if current_price:
                current_value = quantity * current_price
                total_current += current_value
                gain_loss = current_value - invested
                gain_loss_pct = (gain_loss / invested * 100) if invested > 0 else 0
                stock_performance[ticker] = (gain_loss, gain_loss_pct)
        
        total_gain_loss = total_current - total_invested
        total_gain_loss_pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        return total_gain_loss, total_gain_loss_pct, stock_performance
    
    def get_asset_allocation(self) -> Dict[str, float]:
        """Calculate asset allocation percentages."""
        _, stock_values = self.calculate_total_value()
        total = sum(stock_values.values())
        
        if total == 0:
            return {}
        
        return {ticker: (value / total * 100) for ticker, value in stock_values.items()}


def display_menu() -> str:
    """Display main menu."""
    print("\n" + "="*60)
    print("📊 STOCK PORTFOLIO TRACKER")
    print("="*60)
    print("1. Add stock to portfolio")
    print("2. View portfolio summary")
    print("3. View portfolio performance")
    print("4. View asset allocation")
    print("5. View transaction history")
    print("6. Remove stock")
    print("7. Exit")
    print("="*60)
    return input("Choose an option (1-7): ").strip()


def add_stock(db: PortfolioDatabase) -> None:
    """Add stock to portfolio."""
    ticker = input("Enter stock ticker (e.g., AAPL): ").strip().upper()
    
    if not StockPriceFetcher.validate_ticker(ticker):
        print(f"❌ Invalid ticker '{ticker}'. Please check and try again.")
        return
    
    try:
        quantity = int(input(f"Enter quantity for {ticker}: "))
        if quantity <= 0:
            print("❌ Quantity must be greater than 0.")
            return
    except ValueError:
        print("❌ Invalid input! Please enter a whole number.")
        return
    
    current_price = StockPriceFetcher.get_current_price(ticker)
    if current_price is None:
        print(f"❌ Could not fetch price for {ticker}.")
        return
    
    db.add_stock(ticker, quantity, current_price)
    print(f"✅ Added {quantity} shares of {ticker} at ${current_price:.2f}")


def view_portfolio_summary(db: PortfolioDatabase, analyzer: PortfolioAnalyzer) -> None:
    """Display portfolio summary."""
    portfolio = db.get_portfolio()
    
    if not portfolio:
        print("\n❌ Portfolio is empty.")
        return
    
    print("\n" + "="*80)
    print("📋 PORTFOLIO SUMMARY")
    print("="*80)
    print(f"{'Ticker':<10}{'Quantity':<12}{'Current Price':<16}{'Total Value':<16}")
    print("-"*80)
    
    total_value, stock_values = analyzer.calculate_total_value()
    
    for ticker in sorted(portfolio.keys()):
        quantity = portfolio[ticker][0]
        current_price = StockPriceFetcher.get_current_price(ticker)
        stock_value = stock_values.get(ticker, 0)
        
        if current_price:
            print(f"{ticker:<10}{quantity:<12}${current_price:<15.2f}${stock_value:<15.2f}")
    
    print("-"*80)
    print(f"{'TOTAL PORTFOLIO VALUE:':<38}${total_value:,.2f}")
    print("="*80)


def view_portfolio_performance(db: PortfolioDatabase, analyzer: PortfolioAnalyzer) -> None:
    """Display portfolio performance metrics."""
    portfolio = db.get_portfolio()
    
    if not portfolio:
        print("\n❌ Portfolio is empty.")
        return
    
    total_gain_loss, total_gain_loss_pct, stock_performance = analyzer.calculate_gains_losses()
    
    print("\n" + "="*80)
    print("📈 PORTFOLIO PERFORMANCE")
    print("="*80)
    print(f"{'Ticker':<10}{'Gain/Loss':<16}{'Return %':<12}")
    print("-"*80)
    
    for ticker in sorted(stock_performance.keys()):
        gain_loss, gain_loss_pct = stock_performance[ticker]
        symbol = "📈" if gain_loss >= 0 else "📉"
        print(f"{ticker:<10}${gain_loss:<15.2f}{gain_loss_pct:>10.2f}% {symbol}")
    
    print("-"*80)
    symbol = "📈" if total_gain_loss >= 0 else "📉"
    print(f"{'TOTAL':<10}${total_gain_loss:<15.2f}{total_gain_loss_pct:>10.2f}% {symbol}")
    print("="*80)


def view_asset_allocation(analyzer: PortfolioAnalyzer) -> None:
    """Display asset allocation."""
    allocation = analyzer.get_asset_allocation()
    
    if not allocation:
        print("\n❌ Portfolio is empty.")
        return
    
    print("\n" + "="*60)
    print("🥧 ASSET ALLOCATION")
    print("="*60)
    
    for ticker in sorted(allocation.keys()):
        percentage = allocation[ticker]
        bar_length = int(percentage / 5)
        bar = "█" * bar_length
        print(f"{ticker:<10}{bar:<20}{percentage:>6.2f}%")
    
    print("="*60)


def view_transaction_history(db: PortfolioDatabase) -> None:
    """Display transaction history."""
    history = db.get_transaction_history()
    
    if not history:
        print("\n❌ No transactions found.")
        return
    
    print("\n" + "="*80)
    print("📜 TRANSACTION HISTORY")
    print("="*80)
    print(f"{'Date':<20}{'Ticker':<10}{'Type':<8}{'Qty':<8}{'Price':<12}")
    print("-"*80)
    
    for transaction in history:
        print(f"{transaction['date']:<20}{transaction['ticker']:<10}{transaction['type']:<8}{transaction['quantity']:<8}${transaction['price']:<11.2f}")
    
    print("="*80)


def remove_stock(db: PortfolioDatabase) -> None:
    """Remove stock from portfolio."""
    ticker = input("Enter stock ticker to remove: ").strip().upper()
    portfolio = db.get_portfolio()
    
    if ticker not in portfolio:
        print(f"❌ {ticker} not found in portfolio.")
        return
    
    confirm = input(f"Are you sure you want to remove {ticker}? (y/n): ").strip().lower()
    if confirm == 'y':
        db.remove_stock(ticker)
        print(f"✅ {ticker} removed from portfolio.")
    else:
        print("❌ Operation cancelled.")


def main() -> None:
    """Main application loop."""
    db = PortfolioDatabase()
    analyzer = PortfolioAnalyzer(db)
    
    print("\n🚀 Welcome to Stock Portfolio Tracker!")
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            add_stock(db)
        elif choice == '2':
            view_portfolio_summary(db, analyzer)
        elif choice == '3':
            view_portfolio_performance(db, analyzer)
        elif choice == '4':
            view_asset_allocation(analyzer)
        elif choice == '5':
            view_transaction_history(db)
        elif choice == '6':
            remove_stock(db)
        elif choice == '7':
            print("\n👋 Thank you for using Stock Portfolio Tracker!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
