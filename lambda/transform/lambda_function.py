import json
import boto3
from datetime import datetime

# S3 client
s3 = boto3.client("s3")

# S3 Buckets
RAW_BUCKET = "yashashwani-stockmarket-raw"
PROCESSED_BUCKET = "yashashwani-stockmarket-processed"


# --------------------------------------------------
# Find latest raw stock JSON file
# --------------------------------------------------
def get_latest_raw_file():
    response = s3.list_objects_v2(
        Bucket=RAW_BUCKET,
        Prefix="raw/"
    )

    files = response.get("Contents", [])

    if not files:
        raise Exception("No raw stock files found in S3")

    latest_file = max(
        files,
        key=lambda x: x["LastModified"]
    )

    return latest_file["Key"]


# --------------------------------------------------
# Read raw JSON data from S3
# --------------------------------------------------
def read_raw_data(file_key):
    response = s3.get_object(
        Bucket=RAW_BUCKET,
        Key=file_key
    )

    data = response["Body"].read().decode("utf-8")

    return json.loads(data)


# --------------------------------------------------
# Transform stock data
# --------------------------------------------------
def transform_data(stocks):
    transformed_stocks = []

    for stock in stocks:

        current_price = stock.get("current_price")
        previous_close = stock.get("previous_close")

        # Skip records where required prices are missing
        if current_price is None or previous_close is None:
            continue

        # Calculate price change
        price_change = current_price - previous_close

        # Calculate percentage change
        if previous_close != 0:
            change_percent = (price_change / previous_close) * 100
        else:
            change_percent = 0

        # Preserve original stock fields
        transformed_stock = stock.copy()

        # Add transformed fields
        transformed_stock["price_change"] = round(price_change, 2)
        transformed_stock["change_percent"] = round(change_percent, 2)
        transformed_stock["processed_at"] = datetime.utcnow().isoformat()

        transformed_stocks.append(transformed_stock)

    return transformed_stocks


# --------------------------------------------------
# Save transformed data to Processed S3
# --------------------------------------------------
def save_processed_data(stocks):

    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

    file_key = f"processed/stock_data_{timestamp}.json"

    s3.put_object(
        Bucket=PROCESSED_BUCKET,
        Key=file_key,
        Body=json.dumps(stocks, default=str),
        ContentType="application/json"
    )

    return file_key


# --------------------------------------------------
# Lambda Handler
# --------------------------------------------------
def lambda_handler(event, context):

    # 1. Find latest raw JSON
    latest_file = get_latest_raw_file()

    # 2. Read raw data
    raw_stocks = read_raw_data(latest_file)

    # 3. Transform data
    transformed_stocks = transform_data(raw_stocks)

    # 4. Save transformed data
    processed_file = save_processed_data(transformed_stocks)

    # 5. Return execution result
    return {
        "statusCode": 200,
        "source_file": latest_file,
        "processed_file": processed_file,
        "raw_records": len(raw_stocks),
        "transformed_records": len(transformed_stocks),
        "message": "Stock data transformed and saved successfully"
    }