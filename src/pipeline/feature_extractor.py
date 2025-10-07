# src/pipeline/feature_extractor.py

import pandas as pd
from typing import List

# These are the 30 features your model was trained on (derived from your CSV snippet)
EXPECTED_FEATURES: List[str] = [
    "having_IP_Address", "URL_Length", "Shortining_Service", "having_At_Symbol", 
    "double_slash_redirecting", "Prefix_Suffix", "having_Sub_Domain", "SSLfinal_State", 
    "Domain_registeration_length", "Favicon", "port", "HTTPS_token", 
    "Request_URL", "URL_of_Anchor", "Links_in_tags", "SFH", 
    "Submitting_to_email", "Abnormal_URL", "Redirect", "on_mouseover", 
    "RightClick", "popUpWidnow", "Iframe", "age_of_domain", 
    "DNSRecord", "web_traffic", "Page_Rank", "Google_Index", 
    "Links_pointing_to_page", "Statistical_report"
]

def preprocess_input_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates and prepares the raw DataFrame for model prediction.

    :param raw_df: DataFrame loaded directly from the user's uploaded CSV.
    :return: DataFrame containing only the expected features, in the correct order.
    :raises ValueError: If the input data is invalid (e.g., missing columns).
    """
    
    # 1. Check for required columns
    missing_cols = [col for col in EXPECTED_FEATURES if col not in raw_df.columns]
    if missing_cols:
        raise ValueError(
            f"Input CSV is missing required features. Missing columns: {', '.join(missing_cols)}"
        )
    
    # 2. Select and reorder columns (MUST be done in the same order as model training)
    X_processed = raw_df[EXPECTED_FEATURES]

    # 3. Enforce Numeric Type
    try:
        # Convert to numeric, raising an error if non-numeric data is found
        X_processed = X_processed.apply(pd.to_numeric, errors='raise')
    except Exception as e:
        raise ValueError(f"Feature data must be numeric (-1, 0, 1). Error during conversion: {e}")

    return X_processed