"""
Validation Helper Functions
Environment validation and configuration checking
"""

import os
import logging


def validate_required_env_vars(required_vars):
    """Validate that required environment variables are set"""
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {missing_vars}"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    logging.info("All required environment variables are set")
    return True
