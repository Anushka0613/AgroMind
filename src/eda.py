"""
eda.py
-------
Quick exploratory data analysis on the crop recommendation dataset.
Generates a correlation heatmap and per-feature boxplots by crop, saved
to models/ (used in the README / report).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "crop_recommendation.csv"
OUT_DIR = BASE_DIR / "models"

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def main():
    df = pd.read_csv(DATA_PATH)

    # Correlation heatmap
    plt.figure(figsize=(7, 6))
    corr = df[FEATURES].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="YlGnBu", square=True)
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "correlation_heatmap.png", dpi=150)
    plt.close()

    # Rainfall distribution by a handful of representative crops
    sample_crops = ["rice", "maize", "cotton", "coffee", "grapes", "watermelon"]
    plt.figure(figsize=(9, 5))
    sub = df[df["label"].isin(sample_crops)]
    sns.boxplot(data=sub, x="label", y="rainfall", palette="Set2")
    plt.title("Rainfall Requirement by Crop (sample)")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "rainfall_by_crop.png", dpi=150)
    plt.close()

    print("Saved correlation_heatmap.png and rainfall_by_crop.png to models/")


if __name__ == "__main__":
    main()
