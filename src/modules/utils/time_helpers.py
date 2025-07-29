"""
Time Helper Functions
Utilities for time calculations and processing
"""

from datetime import datetime


def calculate_processing_time(start_time, end_time=None):
    """Calculate processing time duration"""
    if end_time is None:
        end_time = datetime.now()
    
    duration = end_time - start_time
    return {
        "duration_seconds": duration.total_seconds(),
        "duration_formatted": str(duration),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
