"""
Client Manager Module
Handles initialization of all Azure service clients
"""

import os
import logging
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI


def initialize_form_recognizer_client():
    """Initialize Azure Document Intelligence client"""
    endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("FORM_RECOGNIZER_KEY")
    
    if not isinstance(key, str):
        raise ValueError("FORM_RECOGNIZER_KEY must be a string")
        
    logging.info(f"Form Recognizer endpoint: {endpoint}")
    return DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def initialize_openai_client():
    """Initialize the Azure OpenAI client for LLM processing"""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    key = os.getenv("AZURE_OPENAI_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not endpoint or not key:
        logging.warning("Azure OpenAI configuration missing or incomplete")
        return None
        
    try:
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version=api_version
        )
        logging.info(f"Azure OpenAI client initialized with API version: {api_version}")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Azure OpenAI client: {e}")
        return None


def get_vision_api_config():
    """Get the Vision API configuration from environment variables"""
    key = os.getenv("VISION_API_KEY")
    endpoint = os.getenv("VISION_API_ENDPOINT")
    
    supported_versions = ["2024-04-01", "2024-02-01-preview", "2023-10-01"]
    configured_version = os.getenv("VISION_API_VERSION", "2024-04-01")
    
    config = {
        "key": key,
        "endpoint": endpoint,
        "version": configured_version,
        "fallback_versions": supported_versions
    }
    
    if key and endpoint:
        logging.info(f"Vision API configuration loaded (API version: {configured_version})")
    else:
        logging.warning("Vision API configuration missing or incomplete")
        
    return config
