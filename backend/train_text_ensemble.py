"""
moodcompiler — Linguistic Soft-Voting Ensemble (Accuracy Boost)
Combines Logistic Regression, Calibrated Linear SVM, and Complement Naive Bayes.
"""

import os
import re
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import ComplementNB
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, 'data', 'reddit', 'Reddit_depression_dataset.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

# Load and clean
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=['text', 'label']).copy()

label_mapping = {'minimum': 'Normal', 'mild': 'Mild', 'moderate': 'Moderate', 'severe': 'Severe'}
df['label_std'] = df['label'].str.lower().str.strip().map(label_mapping)
df = df.dropna(subset=['label_std']).copy()

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

df['clean_text'] = df['text'].apply(clean_text)

X_train, X_test, y_train, y_test = train_test_split(
    df['clean_text'], df['label_std'], test_size=0.20, random_state=42, stratify=df['label_std']
)

tfidf = TfidfVectorizer(max_features=9000, ngram_range=(1, 2), sublinear_tf=True, min_df=2, stop_words='english')
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec  = tfidf.transform(X_test)

# 3 Diverse Classifiers for Voting Committee
clf1 = LogisticRegression(C=2.5, max_iter=1500, class_weight='balanced', random_state=42)
clf2 = CalibratedClassifierCV(SGDClassifier(loss='hinge', class_weight='balanced', random_state=42), cv=3)
clf3 = ComplementNB(alpha=0.4)

ensemble_text = VotingClassifier(
    estimators=[('lr', clf1), ('sgd', clf2), ('cnb', clf3)],
    voting='soft',
    weights=[2, 2, 1]
)

print("Training Text Soft-Voting Ensemble Committee...")
ensemble_text.fit(X_train_vec, y_train)

y_pred = ensemble_text.predict(X_test_vec)
acc = accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average='macro')

print("="*50)
print(f"TEXT ENSEMBLE TEST ACCURACY: {acc * 100:.2f}% | Macro F1: {macro_f1:.4f}")
print("="*50)

# Overwrite saved model with upgraded ensemble
joblib.dump(ensemble_text, os.path.join(MODEL_DIR, 'text_model.joblib'))
joblib.dump(tfidf, os.path.join(MODEL_DIR, 'tfidf_vectorizer.joblib'))
print("[OK] Upgraded text ensemble saved to models/text_model.joblib")
