# streamlit_app.py (MODIFIED for Accuracy Display)

import streamlit as st
import pandas as pd
import requests
from typing import Dict, Any

# 🛑 FIX FOR StreamlitAPIException: Increase the limit for Pandas Styler rendering
# Set a safe margin to avoid rendering errors on large files
pd.set_option("styler.render.max_elements", 500000)

# --- Configuration ---
# This must match the address where your Flask API is running
API_URL = "http://127.0.0.1:5000/predict" 

# --- Helper Function to Send Data to API (remains the same) ---
def upload_file_and_get_prediction(uploaded_file) -> Dict[str, Any]:
    """Sends the uploaded file to the Flask API for processing."""
    try:
        # Prepare the file for the POST request
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
        
        # Make the request to the Flask API
        response = requests.post(API_URL, files=files, timeout=120) 
        
        # Check for successful API call (HTTP status 200)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            st.error(f"Prediction Error: Data validation failed. Details: {response.json().get('error', 'Check required features.')}")
            return None
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error(f"Connection Error: Could not connect to the Prediction API at {API_URL}. \n\n"
                 "Please ensure your **Flask API is running** (run 'python -m src.main_app') in the first terminal.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Streamlit UI Layout ---
def main():
    st.set_page_config(page_title="Phishing Detection Pipeline", layout="wide")
    
    st.title("🛡️ Enterprise Phishing URL Classifier")
    st.markdown("This application uses an ML model sourced from **AWS S3** and logs job details to **MongoDB**.")
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Upload a CSV file containing the 30 required URL features:", 
        type="csv"
    )

    if uploaded_file is not None:
        
        df = pd.read_csv(uploaded_file)
        st.subheader("1. Raw Data Preview")
        st.dataframe(df.head())

        if st.button("Run Phishing Prediction"):
            
            with st.spinner('Processing data and running model on Flask API...'):
                prediction_summary = upload_file_and_get_prediction(uploaded_file)

            if prediction_summary and prediction_summary.get('status') == 'success':
                
                st.markdown("---")
                st.subheader("2. Prediction Results Summary")
                
                # --- Display Key Metrics ---
                # 🛑 NEW: Use 4 columns to include the Accuracy metric
                if 'accuracy' in prediction_summary:
                    col1, col2, col3, col4 = st.columns(4)
                else:
                    col1, col2, col3 = st.columns(3)
                
                col1.metric("Total Records", prediction_summary['total_urls'])
                col2.metric(
                    "🎣 Phishing URLs", 
                    prediction_summary['phishing_count'], 
                    delta_color="inverse"
                )
                col3.metric(
                    "✅ Legitimate URLs", 
                    prediction_summary['legitimate_count'], 
                    delta_color="normal"
                )
                
                # 🛑 Display Accuracy Metric (Conditional)
                if 'accuracy' in prediction_summary:
                    col4.metric("Model Accuracy", f"{prediction_summary['accuracy']}%")

                # --- Display Detailed Output ---
                st.subheader("3. Detailed Classification")
                
                detailed_df = pd.DataFrame(prediction_summary['detailed_results'])
                final_df = df.copy()
                final_df['Classification'] = detailed_df['Prediction'].apply(lambda x: 'PHISHING (-1)' if x == -1 else 'LEGITIMATE (1)')
                
                st.dataframe(
                    final_df.style.apply(
                        lambda x: ['background-color: #ffcccc' if v == 'PHISHING (-1)' else 'background-color: #ccffcc' for v in x], 
                        subset=['Classification'], 
                        axis=0
                    )
                )
                
                st.success("Analysis Complete! Job logged to MongoDB.")

if __name__ == "__main__":
    main()