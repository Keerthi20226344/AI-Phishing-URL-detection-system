import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from features import get_feature_names

def train_and_evaluate():
    # 1. Load dataset
    try:
        df = pd.read_csv('urldata.csv')
        print(f"Loaded dataset: {len(df)} samples")
    except FileNotFoundError:
        print("Error: urldata.csv not found. Please run dataset.py first to generate the data.")
        return
    
    # 2. Separate features and target
    feature_cols = get_feature_names()
    X = df[feature_cols]
    y = df['label']
    
    # 3. Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Training set: {X_train.shape[0]} samples, Testing set: {X_test.shape[0]} samples")
    
    # 4. Define models to train
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100),
        'Support Vector Machine (SVM)': SVC(random_state=42, probability=True)
    }
    
    results = {}
    trained_pipelines = {}
    
    print("\nTraining and evaluating models...")
    for name, model in models.items():
        # Create a pipeline that scales features first
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', model)
        ])
        
        # Train model
        pipeline.fit(X_train, y_train)
        
        # Predict on test set
        y_pred = pipeline.predict(X_test)
        
        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        results[name] = {
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1-score': f1
        }
        
        trained_pipelines[name] = pipeline
        print(f"Completed: {name} | Accuracy: {acc:.4f}")
        
    # 5. Display comparison
    results_df = pd.DataFrame(results).T
    print("\n=== Model Performance Comparison ===")
    print(results_df.to_markdown())
    print("====================================")
    
    # 6. Select the best-performing model based on Accuracy
    best_model_name = results_df['Accuracy'].idxmax()
    best_accuracy = results_df.loc[best_model_name, 'Accuracy']
    best_pipeline = trained_pipelines[best_model_name]
    
    print(f"\nBest Model selected: {best_model_name} with Accuracy: {best_accuracy:.4f}")
    
    # 7. Save the best model pipeline
    model_save_path = 'best_model.pkl'
    joblib.dump(best_pipeline, model_save_path)
    print(f"Saved the best model pipeline to '{model_save_path}'")
    
    # Save a manifest of performance for the application to reference or print
    manifest = {
        'best_model_name': best_model_name,
        'accuracy': best_accuracy,
        'metrics': results
    }
    joblib.dump(manifest, 'model_manifest.pkl')
    print("Saved model performance manifest to 'model_manifest.pkl'")

if __name__ == '__main__':
    train_and_evaluate()
