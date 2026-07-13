import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Dataset Path
current_dir = os.path.dirname(os.path.abspath(__file__))

dataset_path = os.path.join(
    current_dir,
    "..",
    "dataset",
    "Crop_recommendation.csv"
)

# Load Dataset
df = pd.read_csv(dataset_path)

# Features
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]

# Target
y = df['label']

# Split Dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create Model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train Model
model.fit(X_train, y_train)

# Prediction
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", round(accuracy * 100, 2), "%")

# Save Model
model_path = os.path.join(current_dir, "crop_model.pkl")

joblib.dump(model, model_path)

print("Model Saved Successfully!")
print("Location:", model_path)