"""
Vision Analyzer Module
Handles Azure AI Vision API processing
"""

import logging
import uuid
import time
import requests
from io import BytesIO


def analyze_image_with_vision(image_bytes, vision_config, request_id=None):
    """Analyze an image using Azure AI Vision API"""
    if not vision_config.get("endpoint") or not vision_config.get("key"):
        logging.warning("Vision API configuration is missing, skipping vision analysis")
        return None
    
    req_id = request_id or str(uuid.uuid4())[:8]
    logging.info(f"[Vision-{req_id}] Starting image analysis with Azure AI Vision")
    
    vision_endpoint = vision_config.get("endpoint")
    vision_key = vision_config.get("key")
    current_version = vision_config.get("version", "2024-04-01")
    
    try:
        # Build API URL based on version
        if current_version.startswith("2024"):
            analyze_url = f"{vision_endpoint}/computervision/imageanalysis:analyze?api-version={current_version}&features=caption,read"
        else:
            analyze_url = f"{vision_endpoint}/computervision/imageanalysis:analyze?api-version={current_version}&features=caption,read"
        
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': vision_key,
            'x-ms-client-request-id': req_id
        }
        
        logging.info(f"[Vision-{req_id}] Making request to: {analyze_url}")
        
        start_time = time.time()
        response = requests.post(analyze_url, headers=headers, data=image_bytes, timeout=30)
        api_latency = time.time() - start_time
        
        logging.info(f"[Vision-{req_id}] Response received in {api_latency:.2f}s with status {response.status_code}")
        
        response.raise_for_status()
        result = response.json()
        
        # Add tracking information
        result['request_id'] = req_id
        result['api_version_used'] = current_version
        
        logging.info(f"[Vision-{req_id}] Successfully processed with API version {current_version}")
        return result
        
    except Exception as e:
        logging.error(f"[Vision-{req_id}] Vision API error: {str(e)}")
        return {
            "error": "Vision API failed",
            "details": str(e),
            "api_version": current_version
        }


def process_image_file(pdf_bytes, vision_config, invocation_id):
    """Process image files using Vision API"""
    vision_result = analyze_image_with_vision(pdf_bytes, vision_config, request_id=invocation_id)
    
    if vision_result and 'error' not in vision_result:
        # Extract text lines from Vision API response
        text_lines = []
        if 'read' in vision_result and 'blocks' in vision_result['read']:
            for block in vision_result['read']['blocks']:
                if 'lines' in block:
                    for line in block['lines']:
                        if 'text' in line:
                            text_lines.append(line['text'])
        
        layout_data = {
            "id": str(uuid.uuid4()),
            "file_type": "image",
            "pages": [{
                "page_number": 1,
                "lines": text_lines,
                "tables": [],
                "selection_marks": []
            }],
            "vision_analysis": {
                "caption": vision_result.get("caption", {}).get("text", ""),
                "confidence": vision_result.get("caption", {}).get("confidence", 0),
                "api_version": vision_config.get("version", "unknown")
            }
        }
        
        return layout_data, vision_result
    else:
        logging.error(f"[Job-{invocation_id}] Vision API processing failed for image")
        return None, None
