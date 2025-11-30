import joblib
import pandas as pd
import sys

def predict_step_risk(step_name, action_type, selector):
    try:
        # Load model and encoders
        clf = joblib.load('error_model.pkl')
        le_step = joblib.load('le_step.pkl')
        le_action = joblib.load('le_action.pkl')
        le_selector = joblib.load('le_selector.pkl')
        
        # Encode inputs (handle unseen labels gracefully)
        try:
            s_enc = le_step.transform([step_name])[0]
        except:
            s_enc = 0 # Default
            
        try:
            a_enc = le_action.transform([action_type])[0]
        except:
            a_enc = 0
            
        try:
            sel_enc = le_selector.transform([selector])[0]
        except:
            sel_enc = 0
            
        # Predict
        prob_success = clf.predict_proba([[s_enc, a_enc, sel_enc]])[0][1]
        prob_fail = 1 - prob_success
        
        print(f"\nRisk Analysis for step: '{step_name}'")
        print(f"Action: {action_type}")
        print(f"Selector: {selector}")
        print("-" * 30)
        
        if prob_fail > 0.3:
            print(f"⚠️  HIGH RISK DETECTED (Failure Probability: {prob_fail:.1%})")
            print("   Recommendation: Add extra wait times, try-catch blocks, or alternative selectors.")
        elif prob_fail > 0.1:
            print(f"⚠️  MODERATE RISK (Failure Probability: {prob_fail:.1%})")
        else:
            print(f"✅ LOW RISK (Failure Probability: {prob_fail:.1%})")
            
    except FileNotFoundError:
        print("Error: Model not found. Please run 'python3 train_error_model.py' first.")

if __name__ == "__main__":
    if len(sys.argv) > 3:
        predict_step_risk(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # Demo prediction
        print("Running demo prediction for 'Select Dates' step...")
        predict_step_risk("Select Dates", "complex_interaction", "input[name*='travelDatetime']")
