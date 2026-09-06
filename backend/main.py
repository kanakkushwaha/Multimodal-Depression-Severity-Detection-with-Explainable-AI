"""
moodcompiler — Production FastAPI Backend with Real Trained ML Multimodal Pipeline
"Behind Every Signal, There's a Story."

Authors: Kanak Kushwaha, Sahil Tiwari, Aayush Kate
Guide  : Dr. Roshani Raut
Dept   : Information Technology, PCCoE Pune
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from models.fusion import predict_multimodal, load_models

# ── App Initialization ───────────────────────────────────────────────────────
app = FastAPI(
    title="moodcompiler API",
    description="Multimodal Depression Severity Assessment with Trained NLP + Wearable ML Models and XAI Attributions",
    version="2.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Warm up models on startup
@app.on_event("startup")
def startup_event():
    try:
        load_models()
        print("[OK] Real ML Models (NLP + Wearable) loaded into memory.")
    except Exception as e:
        print(f"[WARN] Error loading models at startup: {e}")


# ── Input & Output Schemas ───────────────────────────────────────────────────
class AssessmentInput(BaseModel):
    text:              str             = ""
    heart_rate:        Optional[float] = 74.0
    hrv:               Optional[float] = 40.0
    eda:               Optional[float] = 4.0
    skin_temp:         Optional[float] = 33.5
    respiration_rate:  Optional[float] = 16.0
    sleep_duration:    Optional[float] = 7.0
    daily_steps:       Optional[float] = 5500
    sedentary_hours:   Optional[float] = 8.0
    age:               Optional[float] = 32.0


class AssessmentOutput(BaseModel):
    severity:                str
    level:                   int
    composite_score:         float
    color:                   str
    description:             str
    contributions:           Dict[str, int]
    sensor_readings:         Dict[str, Any]
    modality_probabilities:  Optional[Dict[str, Any]] = None


# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "online",
        "project": "moodcompiler",
        "version": "2.0.0",
        "pipeline": "Trained NLP (Reddit) + Wearable ML (XGBoost) + Decision-Level Fusion",
        "tagline": "Behind Every Signal, There's a Story."
    }


@app.post("/predict", response_model=AssessmentOutput)
def predict(data: AssessmentInput):
    """
    Main prediction endpoint.
    Executes real multimodal late fusion using trained scikit-learn & XGBoost pipelines.
    """
    try:
        payload = data.model_dump()
        result = predict_multimodal(payload)
        return AssessmentOutput(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction pipeline error: {str(e)}")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_pipeline": "production-v2 (Real Trained ML)",
        "modalities": ["Linguistic (TF-IDF + Calibrated Linear)", "Physiological/Behavioral (XGBoost)"],
        "endpoints": ["/predict", "/health", "/docs"],
    }
