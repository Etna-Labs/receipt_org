import yfinance as yf
import pandas as pd
import ta
from typing import Optional, Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_stock_data(data: pd.DataFrame) -> bool:
    """
    Validate that the DataFrame contains required columns and is not empty.
    
    Args:
        data (pd.DataFrame): Stock data DataFrame to validate
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    # Check if DataFrame is empty
    if data.empty:
        logger.error("Received empty DataFrame")
        return False
        
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return False
        
    # Check for null values
    null_counts = data[required_columns].isnull().sum()
    if null_counts.any():
        logger.warning(f"Found null values in columns: \n{null_counts[null_counts > 0]}")
        
    return True

def fetch_historical_data(
    ticker_symbol: str,
    period: str = "1y",
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Fetch historical market data for a given ticker symbol.
    
    Args:
        ticker_symbol (str): Stock ticker symbol
        period (str): Data period to fetch (default: "1y")
                     Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        interval (str): Data interval (default: "1d")
                       Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                       
    Returns:
        Optional[pd.DataFrame]: DataFrame with columns: Open, High, Low, Close, Volume
                              Returns None if data fetch fails
    """
    try:
        logger.info(f"Fetching historical data for {ticker_symbol}")
        stock_data = yf.download(
            ticker_symbol,
            period=period,
            interval=interval,
            progress=False
        )
        
        # Handle multi-index columns if present
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.get_level_values(0)
        
        if validate_stock_data(stock_data):
            logger.info(f"Successfully fetched data for {ticker_symbol}")
            return stock_data
        return None
        
    except Exception as e:
        logger.error(f"Error fetching data for {ticker_symbol}: {str(e)}")
        return None

def get_latest_price_info(ticker_symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get the latest available price information for a ticker.
    
    Args:
        ticker_symbol (str): Stock ticker symbol
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing latest price information
                                Returns None if data fetch fails
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        return {
            'symbol': ticker_symbol,
            'current_price': info.get('currentPrice'),
            'previous_close': info.get('previousClose'),
            'open': info.get('open'),
            'day_high': info.get('dayHigh'),
            'day_low': info.get('dayLow'),
            'volume': info.get('volume')
        }
    except Exception as e:
        logger.error(f"Error fetching latest price info for {ticker_symbol}: {str(e)}")
        return None

def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for the given stock data.
    
    Args:
        data (pd.DataFrame): Stock price data with OHLCV columns
        
    Returns:
        pd.DataFrame: Original data with additional technical indicator columns
    """
    if data.empty:
        logger.error("Cannot calculate indicators on empty DataFrame")
        return data
        
    try:
        # RSI (14-period)
        data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
        
        # MACD (12, 26, 9)
        data['MACD'] = ta.trend.macd(data['Close'])
        data['MACD_Signal'] = ta.trend.macd_signal(data['Close'])
        data['MACD_Hist'] = ta.trend.macd_diff(data['Close'])
        
        # Simple Moving Averages
        data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
        data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
        
        # Bollinger Bands (20-period, 2 standard deviations)
        data['BB_Upper'] = ta.volatility.bollinger_hband(data['Close'])
        data['BB_Middle'] = ta.volatility.bollinger_mavg(data['Close'])
        data['BB_Lower'] = ta.volatility.bollinger_lband(data['Close'])
        
        # Average True Range (14-period)
        data['ATR'] = ta.volatility.average_true_range(data['High'], data['Low'], data['Close'])
        
        logger.info("Successfully calculated technical indicators")
        return data
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        return data

def test_fetcher():
    """
    Test the data fetcher with a sample ticker.
    """
    test_ticker = "AAPL"
    logger.info(f"Testing data fetcher with {test_ticker}")
    
    # Test historical data
    hist_data = fetch_historical_data(test_ticker, period="1mo")
    if hist_data is not None:
        logger.info(f"Successfully fetched historical data for {test_ticker}")
        
        # Calculate technical indicators
        hist_data = calculate_technical_indicators(hist_data)
        
        logger.info(f"Data shape: {hist_data.shape}")
        logger.info(f"Columns: {hist_data.columns.tolist()}")
        logger.info("Technical indicators for latest data:")
        latest_data = hist_data.tail(1)
        for col in ['RSI', 'MACD', 'SMA_20', 'BB_Upper', 'ATR']:
            if col in latest_data.columns:
                logger.info(f"{col}: {latest_data[col].iloc[0]:.2f}")
    
    # Test latest price info
    price_info = get_latest_price_info(test_ticker)
    if price_info is not None:
        logger.info(f"Latest price info for {test_ticker}:")
        for key, value in price_info.items():
            logger.info(f"{key}: {value}")

if __name__ == "__main__":
    test_fetcher()
