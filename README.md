# AI-Based Phishing URL Detection System

A complete, high-fidelity, responsive web application that detects whether a given URL is legitimate (Safe) or a phishing attack. The system uses a Python Flask backend combined with a machine learning classification pipeline.

## 🚀 Key Features

*   **Real-Time Link Inspection**: Parses incoming URLs, extracts structure-based features, and evaluates safety instantly.
*   **Aesthetic Responsive SPA**: A modern corporate-styled Single Page Application (SPA) driven by Vanilla CSS and JS with smooth slide transitions and loading indicators.
*   **Machine Learning Comparison Pipeline**: Integrates four distinct algorithms:
    1.  **Logistic Regression**
    2.  **Decision Tree**
    3.  **Random Forest**
    4.  **Support Vector Machine (SVM)**
*   **Confidence Score Meter**: Dynamic gauge demonstrating the statistical likelihood of deception.
*   **Observation Diagnostics**: Explains exactly *why* a URL is classified as safe or harmful by detailing structural alerts (e.g., IP addresses, double-slash redirects, suspicious keywords, domain hyphens).

---

## 🛠️ Tech Stack & Directory Structure

*   **Frontend**: HTML5, Vanilla CSS3 (Custom Responsive Layout), FontAwesome 6 Icons.
*   **Backend**: Python 3, Flask.
*   **Data & ML**: Pandas, NumPy, Scikit-learn, Joblib.

```
phishing-detection-system/
├── app.py                     # Flask application server
├── features.py                # URL feature extraction module (12 custom features)
├── dataset.py                 # Balanced dataset generator (creates 2,000 URLs)
├── train.py                   # Model comparison and training controller
├── requirements.txt           # Python dependency manifest
├── README.md                  # System setup and execution instructions
├── templates/
│   └── index.html             # Main SPA frontend dashboard template
└── static/
    ├── css/
    │   └── style.css          # Light-theme corporate styles & responsive layouts
    └── js/
        └── main.js            # Client-side state routing and async API fetching
```

---

## 📝 Feature Engineering

The feature extraction module (`features.py`) parses each URL and computes a vector of **12 structural and content-based features**:
1.  `url_length`: Overall length of the URL string.
2.  `hostname_length`: Length of the primary host domain.
3.  `is_ip`: Evaluates if the hostname is an IP address instead of a standard domain.
4.  `has_at_symbol`: Binary check for the `@` character.
5.  `has_double_slash`: Checks for redirection `//` in the path segment.
6.  `has_hyphen_domain`: Evaluates if the domain contains hyphens `-` (common in brand spoofing).
7.  `dot_count`: Count of periods `.` in the URL.
8.  `subdomain_count`: Number of subdomains (excluding `www` and root domains).
9.  `is_shortened`: Checks if the domain belongs to known URL shortening services (e.g. `bit.ly`, `t.co`).
10. `has_https_in_domain`: Validates if `https` or `http` tokens are stuffed in the domain portion.
11. `special_char_count`: Counts active delimiters (`?`, `=`, `&`, `_`, `%`, `+`).
12. `suspicious_keyword_count`: Evaluates occurrences of highly deceptive keywords (`login`, `secure`, `verify`, `update`, `bank`).

---

## 💻 Setup & Execution Instructions

Follow these steps to configure your environment, train the machine learning models, and launch the web server:

### 1. Prerequisite Installation
Ensure you have Python 3 installed. Open your command terminal (Command Prompt, PowerShell, or Git Bash) inside the project root folder and execute:
```bash
python -m pip install -r requirements.txt
```

### 2. Generate the Dataset
Create a balanced dataset containing 2,000 high-fidelity samples (1,000 legitimate and 1,000 phishing URLs) with distinct characteristic distributions:
```bash
python dataset.py
```
This output creates `urldata.csv` inside your project directory.

### 3. Train & Select the Best Model
Execute the machine learning pipeline to split features (80/20 train-test split), scale features using Standard Scaling pipelines, evaluate metrics (Accuracy, Precision, Recall, F1), and save the top-performing model:
```bash
python train.py
```
This trains all four classifiers (Logistic Regression, Decision Tree, Random Forest, SVM) and serializes the best performer to `best_model.pkl` and its manifest metadata to `model_manifest.pkl`.

### 4. Run the Flask Web Application
Launch the Flask development server to serve the SPA frontend dashboard:
```bash
python app.py
```
Once initialized, open your web browser and navigate to:
```
http://127.0.0.1:5000
```
Use the application to paste and verify any link.
