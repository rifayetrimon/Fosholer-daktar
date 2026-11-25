import io
import json
import numpy as np
from pathlib import Path
from PIL import Image
import onnxruntime as ort

_DIR = Path(__file__).parent
_FALLBACK = {"label": "Unknown___Unknown", "confidence": 0.0}

_session = ort.InferenceSession(str(_DIR / "model.onnx"), providers=["CPUExecutionProvider"])
_labels: dict = json.loads((_DIR / "labels.json").read_text())
_INPUT_NAME = _session.get_inputs()[0].name

def _preprocess(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = (arr - 0.5) / 0.5
    return arr.transpose(2, 0, 1)[None]  # (1, 3, 224, 224)

async def classify_disease(image_bytes: bytes) -> dict:
    try:
        pixel_values = _preprocess(image_bytes)
        logits = _session.run(None, {_INPUT_NAME: pixel_values})[0][0]
        idx = int(np.argmax(logits))
        exp = np.exp(logits - np.max(logits))
        confidence = float(exp[idx] / exp.sum())
        label = _labels.get(str(idx), "Unknown___Unknown")
        return {"label": label, "confidence": confidence}
    except Exception:
        return _FALLBACK
