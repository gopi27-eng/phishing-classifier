# src/config/config.py

import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the root directory
load_dotenv() 

class Config:
    """
    Centralized configuration management for the application.
    Loads settings from environment variables for security and flexibility.
    """
    
    # ------------------- AWS S3 Settings -------------------
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    MODEL_S3_KEY = os.getenv("MODEL_S3_KEY", "phishing_detector.pkl")
    
    # Path where the model will be temporarily saved locally after downloading
    LOCAL_MODEL_PATH = "temp_phishing_detector.pkl"
    
    # ------------------- MongoDB Settings -------------------
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE", "phishing_db")
    
    @staticmethod
    def validate():
        """Checks for critical missing configurations."""
        required = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_BUCKET_NAME", "MONGO_URI"]
        for key in required:
            if not getattr(Config, key):
                raise ValueError(f"CRITICAL ERROR: Configuration variable '{key}' is missing. Check your .env file.")

# Ensure we have required credentials when the app starts
Config.validate()