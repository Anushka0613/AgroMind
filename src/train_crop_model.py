"""
train_crop_model.py
--------------------
Trains a crop recommendation model on soil (N, P, K, pH) and climate
(temperature, humidity, rainfall) data, compares several algorithms,
and saves the best one along with the label encoder and per-crop
nutrient profiles (used later by the fertilizer advisor).

Dataset: Crop_recommendation.csv (2200 rows, 22 crops, 7 features)
Source columns: N, P, K, temperature, humidity, ph, rainfall, label
"""

import json
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                              classification_report, f1_score)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "crop_recommendation.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET = "label"


def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Crops ({df[TARGET].nunique()}): {sorted(df[TARGET].unique())}")
    print(f"Missing values:\n{df.isnull().sum()}")
    return df


def build_nutrient_profiles(df: pd.DataFrame) -> dict:
    """
    Computes the mean & std of every feature per crop. This becomes the
    'ideal growing condition profile' for each crop and is later used by
    the rule-based fertilizer advisor to detect nutrient deficiencies
    without needing a separate (and much smaller / narrower) fertilizer
    dataset.
    """
    profiles = {}
    grouped = df.groupby(TARGET)[FEATURES]
    means = grouped.mean()
    stds = grouped.std()
    for crop in means.index:
        profiles[crop] = {
            "mean": {f: round(float(means.loc[crop, f]), 2) for f in FEATURES},
            "std": {f: round(float(stds.loc[crop, f]), 2) for f in FEATURES},
        }
    return profiles


def compare_models(X_train, X_test, y_train, y_test):
    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "Decision Tree": DecisionTreeClassifier(max_depth=12, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=300, random_state=42),
        "SVM (RBF)": SVC(kernel="rbf", probability=True, random_state=42),
    }
    if HAS_XGB:
        candidates["XGBoost"] = XGBClassifier(
            n_estimators=300, use_label_encoder=False, eval_metric="mlogloss", random_state=42
        )

    results = []
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds, average="weighted")
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, n_jobs=-1)
        results.append({
            "model": name,
            "test_accuracy": round(acc, 4),
            "weighted_f1": round(f1, 4),
            "cv_mean_accuracy": round(cv_scores.mean(), 4),
            "cv_std": round(cv_scores.std(), 4),
        })
        fitted[name] = model
        print(f"{name:22s} | test_acc={acc:.4f} | f1={f1:.4f} | cv_acc={cv_scores.mean():.4f} (+/-{cv_scores.std():.4f})")

    results_df = pd.DataFrame(results).sort_values("test_accuracy", ascending=False)
    return results_df, fitted


def main():
    df = load_data()

    # ---- Nutrient profiles (used later by the fertilizer advisor) ----
    profiles = build_nutrient_profiles(df)
    with open(MODEL_DIR / "crop_nutrient_profiles.json", "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"\nSaved per-crop nutrient profiles -> {MODEL_DIR / 'crop_nutrient_profiles.json'}")

    # ---- Encode target ----
    le = LabelEncoder()
    df["label_enc"] = le.fit_transform(df[TARGET])

    X = df[FEATURES]
    y = df["label_enc"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nComparing algorithms...\n")
    results_df, fitted_models = compare_models(X_train, X_test, y_train, y_test)
    print("\nModel comparison summary:")
    print(results_df.to_string(index=False))
    results_df.to_csv(MODEL_DIR / "model_comparison.csv", index=False)

    best_name = results_df.iloc[0]["model"]
    best_model = fitted_models[best_name]
    print(f"\nBest model: {best_name}")

    # ---- Retrain best model on ALL data for deployment ----
    best_model.fit(X, y)

    # ---- Feature importance (if available) ----
    if hasattr(best_model, "feature_importances_"):
        importances = pd.Series(best_model.feature_importances_, index=FEATURES).sort_values(ascending=False)
        plt.figure(figsize=(7, 4))
        sns.barplot(x=importances.values, y=importances.index, color="#3b7a57")
        plt.title(f"Feature Importance - {best_name}")
        plt.xlabel("Importance")
        plt.tight_layout()
        plt.savefig(MODEL_DIR / "feature_importance.png", dpi=150)
        plt.close()
        print("Saved feature importance plot -> models/feature_importance.png")

    # ---- Confusion matrix on the held-out test set ----
    test_model = fitted_models[best_name]
    preds = test_model.predict(X_test)
    fig, ax = plt.subplots(figsize=(11, 10))
    ConfusionMatrixDisplay.from_predictions(
        y_test, preds, display_labels=le.classes_, xticks_rotation=90, ax=ax, colorbar=False, cmap="Greens"
    )
    plt.title(f"Confusion Matrix - {best_name} (held-out test set)")
    plt.tight_layout()
    plt.savefig(MODEL_DIR / "confusion_matrix.png", dpi=150)
    plt.close()
    print("Saved confusion matrix -> models/confusion_matrix.png")

    print("\nClassification report (held-out test set):")
    print(classification_report(y_test, preds, target_names=le.classes_))

    # ---- Save artifacts ----
    joblib.dump(best_model, MODEL_DIR / "crop_model.pkl")
    joblib.dump(le, MODEL_DIR / "label_encoder.pkl")
    with open(MODEL_DIR / "best_model_name.txt", "w") as f:
        f.write(best_name)

    print(f"\nSaved trained model -> models/crop_model.pkl")
    print(f"Saved label encoder -> models/label_encoder.pkl")


if __name__ == "__main__":
    main()
