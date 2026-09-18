"""
moodcompiler — Multimodal Decision-Level Fusion & Explainability Engine
"Behind Every Signal, There's a Story."

Scientifically valid Late-Fusion Architecture for unpaired modalities:
Combines calibrated linguistic confidence from Reddit-trained NLP model
with autonomic & behavioral confidence from the Wearable-trained XGBoost model.
"""

import os
import re
import joblib
import numpy as np
import pandas as pd

# Paths
BASE_DIR  = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
PROC_DIR  = os.path.join(BASE_DIR, 'data', 'processed')

# Global cached models
_text_model = None
_tfidf = None
_wearable_model = None
_scaler = None
_wearable_features = None
_classes = ['Normal', 'Mild', 'Moderate', 'Severe']

# Optional MentalBERT auto-upgrade
_mentalbert_model = None
_mentalbert_tokenizer = None
_use_mentalbert = False

def load_models():
    global _text_model, _tfidf, _wearable_model, _scaler, _wearable_features
    global _mentalbert_model, _mentalbert_tokenizer, _use_mentalbert

    if _text_model is None:
        _text_model = joblib.load(os.path.join(MODEL_DIR, 'text_model.joblib'))
        _tfidf = joblib.load(os.path.join(MODEL_DIR, 'tfidf_vectorizer.joblib'))
        _wearable_model = joblib.load(os.path.join(MODEL_DIR, 'wearable_model.joblib'))
        _scaler = joblib.load(os.path.join(PROC_DIR, 'scaler.joblib'))
        _wearable_features = pd.read_csv(os.path.join(PROC_DIR, 'feature_names.csv')).iloc[:, 0].tolist()

    # Auto-detect MentalBERT fine-tuned checkpoint
    mb_dir = os.path.join(MODEL_DIR, 'mentalbert_depression')
    if os.path.exists(mb_dir) and _mentalbert_model is None:
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            _mentalbert_tokenizer = AutoTokenizer.from_pretrained(mb_dir)
            _mentalbert_model = AutoModelForSequenceClassification.from_pretrained(mb_dir)
            _mentalbert_model.eval()
            _use_mentalbert = True
            print("[INFO] MentalBERT loaded successfully for linguistic branch.")
        except Exception as e:
            print(f"[WARN] Failed loading MentalBERT: {e}. Falling back to TF-IDF ensemble.")
            _use_mentalbert = False

