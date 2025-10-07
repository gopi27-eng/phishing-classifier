import pandas as pd
from pymongo import MongoClient
import sys
# Assuming your CustomException is defined in src.exception
from src.exception import CustomException 
from typing import Dict, Any, List, Optional # Ensure Optional is imported

class mongo_operation:
    """
    A class to handle MongoDB operations, primarily for fetching data 
    and returning it as a pandas DataFrame.
    """
    
    def __init__(self, client_url: str, database_name: str, collection_name: str):
        """
        Initializes the MongoDB client connection.
        """
        try:
            self.client = MongoClient(client_url)
            self.database = self.client[database_name]
            self.collection = self.database[collection_name]
            print(f"MongoDB connection established for collection: {collection_name}")
            
        except Exception as e:
            raise CustomException(str(e), sys)

    # FIX: Use Optional[Dict[str, Any]] to allow the query argument to be None
    def find(self, query: Optional[Dict[str, Any]] = None) -> pd.DataFrame: 
        """
        Fetches all documents from the initialized collection that match the query 
        and returns them as a pandas DataFrame.
        
        :param query: A dictionary representing the MongoDB query filter.
        :return: A pandas DataFrame containing the fetched data.
        """
        # This code path is now correctly typed
        if query is None:
            query = {}
            
        try:
            # 1. Fetch data from MongoDB as a list of dictionaries
            data: List[Dict] = list(self.collection.find(query))
            
            if not data:
                # Return an empty DataFrame when no data is found
                print(f"WARNING: No data found in collection '{self.collection.name}'.")
                return pd.DataFrame()
            
            # 2. Convert the list of dicts directly to a DataFrame
            df = pd.DataFrame(data)
            
            # 3. Clean up the connection and return the DataFrame
            self.close_connection()
            
            return df

        except Exception as e:
            self.close_connection()
            # The 'raise' statement correctly terminates the function, 
            # satisfying the return type contract (by not completing execution).
            raise CustomException(str(e), sys)

    def close_connection(self):
        """Closes the MongoDB client connection."""
        if self.client:
            self.client.close()
            # print("MongoDB connection closed by mongo_operation.")


# --- Example Usage (Optional - for testing the module) ---
if __name__ == '__main__':
    print("This module defines the mongo_operation class for MongoDB access.")