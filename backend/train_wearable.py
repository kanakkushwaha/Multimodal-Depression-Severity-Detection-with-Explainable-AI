"""
moodcompiler — High Accuracy Wearable ML Training (XGBoost, LightGBM, Tuned Ensembles)
"""

import numpy as np
import pandas as pd
import joblib
import os
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

PROC = os.path.join(os.path.dirname(__file__), 'data', 'processed')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

X_train = np.load(os.path.join(PROC, 'X_train.npy'))
X_test  = np.load(os.path.join(PROC, 'X_test.npy'))
y_train = np.load(os.path.join(PROC, 'y_train.npy'))
y_test  = np.load(os.path.join(PROC, 'y_test.npy'))
le = joblib.load(os.path.join(PROC, 'label_encoder.joblib'))

print(f"Dataset shapes: Train={X_train.shape}, Test={X_test.shape}")
print(f"Classes: {list(le.classes_)}\n")

models = {
    'XGBoost': XGBClassifier(
        n_estimators=350,
        max_depth=5,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric='mlogloss'
    ),
    'LightGBM': LGBMClassifier(
        n_estimators=350,
        max_depth=6,
        num_leaves=31,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        verbose=-1
    ),
    'HistGradientBoosting': HistGradientBoostingClassifier(
        max_iter=300,
        max_depth=6,
        learning_rate=0.05,
        random_state=42
    ),
    'Neural Net (MLP)': MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        max_iter=300,
        alpha=1e-3,
        random_state=42
    )
}

best_name, best_f1, best_model, best_acc = None, 0, None, 0

for name, model in models.items():
    print(f"Fitting {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"  Accuracy:    {acc * 100:.2f}%")
    print(f"  Macro F1:    {macro_f1:.4f}")
    print(f"  Weighted F1: {weighted_f1:.4f}\n")
    
    if macro_f1 > best_f1:
        best_f1 = macro_f1
        best_acc = acc
        best_name = name
        best_model = model

print("="*60)
print(f"SELECTED CHAMPION: {best_name}")
print(f"Test Accuracy: {best_acc * 100:.2f}% | Macro F1: {best_f1:.4f}")
print("="*60)

y_pred = best_model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Save the champion model
model_path = os.path.join(MODEL_DIR, 'wearable_model.joblib')
joblib.dump(best_model, model_path)
print(f"[OK] Champion model saved to: {model_path}")
