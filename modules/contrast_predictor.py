import os
import numpy as np
import pandas as pd
import joblib

# ================================================
# Different models paths
# ================================================
MODEL_WITH_META = "./prediction_models/model7_lgbm_full_pipeline_dicom_qc_metrics_no_categorical.pkl"
MODEL_NO_META   = "./prediction_models/model4_lgbm_full_pipeline_qc_metrics.pkl"

# Exact metadata fields to check
METADATA_FIELDS = [
    "MagneticFieldStrength",
    "ImagingFrequency",
    "Manufacturer",
    "ManufacturersModelName",
    "BodyPartExamined",
    "MRAcquisitionType",
    "SeriesDescription",
    "ProtocolName",
    "ScanningSequence",
    "SequenceVariant",
    "ScanOptions",
    "SeriesNumber",
    "SliceThickness",
    "SpacingBetweenSlices",
    "EchoTime",
    "RepetitionTime",
    "FlipAngle",
    "EchoTrainLength",
    "PhaseEncodingSteps",
    "AcquisitionMatrixPE",
    "PixelBandwidth",
    "InPlanePhaseEncodingDirectionDICOM",
    "NumberOfAverages",
    "EchoNumber",
    "InversionTime"
]

# ================================================
# Loading and caching models
# ================================================
_cached_models = {}

def _load_model(model_path):
    """Charge le modèle demandé et le met en cache."""
    if model_path in _cached_models:
        return _cached_models[model_path]

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"[ERROR] Modèle introuvable : {model_path}")

    print(f"[ContrastPredictor] Chargement du modèle : {model_path}")
    artifacts = joblib.load(model_path)

    _cached_models[model_path] = {
        "model": artifacts["model"],
        "label_encoder": artifacts.get("label_encoder", None),
        "feature_names": artifacts["feature_names"],
        "categorical_cols": artifacts["categorical_cols"]
    }

    return _cached_models[model_path]

# ================================================
# Choice of model based on metadata presence
# ================================================
def _choose_model(results_dict):
    """Retourne le chemin du bon modèle."""
    has_meta = any(results_dict.get(f) is not None for f in METADATA_FIELDS)
    return MODEL_WITH_META if has_meta else MODEL_NO_META

# ================================================
# Prepare the data for prediction
# ================================================
def _prepare_features(results_dict, feature_names, categorical_cols):
    df = pd.DataFrame([results_dict])
    X = pd.DataFrame()

    for col in feature_names:
        if col in df.columns:
            X[col] = df[col]
        else:
            X[col] = np.nan
            print(f"[WARN] Feature manquante pour le modèle, remplie par NaN : {col}")

    # Categorical
    for col in categorical_cols:
        if col in X.columns:
            X[col] = X[col].fillna("unknown").astype("category")

    # Numerical
    for col in X.columns:
        if col not in categorical_cols:
            X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    return X

# ================================================
# Principal function
# ================================================
def predict_contrast_from_results(results_dict):
    """
    Selects the right model (with or without metadata),
    prepares the features, then predicts.
    """

    # Choice of model
    model_path = _choose_model(results_dict)
    artifacts = _load_model(model_path)

    model = artifacts["model"]
    label_encoder = artifacts["label_encoder"]
    feature_names = artifacts["feature_names"]
    categorical_cols = artifacts["categorical_cols"]

    # Keep only the features expected by the model
    pred_dict = {k: results_dict.get(k, np.nan) for k in feature_names}

    # Prepare the DataFrame
    X = _prepare_features(pred_dict, feature_names, categorical_cols)

    # Prediction
    pred_label = model.predict(X)

    # Probabilities
    try:
        probs = model.predict_proba(X)[0]
        all_probabilities = {cls: float(prob) for cls, prob in zip(model.classes_, probs)}
        confidence = float(np.max(probs))
    except Exception:
        all_probabilities = None
        confidence = None

    return pred_label, confidence, all_probabilities
