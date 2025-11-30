import pandas as pd
import os
from datetime import datetime
import uuid

class TestLogger:
    def __init__(self, filepath="test_history.csv"):
        self.filepath = filepath
        self.run_id = str(uuid.uuid4())[:8]
        self.logs = []
        
        # Initialize file with headers if it doesn't exist
        if not os.path.exists(self.filepath):
            df = pd.DataFrame(columns=[
                "timestamp", "run_id", "step_name", "action_type", 
                "selector", "status", "error_message", "duration_ms"
            ])
            df.to_csv(self.filepath, index=False)

    def log_step(self, step_name, action_type, selector, status, error_msg="", duration_ms=0, context=None):
        """Log a single test step with optional context (e.g., dates used)"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "run_id": self.run_id,
            "step_name": step_name,
            "action_type": action_type,
            "selector": selector,
            "status": status,  # 1 for success, 0 for failure
            "error_message": str(error_msg).replace("\n", " ")[:200],
            "duration_ms": duration_ms,
            "context": str(context) if context else ""
        }
        self.logs.append(entry)
        
        # Append immediately to file
        df = pd.DataFrame([entry])
        # Check if file exists to write header
        header = not os.path.exists(self.filepath)
        df.to_csv(self.filepath, mode='a', header=header, index=False)
        print(f"   [ML-LOG] Recorded step: {step_name} -> {'PASS' if status else 'FAIL'}")

    def get_history(self):
        return pd.read_csv(self.filepath)
