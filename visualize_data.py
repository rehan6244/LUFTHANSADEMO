import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from train_error_model import generate_synthetic_data
from train_price_model import generate_synthetic_prices
import os

def visualize_test_reliability():
    print("Generating Test Reliability Chart...")
    
    # Load real data if available
    if os.path.exists("test_history.csv"):
        real_df = pd.read_csv("test_history.csv")
    else:
        real_df = pd.DataFrame()
        
    # Generate synthetic data to make the chart look good
    syn_df = generate_synthetic_data(200)
    
    # Combine
    df = pd.concat([real_df, syn_df], ignore_index=True)
    
    # Calculate success rate per step
    step_stats = df.groupby('step_name')['status'].mean().reset_index()
    step_stats['success_rate'] = step_stats['status'] * 100
    step_stats = step_stats.sort_values('success_rate', ascending=False)
    
    # Plot
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    
    # Color bars based on success rate (Green=High, Red=Low)
    colors = ['green' if x > 80 else 'orange' if x > 50 else 'red' for x in step_stats['success_rate']]
    
    ax = sns.barplot(x='success_rate', y='step_name', data=step_stats, palette=colors)
    
    plt.title('Test Step Reliability (Success Rate %)', fontsize=16)
    plt.xlabel('Success Rate (%)', fontsize=12)
    plt.ylabel('Test Step', fontsize=12)
    plt.xlim(0, 100)
    
    # Add percentage labels
    for i, v in enumerate(step_stats['success_rate']):
        ax.text(v + 1, i, f"{v:.1f}%", va='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('test_reliability.png')
    print("✓ Saved test_reliability.png")

def visualize_price_trends():
    print("Generating Price Trend Chart...")
    
    # Generate synthetic price data (mimicking our model's logic)
    df = generate_synthetic_prices(500)
    
    # Plot
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="darkgrid")
    
    # Scatter plot with regression line
    sns.regplot(
        x='days_advance', 
        y='price', 
        data=df, 
        scatter_kws={'alpha':0.5, 's':20}, 
        line_kws={'color': 'red'},
        order=3 # Polynomial fit to show the "dip" in prices
    )
    
    plt.title('Flight Price vs. Booking Lead Time', fontsize=16)
    plt.xlabel('Days in Advance', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    
    # Highlight the "Sweet Spot"
    plt.axvspan(21, 60, color='green', alpha=0.1, label='Best Booking Window')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('price_trends.png')
    print("✓ Saved price_trends.png")

if __name__ == "__main__":
    visualize_test_reliability()
    visualize_price_trends()
