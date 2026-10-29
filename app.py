import os
import joblib
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load model artifact
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "housing_model.pkl")

def get_model():
    if os.path.exists(MODEL_PATH):
        artifact = joblib.load(MODEL_PATH)
        return artifact["model"], artifact.get("features", ["area", "bedrooms", "bathrooms", "stories", "parking"])
    return None, None

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    input_data = {}
    if request.method == "POST":
        try:
            area = float(request.form.get("area", 1500))
            bedrooms = int(request.form.get("bedrooms", 3))
            bathrooms = int(request.form.get("bathrooms", 2))
            stories = int(request.form.get("stories", 2))
            parking = int(request.form.get("parking", 1))

            input_data = {
                "area": area,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "stories": stories,
                "parking": parking
            }

            model, _ = get_model()
            if model is not None:
                features = np.array([[area, bedrooms, bathrooms, stories, parking]])
                raw_pred = model.predict(features)[0]
                prediction = max(0, round(float(raw_pred), 2))
        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template("index.html", prediction=prediction, input_data=input_data)

@app.route("/health", methods=["GET"])
def health():
    model, _ = get_model()
    status = "healthy" if model is not None else "degraded"
    return jsonify({
        "status": status,
        "service": "housing-price-predictor",
        "model_loaded": model is not None,
        "framework": "scikit-learn + flask"
    }), 200

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    try:
        area = float(data.get("area", 0))
        bedrooms = int(data.get("bedrooms", 1))
        bathrooms = int(data.get("bathrooms", 1))
        stories = int(data.get("stories", 1))
        parking = int(data.get("parking", 0))

        if area <= 0:
            return jsonify({"error": "Area must be greater than zero"}), 400

        model, _ = get_model()
        if model is None:
            return jsonify({"error": "Model artifact not loaded"}), 503

        features = np.array([[area, bedrooms, bathrooms, stories, parking]])
        predicted_price = float(model.predict(features)[0])
        return jsonify({
            "estimated_price": round(predicted_price, 2),
            "currency": "USD",
            "features_used": {
                "area": area,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "stories": stories,
                "parking": parking
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