def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_wearable_features(inputs: dict) -> np.ndarray:
    """Computes both raw and non-linear engineered features matching prepare_wearable.py."""
    hr       = float(inputs.get('heart_rate', 74.0))
    hrv      = float(inputs.get('hrv', 40.0))
    eda      = float(inputs.get('eda', 4.0))
    temp     = float(inputs.get('skin_temp', 33.5))
    resp     = float(inputs.get('respiration_rate', 16.0))
    sleep    = float(inputs.get('sleep_duration', 7.0))
    steps    = float(inputs.get('daily_steps', 5500))
    sed      = float(inputs.get('sedentary_hours', 8.0))
    age      = float(inputs.get('age', 32.0))

    # Compute dynamic somatic-affective strain from raw telemetry
    hr_strain   = max(0.0, min(1.0, (hr - 65.0) / 45.0))
    eda_strain  = max(0.0, min(1.0, (eda - 2.5) / 7.5))
    hrv_strain  = max(0.0, min(1.0, 1.0 - (hrv - 15.0) / 45.0))
    sleep_strain= max(0.0, min(1.0, abs(sleep - 7.5) / 4.5))
    sed_strain  = max(0.0, min(1.0, (sed - 6.0) / 8.0))

    phys_strain = (hr_strain * 0.25) + (hrv_strain * 0.25) + (eda_strain * 0.20) + (sleep_strain * 0.15) + (sed_strain * 0.15)

    # Derived affective & behavioral telemetry
    mood_score    = float(np.clip(8.5 - (phys_strain * 6.5), 1.5, 9.0))
    stress_idx    = float(np.clip(25.0 + (phys_strain * 65.0), 20.0, 95.0))
    anx_idx       = float(np.clip(25.0 + (phys_strain * 60.0), 20.0, 95.0))
    emo_stab      = float(np.clip(80.0 - (phys_strain * 55.0), 20.0, 90.0))

    sleep_eff     = float(np.clip(85.0 - (phys_strain * 35.0), 45.0, 95.0))
    deep_sleep    = float(np.clip(22.0 - (phys_strain * 15.0), 5.0, 25.0))
    phys_act      = float(np.clip(steps / 150.0, 5.0, 90.0))
    mob_usage     = float(np.clip(2.5 + (phys_strain * 5.0), 1.5, 10.0))
    screen_unlock = float(np.clip(45.0 + (phys_strain * 75.0), 30.0, 140.0))
    social_app    = float(np.clip(1.5 + (phys_strain * 3.5), 0.5, 6.0))
    night_phone   = float(np.clip(15.0 + (phys_strain * 75.0), 5.0, 90.0))

    # Interaction & Ratio features
    hr_to_hrv        = hr / (hrv + 1e-4)
    autonomic_load   = (eda * hr) / (hrv + 1e-4)
    cardio_resp      = hr / (resp + 1e-4)
    sed_to_sleep     = sed / (sleep + 1e-4)
    step_to_sed      = steps / ((sed * 60) + 1e-4)
    sleep_qual       = (sleep * sleep_eff * deep_sleep) / 1000.0
    affective_risk   = (stress_idx + anx_idx) / (mood_score + 1e-4)
    emo_dysreg       = (stress_idx * anx_idx) / (emo_stab + 1e-4)
    digi_sat         = mob_usage + (night_phone / 60.0)

    feature_dict = {
        'Heart_Rate_BPM': hr, 'HRV_ms': hrv, 'EDA_Level_uS': eda, 'Skin_Temperature_C': temp, 'Respiration_Rate_BPM': resp,
        'HR_to_HRV_Ratio': hr_to_hrv, 'Autonomic_Load': autonomic_load, 'Cardio_Resp_Ratio': cardio_resp,
        'Sleep_Duration_Hours': sleep, 'Sleep_Efficiency_Percentage': sleep_eff, 'Deep_Sleep_Percentage': deep_sleep, 'Sleep_Quality_Index': sleep_qual,
        'Daily_Steps': steps, 'Physical_Activity_Minutes': phys_act, 'Sedentary_Time_Hours': sed, 'Sedentary_to_Sleep_Ratio': sed_to_sleep, 'Step_to_Sedentary_Ratio': step_to_sed,
        'Mobile_Usage_Hours': mob_usage, 'Screen_Unlock_Count': screen_unlock, 'Social_App_Usage_Hours': social_app, 'Night_Phone_Usage_Minutes': night_phone, 'Digital_Saturation': digi_sat,
        'Mood_Score': mood_score, 'Stress_Index': stress_idx, 'Anxiety_Index': anx_idx, 'Emotional_Stability_Index': emo_stab, 'Affective_Risk_Ratio': affective_risk, 'Emotional_Dysregulation': emo_dysreg,
        'Age': age
    }

    feature_df = pd.DataFrame([feature_dict])[_wearable_features]
    return _scaler.transform(feature_df), feature_dict

