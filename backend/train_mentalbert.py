"""
moodcompiler — MentalBERT Fine-Tuning Pipeline
"Behind Every Signal, There's a Story."

Model: mental/mental-bert-base-uncased (Domain-specific pretrained BERT for mental health)
Dataset: Reddit_depression_dataset.csv (4 Classes: Normal, Mild, Moderate, Severe)
Features: Class-weighted loss, Stratified Split, Auto-save Best Checkpoint
"""

import os
import re
import json
import torch
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup
)
from torch.optim import AdamW

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'reddit', 'Reddit_depression_dataset.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'models', 'mentalbert_depression')
MODEL_NAME = 'mental/mental-bert-base-uncased'

BATCH_SIZE = 16
MAX_LEN = 128
EPOCHS = 3
LR = 2e-5
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

LABEL_MAP = {'minimum': 'Normal', 'mild': 'Mild', 'moderate': 'Moderate', 'severe': 'Severe'}
LABEL2ID = {'Normal': 0, 'Mild': 1, 'Moderate': 2, 'Severe': 3}
ID2LABEL = {0: 'Normal', 1: 'Mild', 2: 'Moderate', 3: 'Severe'}

def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

class DepressionTextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_len,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

def train_mentalbert():
    print("==================================================")
    print(" moodcompiler — MentalBERT Fine-Tuning Pipeline")
    print(f" Using Device: {DEVICE}")
    print(f" Pretrained Foundation: {MODEL_NAME}")
    print("==================================================")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH).dropna(subset=['text', 'label']).copy()
    df['label_std'] = df['label'].str.lower().str.strip().map(LABEL_MAP)
    df = df.dropna(subset=['label_std']).copy()
    df['clean'] = df['text'].apply(clean_text)
    df['target'] = df['label_std'].map(LABEL2ID)

    print(f"[+] Loaded {len(df)} samples.")
    print(f"    Class distribution:\n{df['label_std'].value_counts()}")

    X_train, X_val, y_train, y_val = train_test_split(
        df['clean'].values,
        df['target'].values,
        test_size=0.20,
        random_state=42,
        stratify=df['target'].values
    )
    print(f"[+] Train: {len(X_train)} | Validation: {len(X_val)}")

    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.array([0, 1, 2, 3]),
        y=y_train
    )
    weights_tensor = torch.tensor(class_weights, dtype=torch.float).to(DEVICE)
    print(f"[+] Computed Balanced Class Weights: {np.round(class_weights, 3)}")

    print(f"[+] Loading Tokenizer ({MODEL_NAME})...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_ds = DepressionTextDataset(X_train, y_train, tokenizer, MAX_LEN)
    val_ds = DepressionTextDataset(X_val, y_val, tokenizer, MAX_LEN)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    print("[+] Initializing Sequence Classification Model (4 classes)...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=4,
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )
    model.to(DEVICE)

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),
        num_training_steps=total_steps
    )
    criterion = torch.nn.CrossEntropyLoss(weight=weights_tensor)

    best_f1 = 0.0
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n--- Commencing Training Loop ---")
    for epoch in range(EPOCHS):
        model.train()
        total_train_loss = 0.0

        for step, batch in enumerate(train_loader):
            input_ids = batch['input_ids'].to(DEVICE)
            attention_mask = batch['attention_mask'].to(DEVICE)
            labels = batch['labels'].to(DEVICE)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = criterion(outputs.logits, labels)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

            total_train_loss += loss.item()

            if (step + 1) % 25 == 0 or (step + 1) == len(train_loader):
                print(f" Epoch [{epoch+1}/{EPOCHS}] | Step [{step+1}/{len(train_loader)}] | Loss: {loss.item():.4f}")

        avg_train_loss = total_train_loss / len(train_loader)

        model.eval()
        val_preds, val_targets = [], []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(DEVICE)
                attention_mask = batch['attention_mask'].to(DEVICE)
                labels = batch['labels'].to(DEVICE)

                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
                val_preds.extend(preds)
                val_targets.extend(labels.cpu().numpy())

        acc = accuracy_score(val_targets, val_preds)
        f1 = f1_score(val_targets, val_preds, average='macro')
        print(f"\n>> Epoch {epoch+1} Results: Val Accuracy: {acc*100:.2f}% | Macro F1: {f1:.4f} | Avg Train Loss: {avg_train_loss:.4f}\n")

        if f1 > best_f1:
            best_f1 = f1
            print(f"[*] New best validation Macro F1: {best_f1:.4f}. Saving checkpoint to {OUTPUT_DIR}...")
            model.save_pretrained(OUTPUT_DIR)
            tokenizer.save_pretrained(OUTPUT_DIR)
            with open(os.path.join(OUTPUT_DIR, 'metadata.json'), 'w') as f:
                json.dump({
                    'model_name': MODEL_NAME,
                    'val_accuracy': round(acc * 100, 2),
                    'val_macro_f1': round(f1, 4),
                    'classes': ['Normal', 'Mild', 'Moderate', 'Severe']
                }, f, indent=2)

    print("==================================================")
    print(f"Training Complete! Best Macro F1: {best_f1:.4f}")
    print(f"Artifacts saved to: {OUTPUT_DIR}")
    print("==================================================")

if __name__ == '__main__':
    train_mentalbert()
