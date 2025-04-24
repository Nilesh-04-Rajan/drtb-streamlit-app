from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd

# Initialize app
app = Flask(__name__)
CORS(app)

# Load your trained model pipeline
with open("model_rf_pipeline.pkl", "rb") as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return "DR-TB Model API is running! Use POST "


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        input_df = pd.DataFrame([data])

        prediction = model.predict(input_df)[0]
        result = "Resistant" if prediction == 1 else "Sensitive"

        return jsonify({
            "prediction": int(prediction),
            "result": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