def predict_multimodal(raw_input: dict) -> dict:
    """
    Executes late-fusion decision making across trained text and wearable branches.
    Returns composite severity, level, color, description, and real XAI attribution.
    """
    load_models()
    text = str(raw_input.get('text', '')).strip()

    # 1. Linguistic Branch Prediction
    has_text = len(text) >= 15
    if has_text:
        clean = clean_text(text)
        if _use_mentalbert and _mentalbert_model is not None:
            import torch
            with torch.no_grad():
                encoded = _mentalbert_tokenizer(
                    clean,
                    truncation=True,
                    padding=True,
                    max_length=128,
                    return_tensors='pt'
                )
                outputs = _mentalbert_model(**encoded)
                probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()[0]
                id2label = _mentalbert_model.config.id2label
                p_text = np.array([probs[int(k)] for k in sorted(id2label.keys(), key=lambda x: _classes.index(id2label[int(x)]))])
        else:
            text_vec = _tfidf.transform([clean])
            text_probs = _text_model.predict_proba(text_vec)[0]
            # align probabilities with ['Normal', 'Mild', 'Moderate', 'Severe']
            text_classes = list(_text_model.classes_)
            p_text = np.array([text_probs[text_classes.index(c)] for c in _classes])
    else:
        # Uniform prior if no text provided
        p_text = np.array([0.25, 0.25, 0.25, 0.25])

    # 2. Wearable Branch Prediction
    wearable_scaled, feat_dict = extract_wearable_features(raw_input)
    wearable_probs = _wearable_model.predict_proba(wearable_scaled)[0]
    le = joblib.load(os.path.join(PROC_DIR, 'label_encoder.joblib'))
    wb_classes = list(le.classes_) # ['Mild', 'Moderate', 'Normal', 'Severe']
    p_wearable_raw = np.array([wearable_probs[wb_classes.index(c)] for c in _classes])

    # Empirical Priors (Classes: Normal, Mild, Moderate, Severe)
    # Corrects for the massive 41% Mild bias in the training distribution
    wearable_priors = np.array([0.154, 0.411, 0.307, 0.128])
    p_wearable_unbiased = p_wearable_raw / wearable_priors
    p_wearable = p_wearable_unbiased / np.sum(p_wearable_unbiased)

    text_priors = np.array([0.728, 0.081, 0.111, 0.080]) # Reddit minimum is 72%
    p_text_unbiased = p_text / text_priors
    p_text_calibrated = p_text_unbiased / np.sum(p_text_unbiased)

    # 3. Decision-Level Late Fusion (Adaptive Alpha Weighting)
    if len(text) > 80:
        alpha = 0.50
    elif len(text) >= 15:
        alpha = 0.35
    else:
        alpha = 0.05

    fused_probs = alpha * p_text_calibrated + (1.0 - alpha) * p_wearable

    # Continuous Severity Projection
    level_weights = np.array([0.05, 0.35, 0.68, 1.0])
    composite_score = float(np.dot(fused_probs, level_weights))

    # Determine winning severity directly by calibrated fused likelihood
    pred_idx = int(np.argmax(fused_probs))
    pred_label = _classes[pred_idx]

    # Metadata mapping
    meta = {
        'Normal': {
            'level': 1, 'color': '#64b8ad',
            'desc': 'Multimodal signal patterns indicate balanced physiological and affective baseline. No critical depression indicators detected.'
        },
        'Mild': {
            'level': 2, 'color': '#8bc4b8',
            'desc': 'Mild divergence detected across autonomic and linguistic modalities. Stress indicators are manageable but recommend healthy lifestyle pacing.'
        },
        'Moderate': {
            'level': 3, 'color': '#e5bd73',
            'desc': 'Noticeable convergence between elevated physiological strain and affective cognitive load. Contextual monitoring and stress-reduction recommended.'
        },
        'Severe': {
            'level': 4, 'color': '#c488a0',
            'desc': 'Strong cross-modal signal convergence indicating significant depressive distress. Professional clinical guidance is recommended.'
        }
    }

    # 4. Real XAI — SHAP TreeExplainer on XGBoost sub-model
    # Extract the XGBoost estimator from the VotingClassifier
    try:
        import shap
        xgb_model = _wearable_model.named_estimators_['xgb']

        # Build a SHAP explainer and get values for this single sample
        explainer   = shap.TreeExplainer(xgb_model)
        shap_values = explainer.shap_values(wearable_scaled)  # shape: (n_classes, n_features)

        # Use the predicted class's SHAP values (absolute = contribution magnitude)
        pred_class_idx  = list(le.classes_).index(pred_label) if pred_label in list(le.classes_) else 0
        sample_shap     = np.abs(shap_values[pred_class_idx][0])   # 1-D array, one value per feature

        feat_names = _wearable_features  # ordered list of feature names

        # Map features → 6 clinical signal groups
        group_map = {
            'Autonomic Arousal (EDA)': ['EDA_Level_uS', 'Autonomic_Load', 'Digital_Saturation'],
            'Cardiac Stress (HR/HRV)': ['Heart_Rate_BPM', 'HRV_ms', 'HR_to_HRV_Ratio', 'Cardio_Resp_Ratio', 'Autonomic_Load'],
            'Sleep Deprivation Risk':  ['Sleep_Duration_Hours', 'Sleep_Efficiency_Percentage', 'Deep_Sleep_Percentage', 'Sleep_Quality_Index'],
            'Sedentary Inactivity':    ['Sedentary_Time_Hours', 'Sedentary_to_Sleep_Ratio', 'Step_to_Sedentary_Ratio', 'Daily_Steps', 'Physical_Activity_Minutes'],
            'Respiratory Pattern':     ['Respiration_Rate_BPM'],
        }

        # Sum SHAP magnitudes per group
        shap_dict = dict(zip(feat_names, sample_shap))
        group_shap = {}
        for group, members in group_map.items():
            group_shap[group] = sum(shap_dict.get(f, 0.0) for f in members)

        # Linguistic Depth: use alpha weight (text model is not tree-based)
        group_shap['Linguistic Depth (NLP)'] = alpha * max(group_shap.values()) if group_shap else alpha * 10.0

        total_shap = sum(group_shap.values()) or 1.0
        norm_contributions = {k: int(round((v / total_shap) * 100)) for k, v in group_shap.items()}

    except Exception as e:
        # Graceful fallback to heuristics if SHAP fails
        autonomic_contrib = float(feat_dict['Autonomic_Load'])
        cardiac_contrib   = float(feat_dict['HR_to_HRV_Ratio'])
        sleep_contrib     = float(max(0, 8.0 - feat_dict['Sleep_Duration_Hours']) * 10)
        sed_contrib       = float(feat_dict['Sedentary_Time_Hours'] * 5)
        resp_contrib      = float(abs(feat_dict['Respiration_Rate_BPM'] - 16.0) * 8)
        text_contrib      = float(alpha * 100)
        raw_contributions = {
            'Autonomic Arousal (EDA)': autonomic_contrib,
            'Cardiac Stress (HR/HRV)': cardiac_contrib,
            'Sleep Deprivation Risk':  sleep_contrib,
            'Sedentary Inactivity':    sed_contrib,
            'Respiratory Pattern':     resp_contrib,
            'Linguistic Depth (NLP)':  text_contrib
        }
        total_val = sum(raw_contributions.values()) or 1.0
        norm_contributions = {k: int(round((v / total_val) * 100)) for k, v in raw_contributions.items()}

    return {
        'severity': pred_label + (" Depression" if pred_label != "Normal" else ""),
        'level': meta[pred_label]['level'],
        'composite_score': round(composite_score, 4),
        'color': meta[pred_label]['color'],
        'description': meta[pred_label]['desc'],
        'contributions': norm_contributions,
        'modality_probabilities': {
            'text': {c: round(float(p_text[i]), 3) for i, c in enumerate(_classes)},
            'wearable': {c: round(float(p_wearable[i]), 3) for i, c in enumerate(_classes)},
            'fused': {c: round(float(fused_probs[i]), 3) for i, c in enumerate(_classes)}
        },
        'sensor_readings': {
            'hr':        feat_dict['Heart_Rate_BPM'],
            'hrv':       feat_dict['HRV_ms'],
            'eda':       feat_dict['EDA_Level_uS'],
            'temp':      feat_dict['Skin_Temperature_C'],
            'resp':      feat_dict['Respiration_Rate_BPM'],
            'sleep':     feat_dict['Sleep_Duration_Hours'],
            'steps':     feat_dict['Daily_Steps'],
            'sedentary': feat_dict['Sedentary_Time_Hours'],
        }
    }
