import joblib
import json

model_path = "gam_model.pkl"
features_path = "features.json"   # if you saved features via your earlier code

model = joblib.load(model_path)
print("Loaded model:", type(model))

# --------------------------------------------------
# 1. If you saved features.json earlier
# --------------------------------------------------
try:
    with open(features_path, "r") as f:
        features = json.load(f)
    print("\nFEATURES LOADED FROM features.json:")
    for f in features:
        print(" -", f)
except Exception:
    print("\nNo features.json found.")

# --------------------------------------------------
# 2. pyGAM models store feature count here:
# --------------------------------------------------
try:
    print("\npyGAM Feature Count:", model.m_features)
except Exception:
    pass

# --------------------------------------------------
# 3. If the model is sklearn-based
# --------------------------------------------------
if hasattr(model, "feature_names_in_"):
    print("\nsklearn feature names:")
    for f in model.feature_names_in_:
        print(" -", f)

# --------------------------------------------------
# 4. If you stored model metadata inside the pickle
# --------------------------------------------------
if hasattr(model, "feature_names"):
    print("\nCustom attribute 'feature_names':")
    print(model.feature_names)

print("\nDone.")

