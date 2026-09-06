"""
moodcompiler — Reddit Linguistic NLP Classifier
Trains an optimized TF-IDF + Calibrated Linear Classifier on the Reddit Depression Dataset.
Handles class imbalance via balanced weighting and evaluates macro F1, precision, recall.
"""

import os
import re
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

# Paths
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'reddit', 'Reddit_depression_dataset.csv')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

# 1. Load dataset
df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=['text', 'label']).copy()

# Label normalization to project standards:
# minimum -> Normal, mild -> Mild, moderate -> Moderate, severe -> Severe
label_mapping = {
    'minimum':  'Normal',
    'mild':     'Mild',
    'moderate': 'Moderate',
    'severe':   'Severe'
}
df['label_std'] = df['label'].str.lower().str.strip().map(label_mapping)
df = df.dropna(subset=['label_std']).copy()

print(f"Total clean samples: {len(df)}")
print("Class Distribution:")
print(df['label_std'].value_counts())

# 2. Text cleaning function
def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("\nCleaning text tokens...")
df['clean_text'] = df['text'].apply(clean_text)

# 3. Stratified Train-Test Split (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    df['clean_text'],
    df['label_std'],
    test_size=0.20,
    random_state=42,
    stratify=df['label_std']
)

print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

# 4. Feature Extraction: Sublinear TF-IDF (Unigram + Bigram)
print("\nExtracting TF-IDF n-grams (1, 2)...")
tfidf = TfidfVectorizer(
    max_features=8000,
    ngram_range=(1, 2),
    sublinear_tf=True,
    min_df=2,
    stop_words='english'
)

X_train_vec = tfidf.fit_transform(X_train)
X_test_vec  = tfidf.transform(X_test)

# 5. Candidate Classifiers with Balanced Weights
candidates = {
    'Balanced Logistic Regression': LogisticRegression(
        C=2.5,
        max_iter=1500,
        class_weight='balanced',
        random_state=42
    ),
    'Calibrated Linear SGD (Hinge)': CalibratedClassifierCV(
        SGDClassifier(loss='hinge', penalty='l2', alpha=1e-4, class_weight='balanced', random_state=42),
        cv=3
    ),
    'Complement Naive Bayes': ComplementNB(alpha=0.5)
}

best_name, best_f1, best_model = None, 0, None

for name, model in candidates.items():
    print(f"\n--- Training {name} ---")
    model.fit(X_train_vec, y_train)
    y_pred = model.predict(X_test_vec)
    
    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"  Accuracy:    {acc * 100:.2f}%")
    print(f"  Macro F1:    {macro_f1:.4f}")
    print(f"  Weighted F1: {weighted_f1:.4f}")
    
    if macro_f1 > best_f1:
        best_f1 = macro_f1
        best_name = name
        best_model = model

print("\n" + "="*55)
print(f"CHAMPION TEXT MODEL: {best_name} (Macro F1: {best_f1:.4f})")
print("="*55)

y_pred = best_model.predict(X_test_vec)
classes = ['Normal', 'Mild', 'Moderate', 'Severe']
print("\nClassification Report:")
print(classification_report(y_test, y_pred, labels=classes))

print("Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred, labels=classes)
print(pd.DataFrame(cm, index=classes, columns=classes))

# 6. Save Artifacts for Backend
joblib.dump(best_model, os.path.join(MODEL_DIR, 'text_model.joblib'))
joblib.dump(tfidf, os.path.join(MODEL_DIR, 'tfidf_vectorizer.joblib'))

print(f"\n[OK] Text model saved to: {os.path.join(MODEL_DIR, 'text_model.joblib')}")
print(f"[OK] Vectorizer saved to: {os.path.join(MODEL_DIR, 'tfidf_vectorizer.joblib')}")
print("STEP 21 COMPLETE.")
