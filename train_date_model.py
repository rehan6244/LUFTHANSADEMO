import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
from datetime import datetime, timedelta

class DateOptimizer:
    def __init__(self):
        self.model = None
        
    def train(self):
        print("Generating date training data...")
        # Generate synthetic data: 
        # - Negative days (past) -> 0% success
        # - 0-2 days (too soon) -> 20% success
        # - 3-330 days (good) -> 95% success
        # - >330 days (too far) -> 10% success
        
        data = []
        # Cover a wide range of days
        for days in range(-1000, 1000):
            if days < 0:
                success = 0
            elif days < 3:
                success = 1 if np.random.random() < 0.2 else 0
            elif days < 330:
                success = 1 if np.random.random() < 0.95 else 0
            else:
                success = 0 # Assume > 330 is definitely bad for this simple model
                
            data.append({"days_from_today": days, "success": success})
            
        df = pd.DataFrame(data)
        
        X = df[["days_from_today"]]
        y = df["success"]
        
        print("Training Date Logic Model (Random Forest)...")
        self.model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
        self.model.fit(X, y)
        
        print("Saving model...")
        joblib.dump(self.model, "date_model.pkl")
        print("Date model trained!")

    def suggest_date(self, target_date_str):
        """
        Takes a date string (MM/DD/YYYY), checks if it's valid using the model.
        If invalid, finds the next valid date.
        """
        if self.model is None:
            try:
                self.model = joblib.load("date_model.pkl")
            except:
                print("Model not loaded. Please train first.")
                return target_date_str

        try:
            target_date = datetime.strptime(target_date_str, "%m/%d/%Y")
        except ValueError:
            print(f"Invalid date format: {target_date_str}")
            return target_date_str
            
        today = datetime.now()
        days_diff = (target_date - today).days
        
        # Predict probability of success
        # Note: RF requires 2D array
        prob = self.model.predict_proba([[days_diff]])[0][1]
        
        print(f"\nAnalyzing Date: {target_date_str} ({days_diff} days from now)")
        print(f"Success Probability: {prob:.1%}")
        
        if prob > 0.6:
            print("✅ Date looks good!")
            return target_date_str
        else:
            print("⚠️  Date is risky (likely in past or too far). Finding better date...")
            
            # Search forward for the next 365 days to find a good date
            # We start searching from TODAY (0) to 365, not from the bad date
            # This ensures if we passed 2020, we suggest 2025, not 2021.
            
            for i in range(3, 365): # Start from 3 days out
                new_prob = self.model.predict_proba([[i]])[0][1]
                
                if new_prob > 0.8:
                    new_date = today + timedelta(days=i)
                    new_date_str = new_date.strftime("%m/%d/%Y")
                    print(f"💡 AI Suggestion: Change to {new_date_str} (Probability: {new_prob:.1%})")
                    return new_date_str
            
            return target_date_str

if __name__ == "__main__":
    optimizer = DateOptimizer()
    optimizer.train()
    
    # Test it
    print("\n--- TEST: Past Date (2020) ---")
    optimizer.suggest_date("01/01/2020")
    
    print("\n--- TEST: Future Date (2025) ---")
    optimizer.suggest_date("12/25/2025")
