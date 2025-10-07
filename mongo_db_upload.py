import pandas as pd
from pymongo import MongoClient
import os
from pprint import pprint



# NOTE: Use the correct, full connection string from MongoDB Atlas, 
# including the username and password you set. 
# **Always protect your credentials!**
# Update MONGO_URI (Line 10)
MONGO_URI = "mongodb+srv://Gopi27:Gopiborra@cluster0.ytrhnxg.mongodb.net/"

# This variable is now redundant if the name is in the URI, but keep it for clarity
DATABASE_NAME = "phishing_classifier" 

COLLECTION_NAME = "phishing_mails"

client = MongoClient(MONGO_URI)
# The database name will be read from the URI, or you can explicitly use the variable:
db = client[DATABASE_NAME] 
collection = db[COLLECTION_NAME]


# to the main 'phishing-classifier' folder where your 'phishing.csv' is located.
FILE_PATH = r"C:\sync data\Desktop\phishing -classifier\notebook implementaions\phising.csv"



# --- 2. DATA LOADING AND INSERTION ---

try:
    print(f"Attempting to load data from: {FILE_PATH}...")
    
    # Read the file into a Pandas DataFrame
    if FILE_PATH.lower().endswith('.csv'):
        # Assuming the CSV has a header row
        df = pd.read_csv(FILE_PATH)
    elif FILE_PATH.lower().endswith('.json'):
        df = pd.read_json(FILE_PATH)
    else:
        print("ERROR: Unsupported file type. Please use .csv or .json.")
        exit()
        
    print(f"Successfully read {len(df)} records.")
    
    #  Convert DataFrame to list of dictionaries
    # The 'records' orientation creates one dictionary per row.
    data_records = df.to_dict('records')

    #  Connect to MongoDB Atlas
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    #  Insert the data
    print(f"Connecting to MongoDB and inserting data into {DATABASE_NAME}.{COLLECTION_NAME}...")
    result = collection.insert_many(data_records)
    
    # --- SUCCESS MESSAGE ---
    print("\n==============================")
    print("✨ INSERTION COMPLETE! ✨")
    print(f"Total documents inserted: {len(result.inserted_ids)}")
    print("==============================")
    print(f"First inserted ID: {result.inserted_ids[0]}")
    
except FileNotFoundError:
    print("\n--- FATAL ERROR: FILE NOT FOUND ---")
    print(f"Double-check that the file name and path are correct: {FILE_PATH}")
    print("If the file is in a different folder, adjust the FILE_PATH variable.")
    
except Exception as e:
    # Handles issues like connection errors, authentication failures, etc.
    print(f"\n--- DATABASE ERROR ---")
    print(f"An unexpected error occurred during import: {e}")
    print("Check your MONGO_URI, username, password, and network access settings in Atlas.")

finally:
    #  Ensure the connection is closed
    if 'client' in locals() and client:
        client.close()
        print("\nMongoDB connection closed.")