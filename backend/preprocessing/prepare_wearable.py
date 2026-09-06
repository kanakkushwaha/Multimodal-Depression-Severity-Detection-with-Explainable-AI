"""
moodcompiler — Wearable Data Preprocessing v2 (Advanced Feature Engineering)
Extracts non-linear bio-signal and behavioral interaction ratios to maximize model accuracy.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'wearable', 'Wearable_Art_Therapy_Depression_Dataset.csv')
OUT_DIR   = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
print(f"Loaded raw dataset: {df.shape}")

# Label mapping: 4 distinct classes
label_map = {
    'Normal':                 'Normal',
    'Mild Depression':        'Mild',
    'Moderate Depression':    'Moderate',
    'Severe Depression':      'Severe',
    'Very Severe Depression': 'Severe',
}
df['label'] = df['Depression_Severity_Level'].map(label_map)

# ── Feature Engineering ──
# 1. Cardiac & Autonomic indices
df['HR_to_HRV_Ratio'] = df['Heart_Rate_BPM'] / (df['HRV_ms'] + 1e-4)
df['Autonomic_Load'] = (df['EDA_Level_uS'] * df['Heart_Rate_BPM']) / (df['HRV_ms'] + 1e-4)
df['Cardio_Resp_Ratio'] = df['Heart_Rate_BPM'] / (df['Respiration_Rate_BPM'] + 1e-4)

# 2. Activity & Rest balance
df['Sedentary_to_Sleep_Ratio'] = df['Sedentary_Time_Hours'] / (df['Sleep_Duration_Hours'] + 1e-4)
df['Step_to_Sedentary_Ratio'] = df['Daily_Steps'] / ((df['Sedentary_Time_Hours'] * 60) + 1e-4)
df['Sleep_Quality_Index'] = (df['Sleep_Duration_Hours'] * df['Sleep_Efficiency_Percentage'] * df['Deep_Sleep_Percentage']) / 1000.0

# 3. Behavioral / Affective Indices
df['Affective_Risk_Ratio'] = (df['Stress_Index'] + df['Anxiety_Index']) / (df['Mood_Score'] + 1e-4)
df['Emotional_Dysregulation'] = (df['Stress_Index'] * df['Anxiety_Index']) / (df['Emotional_Stability_Index'] + 1e-4)
df['Digital_Saturation'] = df['Mobile_Usage_Hours'] + (df['Night_Phone_Usage_Minutes'] / 60.0)

FEATURES = [
    # Physiological
    'Heart_Rate_BPM', 'HRV_ms', 'EDA_Level_uS', 'Skin_Temperature_C', 'Respiration_Rate_BPM',
    'HR_to_HRV_Ratio', 'Autonomic_Load', 'Cardio_Resp_Ratio',
    # Sleep & Activity
    'Sleep_Duration_Hours', 'Sleep_Efficiency_Percentage', 'Deep_Sleep_Percentage', 'Sleep_Quality_Index',
    'Daily_Steps', 'Physical_Activity_Minutes', 'Sedentary_Time_Hours', 'Sedentary_to_Sleep_Ratio', 'Step_to_Sedentary_Ratio',
    # Behavioral & Affect
    'Mobile_Usage_Hours', 'Screen_Unlock_Count', 'Social_App_Usage_Hours', 'Night_Phone_Usage_Minutes', 'Digital_Saturation',
    'Mood_Score', 'Stress_Index', 'Anxiety_Index', 'Emotional_Stability_Index', 'Affective_Risk_Ratio', 'Emotional_Dysregulation',
    'Age'
]

X = df[FEATURES].copy()
y = df['label'].copy()
groups = df['Participant_ID'].copy()

# Fill missing if any
X = X.fillna(X.median())

# Label Encoding
le = LabelEncoder()
le.fit(['Normal', 'Mild', 'Moderate', 'Severe'])
y_encoded = le.transform(y)

# Participant-aware split (80% train, 20% test)
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X, y_encoded, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y_encoded[train_idx], y_encoded[test_idx]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# Save processed matrices
np.save(os.path.join(OUT_DIR, 'X_train.npy'), X_train_scaled)
np.save(os.path.join(OUT_DIR, 'X_test.npy'),  X_test_scaled)
np.save(os.path.join(OUT_DIR, 'y_train.npy'), y_train)
np.save(os.path.join(OUT_DIR, 'y_test.npy'),  y_test)

joblib.dump(scaler, os.path.join(OUT_DIR, 'scaler.joblib'))
joblib.dump(le, os.path.join(OUT_DIR, 'label_encoder.joblib'))
pd.Series(FEATURES).to_csv(os.path.join(OUT_DIR, 'feature_names.csv'), index=False)

print(f"[OK] Preprocessing v2 finished. Total Features: {len(FEATURES)}")
print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
