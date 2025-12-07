import joblib
import json
import numpy as np
import os

# Load model and features
MODEL_PATH = os.path.join(os.path.dirname(__file__), "gam_model.pkl")
FEATURE_PATH = os.path.join(os.path.dirname(__file__), "features.json")

gam_model = joblib.load(MODEL_PATH)

with open(FEATURE_PATH, "r") as f:
    feature_list = json.load(f)

def predict(sample_dict):
    """
    Azure-ready prediction function.

    sample_dict: a dictionary mapping feature names to values.
                 Example:
                     {
                       "Tair_mean": 20.1,
                       "Rhair_mean": 80.4,
                       "CO2air_mean": 650,
                       ...
                     }
    Returns: float predicted scalarized utility
    """

    # Convert dict → feature vector in correct order
    x = np.array([[sample_dict[f] for f in feature_list]], dtype=float)

    pred = gam_model.predict(x)[0]
    return float(pred)
