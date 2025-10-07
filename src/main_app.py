import os
import sys
import uuid
from datetime import datetime

import pandas as pd
from flask import Flask, request, jsonify
from pymongo import MongoClient

# Local Project Imports
from .model.predictor import PhishingPredictor
from .config.config import Config
from .exception import *

app = Flask(__name__)

# --- Global Initialization (Run Once at Startup) ---
predictor = None
mongo_client = None
prediction_jobs_collection = None

try:
    # 1. Initialize Predictor (This internally loads the model from S3)
    predictor = PhishingPredictor()

    # 2. Initialize MongoDB Client and verify connection
    print("Attempting to connect to MongoDB...")
    mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Force a connection check (will raise exception if server is down)
    mongo_client.admin.command('ping') 
    
    db = mongo_client[Config.MONGO_DATABASE]
    prediction_jobs_collection = db['prediction_jobs']
    print(f"✅ Connected to MongoDB database: {Config.MONGO_DATABASE}")

except (S3ModelLoadError, MongoDBConnectionError) as e:
    # Handle critical custom startup failures (S3 or DB connection)
    print(f"❌ FATAL STARTUP ERROR: {e.error_message}")
    predictor = None
    mongo_client = None
except Exception as e:
    # Handle any other unexpected startup errors
    custom_error = CustomException(e, sys)
    print(f"❌ FATAL UNEXPECTED STARTUP ERROR: {custom_error.error_message}")
    predictor = None
    mongo_client = None
    
# --- API Endpoint ---
@app.route('/predict', methods=['POST'])
def predict_file():
    job_id = str(uuid.uuid4())
    
    # 1. Check service availability (if model or DB failed at startup)
    if predictor is None or mongo_client is None:
        # Log error using print for visibility, as DB connection might be the failure point
        print(f"Job {job_id} rejected: Service not available due to fatal startup error.")
        return jsonify({"error": "Service not available. Check server startup logs."}), 503

    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['file']
    filename = file.filename
    if not filename.endswith('.csv'):
        return jsonify({"error": "Invalid file type. Please upload a CSV file."}), 400

    # 2. Log job start in MongoDB (Initial PENDING status)
    job_record = {
        "_id": job_id,
        "filename": filename,
        "upload_date": datetime.utcnow(),
        "status": "PENDING",
        "model_version": Config.MODEL_S3_KEY
    }
    prediction_jobs_collection.insert_one(job_record)
    print(f"Processing job {job_id} for file {filename}...")

    try:
        # 3. Read the file directly into a Pandas DataFrame
        raw_df = pd.read_csv(file)
        
        # 4. Run Prediction (Logic in predictor.py will call feature_extractor.py)
        results = predictor.predict(raw_df)

        # 5. Update MongoDB with results (COMPLETED status)
        update_data = {
            "status": "COMPLETED",
            "total_urls": results['total_urls'],
            "phishing_count": results['phishing_count'],
            "legitimate_count": results['legitimate_count'],
            "processed_date": datetime.utcnow()
        }
        prediction_jobs_collection.update_one({"_id": job_id}, {"$set": update_data})
        print(f"Job {job_id} completed successfully.")

        # 6. Return summary to the user
        return jsonify(results), 200

    except DataValidationFailure as e:
        # Handle errors raised from feature_extractor/predictor
        # Log the detailed custom error message internally
        print(f"Job {job_id} failed: {e.error_message}") 
        
        # Update DB to FAILED
        update_data = {"status": "FAILED", "error_message": str(e), "processed_date": datetime.utcnow()}
        prediction_jobs_collection.update_one({"_id": job_id}, {"$set": update_data})
        
        # Return a clean error message to the user (hiding internal details)
        return jsonify({"error": str(e).split('] error message [')[-1].replace(']','')}), 422 
        
    except Exception as e:
        # Handle unexpected errors (e.g., file corruption, internal code bugs)
        custom_error = CustomException(e, sys)
        print(f"Job {job_id} failed unexpectedly: {custom_error.error_message}")
        
        # Update DB to FAILED
        update_data = {"status": "FAILED", "error_message": custom_error.error_message, "processed_date": datetime.utcnow()}
        prediction_jobs_collection.update_one({"_id": job_id}, {"$set": update_data})
        
        return jsonify({"error": "An unexpected server error occurred. Check server logs for job details."}), 500

if __name__ == '__main__':
    print("Starting Flask application...")
    # Using 127.0.0.1 for local development
    app.run(host='127.0.0.1', port=5000, debug=True)