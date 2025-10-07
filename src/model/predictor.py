# src/model/predictor.py (MODIFIED for Accuracy)

import pandas as pd
import numpy as np
import sys
from typing import Dict, Any

# 🛑 NEW IMPORT: Needed to calculate performance metrics
from sklearn.metrics import accuracy_score

# Note the relative imports using the package structure
from ..utils.data_loader import load_model_from_s3
from ..pipeline.feature_extractor import preprocess_input_data
from ..exception import DataValidationFailure

class PhishingPredictor:
    """
    Manages the loading and prediction using the ML model. 
    Loads the model from S3 during initialization.
    """
    
    def __init__(self):
        print("Loading ML model into memory from S3...")
        self.model = load_model_from_s3()
        if self.model:
            print("✅ Model successfully initialized and ready for prediction.")

    def predict(self, raw_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Takes a raw input DataFrame, processes it, and returns prediction results,
        including accuracy if the 'Result' column is present.
        """
        if self.model is None:
            raise RuntimeError("Prediction model is not loaded. Service is unavailable.")

        # --- 🛑 ACCURACY CALCULATION LOGIC START ---
        accuracy_metric = None
        y_true = None
        
        # 1. Check for the ground truth column
        if 'Result' in raw_df.columns:
            print("Ground truth 'Result' column found. Preparing to calculate metrics.")
            y_true = raw_df['Result'].values
            # Create a features-only DataFrame to avoid errors during feature extraction
            df_features = raw_df.drop(columns=['Result'])
        else:
            df_features = raw_df
        # --- ACCURACY CALCULATION LOGIC END ---

        # 2. Preprocess the data using the Feature Extractor logic
        try:
            X_processed = preprocess_input_data(df_features) 
        except DataValidationFailure as e:
            raise e 
        except Exception as e:
            raise DataValidationFailure(f"Unexpected preprocessing error: {e}", sys) 

        # 3. Make Predictions
        predictions = self.model.predict(X_processed)
        
        # --- 🛑 ACCURACY CALCULATION START ---
        # 4. Calculate Accuracy if we had the true labels
        if y_true is not None:
            accuracy = accuracy_score(y_true, predictions)
            accuracy_metric = round(accuracy * 100, 2)
            print(f"Prediction Accuracy: {accuracy_metric}%")
        # --- ACCURACY CALCULATION END ---
        
        # 5. Format Results
        # Model returns 1 for Legitimate, -1 for Phishing
        phishing_count = int(np.sum(predictions == -1)) 
        legitimate_count = int(np.sum(predictions == 1)) 
        total_count = len(predictions)
        
        # Combine input features with predictions for detailed output
        X_processed['Prediction'] = predictions.tolist()
        
        result = {
            "status": "success",
            "total_urls": total_count,
            "phishing_count": phishing_count,
            "legitimate_count": legitimate_count,
            "detailed_results": X_processed[['Prediction']].to_dict('records') 
        }
        
        # 🛑 Add accuracy to the result dictionary if calculated
        if accuracy_metric is not None:
            result['accuracy'] = accuracy_metric
            
        return result