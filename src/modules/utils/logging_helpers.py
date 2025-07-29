"""
Logging Helper Functions
Utilities for consistent logging and formatting
"""

import logging
from datetime import datetime


def log_processing_step(step_name, details=None):
    """Log a processing step with consistent formatting"""
    separator = "-" * 50
    logging.info(separator)
    logging.info(f"PROCESSING STEP: {step_name}")
    if details:
        logging.info(f"Details: {details}")
    logging.info(f"Timestamp: {format_timestamp()}")
    logging.info(separator)


def format_timestamp(timestamp=None):
    """Format timestamp for logging and display"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")
