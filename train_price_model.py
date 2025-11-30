import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime
import os

def generate_synthetic_prices(n_samples=500):
    """Generate synthetic price data to bootstrap the model"""
    data = []
    base_price = 800
    
    for _ in range(n_samples):
        # Random days in advance (1 to 180)
        days_advance = np.random.randint(1, 180)
        
        # Price logic:
        # - Very close (< 7 days): Expensive
        # - Close (7-21 days): Moderate
        # - Sweet spot (21-60 days): Cheapest
        # - Far out (> 60 days): Moderate
        
        if days_advance < 7:
            price = base_price * np.random.uniform(1.5, 2.5)
        elif days_advance < 21:
            price = base_price * np.random.uniform(1.2, 1.5)
        elif days_advance < 60:
            price = base_price * np.random.uniform(0.8, 1.1) # Cheap!
        else:
            price = base_price * np.random.uniform(1.0, 1.3)
            
        # Add some noise
        price += np.random.normal(0, 50)
        
        data.append({
            "days_advance": days_advance,
            "price": round(price, 2)
        })
            
    return pd.DataFrame(data)

def train_price_model():
    print("Loading price history...")
    
    real_data = pd.DataFrame()
    if os.path.exists("price_history.csv"):
        try:
            df = pd.read_csv("price_history.csv")
            # Calculate days in advance
            today = datetime.now()
            df['dep_dt'] = pd.to_datetime(df['dep_date'])
            df['days_advance'] = (df['dep_dt'] - today).dt.days
            real_data = df[['days_advance', 'price']]
            print(f"Loaded {len(real_data)} real price points.")
        except Exception as e:
            print(f"Error reading real data: {e}")
            
    # Generate synthetic data
    print("Generating synthetic price data...")
    syn_data = generate_synthetic_prices(1000)
    
    # Combine
    df = pd.concat([real_data, syn_data], ignore_index=True)
    
    X = df[['days_advance']]
    y = df['price']
    
    print("Training Price Prediction Model (Random Forest)...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    print("Saving model...")
    joblib.dump(model, "price_model.pkl")
    print("Price model trained!")
    
    # Test predictions
    print("\n--- Price Predictions ---")
    test_days = [2, 14, 45, 90]
    for d in test_days:
        pred = model.predict([[d]])[0]
        print(f"Booking {d} days in advance: ${pred:.2f}")

if __name__ == "__main__":
    train_price_model()
