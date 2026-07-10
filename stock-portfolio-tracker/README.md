# 📊 Stock Portfolio Tracker

A professional Python application for tracking and analyzing your stock portfolio with real-time data, performance metrics, and database persistence.

## ✨ Features

- **Real-Time Stock Data**: Fetch current stock prices using Yahoo Finance API
- **Portfolio Management**: Add, remove, and track multiple stocks
- **Performance Metrics**: Calculate gains/losses and return percentages
- **Asset Allocation**: View portfolio composition and diversification
- **Transaction History**: Track all buy/sell transactions with timestamps
- **Data Persistence**: All portfolio data stored in SQLite database
- **Professional CLI**: User-friendly command-line interface
- **Type Hints**: Full type annotations for better code quality

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Navigate to project directory**
   ```bash
   cd stock-portfolio-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python src/portfolio_tracker.py
   ```

## 📖 Usage

### Main Menu Options

```
1. Add stock to portfolio
   - Enter stock ticker (e.g., AAPL)
   - Current price fetched automatically
   - Add desired quantity

2. View portfolio summary
   - See all holdings with current values
   - Total portfolio value displayed

3. View portfolio performance
   - Track gains/losses per stock
   - Percentage returns calculated
   - Overall portfolio performance

4. View asset allocation
   - Visual representation of portfolio composition
   - Percentage allocation per stock

5. View transaction history
   - Complete record of all transactions
   - Timestamps and prices logged

6. Remove stock
   - Delete stock from portfolio
   - Requires confirmation

7. Exit
   - Close application
```

## 💾 Data Storage

- All data stored in `portfolio.db` (SQLite)
- Database created automatically on first run
- Tables: `portfolio`, `transactions`

### Portfolio Table
| Column | Type | Description |
|--------|------|-------------|
| ticker | TEXT | Stock symbol |
| quantity | INTEGER | Number of shares |
| purchase_price | REAL | Price per share |
| purchase_date | TEXT | When purchased |

### Transactions Table
| Column | Type | Description |
|--------|------|-------------|
| ticker | TEXT | Stock symbol |
| quantity | INTEGER | Number of shares |
| price | REAL | Price per share |
| transaction_type | TEXT | BUY/SELL |
| transaction_date | TEXT | When transacted |

## 📈 Example Usage

```python
# Add Apple stock
Enter stock ticker: AAPL
Enter quantity: 10

# Add Google stock
Enter stock ticker: GOOGL
Enter quantity: 5

# View portfolio
Portfolio Summary:
- AAPL: 10 shares @ $180.00 = $1,800.00
- GOOGL: 5 shares @ $175.50 = $877.50
Total: $2,677.50

# View performance
- AAPL: +$50.00 gain (2.86% return)
- GOOGL: -$25.00 loss (-2.78% return)
Total: +$25.00 (0.94% return)

# Asset allocation
- AAPL: 67.21%
- GOOGL: 32.79%
```

## 🧪 Testing

Run unit tests to verify functionality:

```bash
pytest tests/test_portfolio.py -v
```

Test coverage:
- Database operations (add, retrieve, delete)
- Stock price validation and fetching
- Portfolio calculations
- Asset allocation
- Performance metrics

## 📊 Architecture

### Classes

#### PortfolioDatabase
- Manages SQLite database operations
- Methods: `add_stock()`, `get_portfolio()`, `remove_stock()`, `get_transaction_history()`

#### StockPriceFetcher
- Fetches real-time stock data from Yahoo Finance
- Methods: `get_current_price()`, `validate_ticker()`

#### PortfolioAnalyzer
- Calculates portfolio metrics
- Methods: `calculate_total_value()`, `calculate_gains_losses()`, `get_asset_allocation()`

## 🔧 Technical Details

- **Language**: Python 3.8+
- **Database**: SQLite3
- **API**: yfinance (Yahoo Finance)
- **Testing**: pytest
- **Type Checking**: Full type hints included

## 📦 Dependencies

```
yfinance==0.2.32
pytest==7.4.3
pytest-cov==4.1.0
```

## 🛠️ Troubleshooting

### Issue: "Invalid ticker"
- **Solution**: Verify ticker symbol is correct (e.g., AAPL not APPLE)

### Issue: "Could not fetch price"
- **Solution**: Check internet connection, Yahoo Finance API might be temporarily unavailable

### Issue: Database locked
- **Solution**: Ensure only one instance of the application is running

## 🎯 Future Enhancements

- [ ] Web dashboard with Plotly visualizations
- [ ] Export portfolio to CSV/PDF
- [ ] Dividend tracking
- [ ] Cost basis calculations
- [ ] Tax loss harvesting analysis
- [ ] Real-time alerts for price changes
- [ ] Portfolio rebalancing recommendations

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💼 Author

Created as an internship project to demonstrate:
- Object-oriented programming
- Database management
- API integration
- Financial data analysis
- Professional code practices

---

**Happy investing! 📈**
