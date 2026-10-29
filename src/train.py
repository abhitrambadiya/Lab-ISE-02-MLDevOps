import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def generate_synthetic_housing_data(n_samples=500, random_state=42):
    """
    Generates realistic housing price dataset (Kaggle Housing schema benchmark)
    Features:
      - area: Square feet (500 to 5000)
      - bedrooms: 1 to 5
      - bathrooms: 1 to 4
      - stories: 1 to 4
      - parking: 0 to 3
    Target:
      - price: Continuous property value in USD / INR
    """
    np.random.seed(random_state)
    area = np.random.randint(600, 4500, size=n_samples)
    bedrooms = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.25, 0.4, 0.2, 0.05], size=n_samples)
    bathrooms = np.random.choice([1, 2, 3, 4], p=[0.35, 0.45, 0.15, 0.05], size=n_samples)
    stories = np.random.choice([1, 2, 3, 4], p=[0.4, 0.4, 0.15, 0.05], size=n_samples)
    parking = np.random.choice([0, 1, 2, 3], p=[0.25, 0.45, 0.25, 0.05], size=n_samples)

    # Price generation formula with realistic market weights and Gaussian variance
    base_price = 25000
    price = (
        base_price
        + (area * 85.0)
        + (bedrooms * 12000.0)
        + (bathrooms * 22000.0)
        + (stories * 15000.0)
        + (parking * 8000.0)
        + np.random.normal(0, 15000, size=n_samples)
    )

    df = pd.DataFrame({
        "area": area,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "stories": stories,
        "parking": parking,
        "price": np.round(price, 2)
    })
    return df

def train_and_save_model(data_path="data/housing.csv", model_dir="models"):
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)

    df = generate_synthetic_housing_data()
    df.to_csv(data_path, index=False)
    print(f"[INFO] Dataset saved to {data_path} with {len(df)} records.")

    features = ["area", "bedrooms", "bathrooms", "stories", "parking"]
    X = df[features]
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))

    print(f"[SUCCESS] Model trained. R^2 Score: {r2:.4f}, RMSE: ${rmse:,.2f}")

    model_path = os.path.join(model_dir, "housing_model.pkl")
    joblib.dump({"model": model, "features": features, "r2_score": r2, "rmse": rmse}, model_path)
    print(f"[SUCCESS] Model artifact serialized to {model_path}")
    return model_path

if __name__ == "__main__":
    train_and_save_model()

