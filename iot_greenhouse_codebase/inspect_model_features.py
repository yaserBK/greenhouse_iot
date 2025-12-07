import joblib
import json

# Load the model
model = joblib.load("gam_model.pkl")

print("\n=== MODEL TYPE ===")
print(type(model))

# Try to load features.json (this is often the ground truth)
try:
    with open("features.json") as f:
        feats = json.load(f)
    print("\n=== FEATURES FROM features.json (most important) ===")
    for f in feats:
        print(" -", f)
except FileNotFoundError:
    print("\nNo features.json found next to the model.")

# pyGAM only stores number of features, not names
if hasattr(model, "m_features"):
    print("\npyGAM says num features:", model.m_features)

# If sklearn model was involved earlier:
if hasattr(model, "feature_names_in_"):
    print("\n=== SKLEARN feature_names_in_ ===")
    for f in model.feature_names_in_:
        print(" -", f)

