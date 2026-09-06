# 🧠 moodcompiler
> *"Behind Every Signal, There's a Story."*

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-%232196F3.svg?style=for-the-badge)](https://xgboost.readthedocs.io/)

**moodcompiler** is a multimodal AI research system designed for early depression severity detection by fusing continuous wearable physiological telemetry with digital linguistic expressions using Decision-Level Late Fusion and Explainable AI (XAI).

---

## 👥 Academic Project Identity
- **Institution:** Department of Information Technology, Pimpri Chinchwad College of Engineering (PCCoE), Pune
- **Project Title:** Multimodal Early Depression Severity Detection with Explainable AI
- **Project Guide:** Dr. Roshani Raut
- **Project Team:**
  - Kanak Kushwaha
  - Sahil Tiwari
  - Aayush Kate

---

## 🌟 Key Features
- **Multimodal Decision-Level Late Fusion:** Solves the unpaired cohort constraint via adaptive Bayesian posterior likelihood fusion.
- **Linguistic Branch (NLP):** Sublinear TF-IDF with 3-Model Soft-Voting Ensemble (Logistic Regression, Calibrated Linear SVM, Complement Naive Bayes) trained on 3,553 Reddit posts.
- **Physiological Branch (Wearables):** Tree-boosting ensemble (XGBoost, LightGBM, HistGradientBoosting, Random Forest) with participant-aware validation (`GroupShuffleSplit`) trained on 11,700 longitudinal wearable records.
- **Explainable AI (XAI):** Quantitative feature attribution bars and human-readable clinical decision rationale explaining *why* the model assigned the severity tier.
- **Vanilla Canvas 3D Neural Journey:** High-performance hardware-accelerated 3D neural pipeline animation built without heavy WebGL dependencies.
- **Production REST API:** Fast, asynchronous FastAPI backend with automated offline fallback support.

---

## 📊 Model Evaluation Benchmarks

| Modality | Architecture | Dataset | Benchmark Accuracy |
|---|---|---|:---:|
| **Linguistic (Text)** | Sublinear TF-IDF + Soft-Voting Ensemble | Reddit Depression Dataset (N=3,553) | **72.9%** |
| **Physiological (Sensors)** | Biosignal Engineering + XGBoost/LGBM Ensemble | Wearable Depression Dataset (N=11,700) | **58.6%** |
| **Multimodal Synergy** | Decision Late-Fusion ($\alpha$-Adaptive) | Multimodal Late-Fusion | **~73.4%** |
| **Inference Confidence** | Bayesian Posterior Entropy | Live Inference Convergence | **88% – 95%** |

---

## 🗂️ Repository Structure

```plaintext
moodcompiler/
├── frontend/
│   ├── index.html                     # Landing page with neural particle canvas & team showcase
│   ├── assessment.html                # 4-step wizard with text capture & 8 biosignal sliders
│   ├── results.html                   # AI Insight Report with XAI attributions & model accuracy
│   ├── css/
│   │   └── style.css                  # Warm Editorial Midnight design system
│   ├── js/
│   │   ├── emotional-signal-field.js  # 3D background silk waveform canvas
│   │   ├── fusion-pipeline.js         # 3D AI fusion state machine animation
│   │   └── assessment.js              # 2-way input sync, presets, and API integration
│   └── assets/                        # Logo, iconography, and visual artifacts
├── backend/
│   ├── main.py                        # Production FastAPI REST application
│   ├── requirements.txt               # Python package dependencies
│   ├── models/
│   │   ├── fusion.py                  # Decision-level late fusion & XAI engine
│   │   ├── text_model.joblib          # Trained NLP ensemble checkpoint
│   │   ├── tfidf_vectorizer.joblib    # Fitted TF-IDF vocabulary checkpoint
│   │   └── wearable_model.joblib      # Trained wearable ensemble checkpoint
│   ├── preprocessing/
│   │   └── prepare_wearable.py        # Biosignal ratio extraction & participant-aware split
│   ├── notebooks/
│   │   ├── 01_wearable_eda_and_ml.ipynb           # Wearable EDA, boxplots, and ML training
│   │   ├── 02_reddit_nlp_classification.ipynb     # Reddit text cleaning, n-grams, and NLP models
│   │   └── 03_multimodal_fusion_and_xai.ipynb     # Unpaired late-fusion & XAI explanations
│   └── data/                          # Dataset directories
├── .gitignore
└── README.md
```

---

## 🚀 Quickstart & Installation

### 1. Clone the repository
```bash
git clone https://github.com/kanakkushwaha/moodcompiler.git
cd moodcompiler
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

### 3. Frontend Execution
Simply open `frontend/index.html` in your browser or run via VS Code **Live Server**.

---

## ⚖️ Academic Research Disclaimer
*moodcompiler is an exploratory academic research prototype developed as part of a B.Tech IT capstone curriculum at PCCoE Pune. It does not provide medical diagnoses or replace professional psychiatric consultation.*
