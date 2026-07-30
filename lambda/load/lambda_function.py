import json
import os
import boto3
import pymysql

s3 = boto3.client("s3")

PROCESSED_BUCKET = "yashashwani-stockmarket-processed"

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_PORT = int(os.environ["DB_PORT"])


def get_latest_processed_file():
    response = s3.list_objects_v2(
        Bucket=PROCESSED_BUCKET,
        Prefix="processed/"
    )

    files = response.get("Contents", [])

    if not files:
        raise Exception("No processed stock files found in S3")

    latest_file = max(
        files,
        key=lambda x: x["LastModified"]
    )

    return latest_file["Key"]


def read_processed_data(file_key):
    response = s3.get_object(
        Bucket=PROCESSED_BUCKET,
        Key=file_key
    )

    data = response["Body"].read().decode("utf-8")

    return json.loads(data)


def insert_into_rds(stocks):
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

    cursor = connection.cursor()

    sql = """
    INSERT INTO stock_data
    (
        symbol,
        company_name,
        current_price,
        previous_close,
        price_change,
        change_percent,
        volume,
        currency,
        market_time,
        processed_at
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    for stock in stocks:
        cursor.execute(sql, (
            stock.get("symbol"),
            stock.get("company_name"),
            stock.get("current_price"),
            stock.get("previous_close"),
            stock.get("price_change"),
            stock.get("change_percent"),
            stock.get("volume"),
            stock.get("currency"),
            stock.get("market_time"),
            stock.get("processed_at")
        ))

    connection.commit()
    cursor.close()
    connection.close()


def lambda_handler(event, context):

    latest_file = get_latest_processed_file()

    stocks = read_processed_data(latest_file)

    insert_into_rds(stocks)

    return {
        "statusCode": 200,
        "source_file": latest_file,
        "records_inserted": len(stocks),
        "message": "Stock data inserted into RDS successfully"
    }