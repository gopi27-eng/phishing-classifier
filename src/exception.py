# src/exception.py

import sys

def error_message_detail(error, error_detail: sys):
    """
    Formats the detailed error message including file name, line number, and error message.
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    
    error_message = (
        f"Error occurred in python script name [{file_name}] "
        f"line number [{line_number}] error message [{str(error)}]"
    )
    return error_message

class CustomException(Exception):
    """Base class for custom exceptions in the phishing detection pipeline."""
    
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail=error_detail)
        
    def __str__(self):
        return self.error_message

class S3ModelLoadError(CustomException):
    """Exception raised when the ML model fails to load from S3."""
    
    def __init__(self, message, error_detail: sys):
        super().__init__(f"S3 Model Load Error: {message}", error_detail)

class DataValidationFailure(CustomException):
    """Exception raised when the input CSV data fails feature extraction or validation."""
    
    def __init__(self, message, error_detail: sys):
        super().__init__(f"Data Validation Failure: {message}", error_detail)

class MongoDBConnectionError(CustomException):
    """Exception raised for failures in connecting to or interacting with MongoDB."""
    
    def __init__(self, message, error_detail: sys):
        super().__init__(f"MongoDB Connection Error: {message}", error_detail)