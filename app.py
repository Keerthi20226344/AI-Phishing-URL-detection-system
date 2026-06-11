import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify, render_template
from features import extract_features, clean_url, get_feature_names

app = Flask(__name__)

# Global variables for model and manifest
model = None
manifest = None

def load_ml_model():
    """
    Loads the trained model pipeline and performance manifest at startup.
    """
    global model, manifest
    model_path = 'best_model.pkl'
    manifest_path = 'model_manifest.pkl'
    
    if os.path.exists(model_path) and os.path.exists(manifest_path):
        try:
            model = joblib.load(model_path)
            manifest = joblib.load(manifest_path)
            print(f"ML Model loaded successfully. Best algorithm: {manifest['best_model_name']}")
        except Exception as e:
            print(f"Error loading model: {e}")
            model = None
            manifest = None
    else:
        print("Warning: Trained model files not found. Please train the model first by running train.py")
        model = None
        manifest = None

# Initialize model load
load_ml_model()

@app.route('/')
def index():
    """
    Serves the main application page.
    """
    model_name = manifest['best_model_name'] if manifest else "Not Trained"
    accuracy = f"{manifest['accuracy'] * 100:.2f}%" if manifest else "N/A"
    return render_template('index.html', model_name=model_name, accuracy=accuracy)

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    POST API endpoint to analyze a URL.
    Expects JSON: { "url": "..." }
    """
    global model
    if model is None:
        # Re-attempt loading in case it was trained after startup
        load_ml_model()
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Machine learning model is not trained yet. Please run the training script.'
            }), 503

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing URL in request body.'
        }), 400

    raw_url = data['url'].strip()
    if not raw_url:
        return jsonify({
            'success': False,
            'error': 'URL cannot be empty.'
        }), 400

    try:
        # 1. Clean URL and extract features
        cleaned_url = clean_url(raw_url)
        features_dict = extract_features(cleaned_url)
        
        # 2. Convert to DataFrame to match names and prevent warnings
        features_df = pd.DataFrame([features_dict], columns=get_feature_names())
        
        # 3. Predict and get probability
        prediction = int(model.predict(features_df)[0])
        probabilities = model.predict_proba(features_df)[0]
        
        # Confidence score corresponds to the probability of the predicted class
        confidence = float(probabilities[prediction]) * 100
        
        # 4. Generate granular explanations
        explanation_points = []
        is_phishing = (prediction == 1)
        
        if is_phishing:
            if features_dict['is_ip'] == 1:
                explanation_points.append("The hostname is an IP address instead of a standard domain name, which is heavily associated with spoofing and phishing.")
            if features_dict['has_at_symbol'] == 1:
                explanation_points.append("The URL contains an '@' symbol, which causes modern browsers to ignore the characters before it and navigate directly to the address after it—a common deception technique.")
            if features_dict['is_shortened'] == 1:
                explanation_points.append("The URL uses a known URL shortening service, which masks the final destination domain and is frequently used to bypass basic link scanners.")
            if features_dict['has_double_slash'] == 1:
                explanation_points.append("The URL contains a double slash '//' in its path, which indicates HTTP redirection and can redirect users to an unexpected server.")
            if features_dict['suspicious_keyword_count'] > 0:
                explanation_points.append(f"The URL contains {features_dict['suspicious_keyword_count']} sensitive/suspicious keyword(s) (e.g., login, verify, update) designed to induce urgency or trust.")
            if features_dict['has_hyphen_domain'] == 1:
                explanation_points.append("The domain name contains a hyphen '-', a frequent characteristic of phishing domains impersonating genuine brands (e.g., secure-paypal-login).")
            if features_dict['subdomain_count'] >= 2:
                explanation_points.append(f"The URL has a high number of subdomains ({features_dict['subdomain_count']}), which is often used to embed trademarked brand names within complex, deceptive hostnames.")
            if features_dict['url_length'] > 75:
                explanation_points.append(f"The URL is extremely long ({features_dict['url_length']} characters), which is typically done to push the actual target domain out of the user's address bar view on mobile devices.")
            
            # Catch-all if no specific flags triggered
            if not explanation_points:
                explanation_points.append("The ML model detected an overall signature matching typical phishing patterns, including structural characteristics of the URL path and parameters.")
        else:
            explanation_points.append("The URL uses standard, clean formatting and shows no typical indicators of phishing deception.")
            if features_dict['url_length'] < 50:
                explanation_points.append("The URL is short and structurally clean.")
            if features_dict['suspicious_keyword_count'] == 0:
                explanation_points.append("No suspicious credentials or urgency keywords were detected in the address.")
        
        # 5. Return detailed analysis result
        return jsonify({
            'success': True,
            'url': raw_url,
            'prediction': 'Phishing URL' if is_phishing else 'Safe URL',
            'is_phishing': is_phishing,
            'confidence': round(confidence, 1),
            'features': features_dict,
            'explanations': explanation_points
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error analyzing URL: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Enable debugging for development
    app.run(debug=True, host='0.0.0.0', port=5000)
