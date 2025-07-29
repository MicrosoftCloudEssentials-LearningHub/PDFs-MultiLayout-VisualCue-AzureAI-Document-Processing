"""
Modular PDF Layout Extraction with Azure AI Document Intelligence
Supporting Multiple Document Versions with Visual Selection Cues

This Azure Function provides comprehensive PDF analysis using Azure's built-in capabilities:
1. Azure Document Intelligence for structured extraction (primary PDF processing)
2. Azure AI Vision for image analysis (complementary visual processing)
3. Azure OpenAI for semantic analysis and document understanding
4. Native Azure cloud processing without external dependencies

Modular Architecture:
- Separate module files for different functional areas
- Easier to code, debug, and maintain
- Clear separation of concerns
"""

# IMPORTS AND SETUP
import logging
import azure.functions as func
import time
import traceback
import os
from typing import Dict, Any, List, Optional, Union
from io import BytesIO
from datetime import datetime

# Import functions from modules
from modules.clients.azure_clients import (
    initialize_form_recognizer_client,
    initialize_openai_client,
    get_vision_api_config
)
from modules.processors.document_intelligence import (
    analyze_pdf,
    extract_layout_data
)
from modules.processors.vision_processing import (
    analyze_image_with_vision,
    process_image_file
)
from modules.processors.llm_processing import (
    analyze_content_with_llm,
    prepare_content_for_llm
)
from modules.output.display_manager import (
    display_complete_vision_output,
    display_complete_llm_output,
    display_final_concatenated_output
)
from modules.storage.cosmos_manager import (
    initialize_cosmos_client,
    create_database_if_not_exists,
    create_container_if_not_exists,
    prepare_document_for_storage,
    store_document
)
from modules.utils.file_helpers import generate_document_id, get_file_info
from modules.utils.validation import validate_required_env_vars
from modules.utils.logging_helpers import log_processing_step
from modules.utils.time_helpers import calculate_processing_time

# Initialize the function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# MAIN AZURE FUNCTION
@app.blob_trigger(arg_name="myblob", path="pdfinvoices/{name}",
                  connection="invoicecontosostorage_STORAGE")
def BlobTriggerPDFsMultiLayoutsAIDocIntelligence(myblob: func.InputStream) -> None:
    """
    Blob trigger Azure Function for comprehensive PDF document analysis
    Processes PDF files using Azure Document Intelligence, AI Vision, and OpenAI
    """
    start_time = datetime.now()
    
    try:
        # Get blob information
        blob_name = myblob.name
        file_content = myblob.read()
        
        log_processing_step("Starting Document Analysis", f"Processing blob: {blob_name}")
        
        # Validate required environment variables
        required_env_vars = [
            "FORM_RECOGNIZER_ENDPOINT",
            "FORM_RECOGNIZER_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_KEY",
            "AZURE_OPENAI_GPT4_DEPLOYMENT",
            "VISION_API_ENDPOINT",
            "VISION_API_KEY"
        ]
        validate_required_env_vars(required_env_vars)
        
        # Generate unique document ID
        document_id = generate_document_id()
        
        # Extract filename from blob path
        original_filename = blob_name.split('/')[-1] if '/' in blob_name else blob_name
        
        log_processing_step("File Processing", f"Processing file: {original_filename}")
        
        # Initialize Azure clients
        log_processing_step("Client Initialization", "Setting up Azure service clients")
        
        # Initialize Form Recognizer client
        form_recognizer_client = initialize_form_recognizer_client()

        # Initialize OpenAI client
        openai_client = initialize_openai_client()

        # Get Vision API configuration
        vision_config = get_vision_api_config()
        
        # DOCUMENT INTELLIGENCE PROCESSING
        log_processing_step("Document Intelligence Analysis", "Analyzing PDF with Azure Document Intelligence")
        
        # Analyze PDF with Document Intelligence
        document_result = analyze_pdf(form_recognizer_client, file_content)
        
        # Extract layout data
        layout_data = extract_layout_data(document_result)
        
        # Add document ID and filename to layout data
        layout_data["document_id"] = document_id
        layout_data["filename"] = original_filename
        
        log_processing_step("Document Intelligence Complete", f"Extracted {len(layout_data.get('pages', []))} pages")
        
        # AI VISION PROCESSING
        log_processing_step("AI Vision Analysis", "Processing with Azure AI Vision")
        
        try:
            # Process with AI Vision for additional insights
            vision_analysis = analyze_image_with_vision(vision_config, file_content)
            
            # Display complete Vision output
            display_complete_vision_output(vision_analysis, "- Azure AI Vision Analysis")
            
            # Add vision analysis to layout data
            layout_data["vision_analysis"] = vision_analysis
            
        except Exception as e:
            logging.warning(f"Vision analysis failed (continuing without it): {e}")
            layout_data["vision_analysis_error"] = str(e)
        
        # LLM SEMANTIC ANALYSIS
        log_processing_step("LLM Semantic Analysis", "Analyzing content with Azure OpenAI")
        
        try:
            # Prepare content for LLM analysis
            prepared_content = prepare_content_for_llm(layout_data, "pdf")

            # Analyze with LLM
            llm_analysis = analyze_content_with_llm(
                openai_client,
                prepared_content,
                deployment_name=os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT")
            )
            
            # Display complete LLM output
            display_complete_llm_output(llm_analysis)
            
            # Add LLM analysis to layout data
            layout_data["llm_analysis"] = llm_analysis
            
        except Exception as e:
            logging.warning(f"LLM analysis failed (continuing without it): {e}")
            layout_data["llm_analysis_error"] = str(e)
        
        # FINAL OUTPUT DISPLAY
        log_processing_step("Final Output Generation", "Displaying complete processing results")
        
        # Display the final concatenated output with all processing results
        display_final_concatenated_output(layout_data)
        
        # OPTIONAL: STORE IN COSMOS DB
        cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_DB_KEY")
        
        if cosmos_endpoint and cosmos_key:
            try:
                log_processing_step("Data Storage", "Storing results in Cosmos DB")
                
                # Initialize Cosmos client and containers
                cosmos_client = initialize_cosmos_client(cosmos_endpoint, cosmos_key)
                database = create_database_if_not_exists(cosmos_client, "DocumentAnalysisDB")
                container = create_container_if_not_exists(database, "ProcessedDocuments")
                
                # Prepare and store document
                document_for_storage = prepare_document_for_storage(layout_data, original_filename)
                stored_doc = store_document(container, document_for_storage)
                
                layout_data["storage_info"] = {
                    "stored": True,
                    "document_id": stored_doc["id"],
                    "timestamp": stored_doc["timestamp"]
                }
                
            except Exception as e:
                logging.warning(f"Storage failed (continuing without it): {e}")
                layout_data["storage_error"] = str(e)
        
        # CALCULATE PROCESSING TIME
        end_time = datetime.now()
        processing_time_info = calculate_processing_time(start_time, end_time)
        
        layout_data["processing_time"] = processing_time_info
        
        log_processing_step(
            "Processing Complete", 
            f"Total time: {processing_time_info['duration_formatted']}"
        )
        
        logging.info(f"Successfully processed blob: {blob_name}")
        
    except Exception as e:
        # Define a default blob name in case we fail early
        blob_info = "unknown blob"
        
        # Only use blob_name if it was defined before the error
        if 'blob_name' in dir(): # safer than using locals()
            blob_info = f"blob {blob_name}"
        
        logging.error(f"Document analysis failed for {blob_info}: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise
