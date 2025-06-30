import os
import json
import joblib

def model_fn(model_dir):
    """Load the serialized model from disk."""
    model_path = os.path.join(model_dir, "model.joblib")
    return joblib.load(model_path)

def input_fn(serialized_input_data, content_type):
    """Deserialize JSON input sent via InvokeEndpoint."""
    if content_type == "application/json":
        data = json.loads(serialized_input_data)
        if isinstance(data, str):
            return [data]
        elif isinstance(data, list):
            return data
        elif isinstance(data, dict) and "inputs" in data:
            return data["inputs"] if isinstance(data["inputs"], list) else [data["inputs"]]
    raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    labels = model.predict(input_data).tolist()
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(input_data).max(axis=1).tolist()
        return [{"label": label, "confidence": round(score, 4)} for label, score in zip(labels, probs)]
    else:
        return [{"label": label, "confidence": None} for label in labels]





