# src/utils/data_loader.py

import pickle
import boto3
import os # Import the configuration object
from ..config.config import Config
def load_model_from_s3():
    """
    Connects to AWS S3, downloads the ML model file, and loads it into memory.
    
    Returns:
        The deserialized machine learning model object.
    """
    try:
        print(f"Attempting to connect to S3 bucket: {Config.S3_BUCKET_NAME}")
        
        # Initialize the S3 client using credentials from Config
        s3 = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION
        )
        
        # Download the file from S3 to a temporary local path
        s3.download_file(
            Bucket=Config.S3_BUCKET_NAME,
            Key=Config.MODEL_S3_KEY,
            Filename=Config.LOCAL_MODEL_PATH
        )
        
        print(f"Model '{Config.MODEL_S3_KEY}' successfully downloaded from S3.")
        
        # Load the model from the temporary file
        with open(Config.LOCAL_MODEL_PATH, 'rb') as file:
            model = pickle.load(file)
            
        # Clean up the temporary file (optional, but good practice)
        os.remove(Config.LOCAL_MODEL_PATH)
        
        return model

    except Exception as e:
        print(f"Error loading model from S3: {e}")
        # In a production system, you might fall back to a local model or raise a critical error
        raise ConnectionError("Failed to load machine learning model from AWS S3.")