import json
import boto3
import yfinance as yf
from datetime import datetime

RAW_BUCKET = "YOUR_BUCKET_NAME"

s3 = boto3.client("s3")

STOCKS = [
    # 🇮🇳 Indian Stocks
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "AXISBANK.NS",
    "KOTAKBANK.NS",
    "WIPRO.NS",
    "HCLTECH.NS",
    "TECHM.NS",
    "TATASTEEL.NS",
    "MARUTI.NS",
    "M&M.NS",
    "LT.NS",
    "ITC.NS",
    "BHARTIARTL.NS",
    "SUNPHARMA.NS",
    "DRREDDY.NS",
    "NTPC.NS",
    "POWERGRID.NS",
    "ONGC.NS",
    "COALINDIA.NS",
    "ASIANPAINT.NS",

    # 🇺🇸 US / Global Tech Stocks
    "GOOGL",     # Alphabet (Google)
    "META",      # Meta
    "AAPL",      # Apple
    "MSFT",      # Microsoft
    "AMZN"       # Amazon
]

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info

    return {
        "symbol": symbol,
        "company_name": info.get("longName"),
        "current_price": info.get("currentPrice"),
        "previous_close": info.get("previousClose"),
        "open_price": info.get("open"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "volume": info.get("volume"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "dividend_yield": info.get("dividendYield"),
        "week_52_high": info.get("fiftyTwoWeekHigh"),
        "week_52_low": info.get("fiftyTwoWeekLow"),
        "currency": info.get("currency"),
        "exchange": info.get("exchange")
    }

def lambda_handler(event, context):
    stocks_data = []

    for symbol in STOCKS:
        try:
            stock = get_stock_data(symbol)
            stocks_data.append(stock)
        except Exception as e:
            print(f"Error fetching {symbol}: {str(e)}")

    # Save raw stock data to S3
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"raw/stock_data_{timestamp}.json"

    s3.put_object(
        Bucket=RAW_BUCKET,
        Key=file_name,
        Body=json.dumps(stocks_data, default=str),
        ContentType="application/json"
    )

    return {
        "statusCode": 200,
        "stocks_fetched": len(stocks_data),
        "s3_file": file_name,
        "body": json.dumps(stocks_data, default=str)
    }