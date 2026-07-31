CREATE DATABASE IF NOT EXISTS stock_market;

USE stock_market;

CREATE TABLE IF NOT EXISTS stock_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(100),
    current_price DECIMAL(10,2),
    previous_close DECIMAL(10,2),
    price_change DECIMAL(10,2),
    change_percent DECIMAL(10,2),
    volume BIGINT,
    currency VARCHAR(10),
    market_time DATETIME,
    processed_at DATETIME
);