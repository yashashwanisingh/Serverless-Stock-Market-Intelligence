import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# File paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "stock_data_clean.csv"
OUTPUT_FILE = BASE_DIR / "anomaly_results.csv"

# Load cleaned stock data
df = pd.read_csv(INPUT_FILE)

# Convert features to numeric values
features = ["change_percent", "price_change", "volume"]

for col in features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove missing and invalid feature values
X = df[features].replace([np.inf, -np.inf], np.nan)
valid = X.notna().all(axis=1)

df = df.loc[valid].copy()
X = X.loc[valid].copy()

if len(df) < 10:
    raise ValueError("Not enough valid records for anomaly detection.")

# Statistical method: Z-score on percentage change
mean_change = df["change_percent"].mean()
std_change = df["change_percent"].std(ddof=0)

if std_change == 0 or pd.isna(std_change):
    df["z_score"] = 0.0
else:
    df["z_score"] = (
        df["change_percent"] - mean_change
    ) / std_change

df["z_score_anomaly"] = df["z_score"].abs() >= 2

# Standardize features before Isolation Forest
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Machine-learning method: Isolation Forest
model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

df["iforest_prediction"] = model.fit_predict(X_scaled)
df["iforest_anomaly"] = df["iforest_prediction"] == -1
df["anomaly_score"] = model.decision_function(X_scaled)

# Compare both methods
df["both_methods_flagged"] = (
    df["z_score_anomaly"] & df["iforest_anomaly"]
)

# Sort and save results
df = df.sort_values(
    ["processed_at", "symbol"]
).reset_index(drop=True)

df.to_csv(OUTPUT_FILE, index=False)

print("Anomaly detection completed!")
print("Records analysed:", len(df))
print("Z-score anomalies:", int(df["z_score_anomaly"].sum()))
print("Isolation Forest anomalies:", int(df["iforest_anomaly"].sum()))
print("Flagged by both methods:", int(df["both_methods_flagged"].sum()))
print("Results saved to:", OUTPUT_FILE)

print("\nFlagged records:")

columns = [
    "symbol",
    "processed_at",
    "change_percent",
    "volume",
    "z_score",
    "z_score_anomaly",
    "iforest_anomaly",
]

flagged = df[
    df["z_score_anomaly"] | df["iforest_anomaly"]
]

if flagged.empty:
    print("No records flagged by either method.")
else:
    print(flagged[columns].to_string(index=False))
