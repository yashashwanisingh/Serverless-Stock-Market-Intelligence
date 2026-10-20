
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "anomaly_results.csv"
OUTPUT_DIR = BASE_DIR / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# Convert anomaly flags to Boolean safely
for col in [
    "z_score_anomaly",
    "iforest_anomaly",
    "both_methods_flagged",
]:
    df[col] = df[col].astype(str).str.lower().eq("true")

# 1. Anomaly counts by detection method
counts = [
    int(df["z_score_anomaly"].sum()),
    int(df["iforest_anomaly"].sum()),
    int(df["both_methods_flagged"].sum()),
]

labels = [
    "Z-score",
    "Isolation Forest",
    "Both methods",
]

plt.figure(figsize=(9, 5))
bars = plt.bar(labels, counts)
plt.title("Stock Market Anomaly Detection: Method Comparison")
plt.ylabel("Number of flagged records")
plt.bar_label(bars, padding=3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "method_comparison.png", dpi=300)
plt.close()

# 2. Percentage change vs volume
plt.figure(figsize=(10, 6))

normal = ~(df["z_score_anomaly"] | df["iforest_anomaly"])
flagged = ~normal

plt.scatter(
    df.loc[normal, "volume"],
    df.loc[normal, "change_percent"],
    label="Not flagged",
    alpha=0.6,
    s=35,
)

plt.scatter(
    df.loc[flagged, "volume"],
    df.loc[flagged, "change_percent"],
    label="Potential anomaly",
    marker="x",
    s=90,
)

plt.axhline(0, linewidth=1)
plt.title("Stock Market Anomalies: Percentage Change vs Volume")
plt.xlabel("Trading volume (shares)")
plt.ylabel("Price change (%)")
plt.legend()
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "percentage_change_anomalies.png",
    dpi=300,
)
plt.close()

# 3. Z-score distribution
plt.figure(figsize=(9, 5))
plt.hist(df["z_score"].dropna(), bins=20, edgecolor="black")
plt.axvline(2, linestyle="--", label="Z-score threshold (+2)")
plt.axvline(-2, linestyle="--", label="Z-score threshold (-2)")
plt.title("Distribution of Stock Percentage-Change Z-scores")
plt.xlabel("Z-score")
plt.ylabel("Number of records")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "z_score_distribution.png", dpi=300)
plt.close()

print("Visualizations created successfully!")
print("Saved in:", OUTPUT_DIR)
print("Files:")
for file in sorted(OUTPUT_DIR.glob("*.png")):
    print("-", file.name)
