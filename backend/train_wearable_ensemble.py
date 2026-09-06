"""
moodcompiler — Wearable Soft-Voting Ensemble (Accuracy Boost)
Combines XGBoost, LightGBM, HistGradientBoosting, and Tuned Random Forest.
"""

import os
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

BASE_DIR = os.path.dirname(__file__)
PROC = os.path.join(BASE_DIR, 'data', 'processed')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

X_train = np.load(os.path.join(PROC, 'X_train.npy'))
X_test  = np.load(os.path.join(PROC, 'X_test.npy'))
y_train = np.load(os.path.join(PROC, 'y_train.npy'))
y_test  = np.load(os.path.join(PROC, 'y_test.npy'))
le = joblib.load(os.path.join(PROC, 'label_encoder.joblib'))

# 4 Specialized Decision Tree & Boosting Classifiers
m1 = XGBClassifier(n_estimators=300, max_depth=5, learning_rate=0.03, subsample=0.85, random_state=42, eval_metric='mlogloss')
m2 = LGBMClassifier(n_estimators=300, max_depth=6, num_leaves=31, learning_rate=0.03, subsample=0.85, random_state=42, verbose=-1)
m3 = HistGradientBoostingClassifier(max_iter=300, max_depth=6, learning_rate=0.04, random_state=42)
m4 = RandomForestClassifier(n_estimators=250, max_depth=14, class_weight='balanced', random_state=42, n_jobs=-1)

ensemble_wearable = VotingClassifier(
    estimators=[('xgb', m1), ('lgb', m2), ('hgb', m3), ('rf', m4)],
    voting='soft',
    weights=[2, 2, 2, 1]
)

print("Training Wearable Soft-Voting Ensemble Committee (11,700 samples)...")
ensemble_wearable.fit(X_train, y_train)

y_pred = ensemble_wearable.predict(X_test)
acc = accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average='macro')

print("="*50)
print(f"WEARABLE ENSEMBLE TEST ACCURACY: {acc * 100:.2f}% | Macro F1: {macro_f1:.4f}")
print("="*50)

# Overwrite saved model with upgraded ensemble
joblib.dump(ensemble_wearable, os.path.join(MODEL_DIR, 'wearable_model.joblib'))
print("[OK] Upgraded wearable ensemble saved to models/wearable_model.joblib")
