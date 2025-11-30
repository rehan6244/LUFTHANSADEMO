import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

def generate_synthetic_data(n_samples=100):
    """Generate synthetic test history to bootstrap the model"""
    steps = [
        ("Navigate to Home", "navigation", "url:flight-search"),
        ("Handle Overlays", "javascript", "consent_buttons"),
        ("Set Origin", "input", "input[name*='originCode']"),
        ("Set Destination", "input", "input[name*='destinationCode']"),
        ("Select Dates", "complex_interaction", "input[name*='travelDatetime']"),
        ("Click Search", "click", "button:has-text('Search flights')"),
        ("Wait for Results", "wait", "div[class*='price']")
    ]
    
    data = []
    for _ in range(n_samples):
        for step_name, action, selector in steps:
            # Base success rate
            success_prob = 0.95
            
            # Simulate specific failure patterns we've seen
            if step_name == "Select Dates":
                success_prob = 0.60  # Hard step
            elif step_name == "Wait for Results":
                # If dates failed, this fails
                success_prob = 0.50
            
            status = 1 if np.random.random() < success_prob else 0
            
            duration = np.random.normal(1000, 200)
            if status == 0:
                duration = np.random.normal(30000, 1000) # Timeouts are long
                
            data.append({
                "step_name": step_name,
                "action_type": action,
                "selector": selector,
                "status": status,
                "duration_ms": duration
            })
            
    return pd.DataFrame(data)

def train_model():
    print("Loading training data...")
    
    # Load real data if exists
    if os.path.exists("test_history.csv"):
        real_data = pd.read_csv("test_history.csv")
        # Keep only relevant columns
        real_data = real_data[["step_name", "action_type", "selector", "status", "duration_ms"]]
    else:
        real_data = pd.DataFrame()
        
    # Generate synthetic data
    print("Generating synthetic data to augment training...")
    syn_data = generate_synthetic_data(200)
    
    # Combine
    df = pd.concat([real_data, syn_data], ignore_index=True)
    print(f"Total training samples: {len(df)}")
    
    # Preprocessing
    le_step = LabelEncoder()
    le_action = LabelEncoder()
    le_selector = LabelEncoder()
    
    df['step_encoded'] = le_step.fit_transform(df['step_name'])
    df['action_encoded'] = le_action.fit_transform(df['action_type'])
    df['selector_encoded'] = le_selector.fit_transform(df['selector'])
    
    # Features: Step info + Duration (simulated previous step duration)
    X = df[['step_encoded', 'action_encoded', 'selector_encoded']]
    y = df['status']
    
    # Train
    print("Training Random Forest model...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    # Evaluate
    print("\nModel Performance:")
    print(classification_report(y, clf.predict(X)))
    
    # Save artifacts
    print("Saving model and encoders...")
    joblib.dump(clf, 'error_model.pkl')
    joblib.dump(le_step, 'le_step.pkl')
    joblib.dump(le_action, 'le_action.pkl')
    joblib.dump(le_selector, 'le_selector.pkl')
    print("Done!")

if __name__ == "__main__":
    train_model()
