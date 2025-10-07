# deploy_model_to_s3.py

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

# --- Configuration ---
# Ensure you have already run 'pip install boto3 python-dotenv'

# 1. Load environment variables from .env for secure access
load_dotenv()

# Get settings from environment variables
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
# deploy_model_to_s3.py (After Fix)
LOCAL_FILE_PATH = "notebook implementaions/models/rf_best_model.pkl" # Make sure this path is correct
S3_OBJECT_KEY = os.getenv("MODEL_S3_KEY", "phishing_detector.pkl")

# --- Function to Create Bucket (if needed) ---
def create_s3_bucket(s3_client, bucket_name, region):
    """Creates the S3 bucket if it doesn't already exist."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists. Skipping creation.")
    except ClientError as e:
        # If a 404 error is returned, the bucket does not exist
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"Bucket '{bucket_name}' not found. Creating bucket...")
            
            # Note: US East (N. Virginia) 'us-east-1' does not require LocationConstraint
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            print(f"Bucket '{bucket_name}' created successfully in region {region}.")
        else:
            raise e
            
# --- Function to Upload File ---
def upload_model_to_s3():
    """Uploads the local model file to the specified S3 bucket."""
    
    # 1. Validate local file existence
    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"ERROR: Local model file not found at path: {LOCAL_FILE_PATH}")
        print("HINT: Ensure your trained model is saved here.")
        return False

    # 2. Initialize S3 Client
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
    except Exception as e:
        print(f"Failed to initialize S3 client: {e}")
        return False

    # 3. Handle Bucket and Upload
    try:
        # First, ensure the bucket exists
        create_s3_bucket(s3, BUCKET_NAME, os.getenv("AWS_REGION"))
        
        # Second, upload the file
        print(f"Uploading {LOCAL_FILE_PATH} to s3://{BUCKET_NAME}/{S3_OBJECT_KEY}...")
        s3.upload_file(
            Filename=LOCAL_FILE_PATH,
            Bucket=BUCKET_NAME,
            Key=S3_OBJECT_KEY
        )
        print("\n✅ Model upload successful!")
        return True

    except NoCredentialsError:
        print("\nERROR: AWS credentials not found. Check your .env file or AWS configuration.")
        return False
    except ClientError as e:
        print(f"\nERROR: S3 client error during upload: {e}")
        print("HINT: Check if the bucket name is valid or if your IAM user has s3:PutObject permissions.")
        return False

# --- Execution ---
if __name__ == "__main__":
    if BUCKET_NAME and S3_OBJECT_KEY:
        upload_model_to_s3()
    else:
        print("FATAL ERROR: S3_BUCKET_NAME or MODEL_S3_KEY not set in .env file.")