import logging
import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential
import os
import uuid
import json
from datetime import datetime
import time
from typing import List, Dict, Any, Optional
from PIL import Image
from io import BytesIO
import requests  # For REST API to Vision
from pdf2image import convert_from_bytes  # For PDF to image conversion

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

## DEFINITIONS 
def initialize_form_recognizer_client() -> DocumentAnalysisClient:
    endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("FORM_RECOGNIZER_KEY")
    if not isinstance(key, str):
        raise ValueError("FORM_RECOGNIZER_KEY must be a string")
    logging.info(f"Form Recognizer endpoint: {endpoint}")
    return DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def read_pdf_content(myblob: func.InputStream) -> bytes:
    logging.info(f"Reading PDF content from blob: {myblob.name}")
    return myblob.read()

def analyze_pdf(form_recognizer_client: DocumentAnalysisClient, pdf_bytes: bytes) -> AnalyzeResult:
    logging.info("Starting PDF layout analysis.")
    poller = form_recognizer_client.begin_analyze_document(
        model_id="prebuilt-layout",
        document=pdf_bytes
    )
    logging.info("PDF layout analysis in progress.")
    result = poller.result()
    logging.info("PDF layout analysis completed.")
    num_pages = len(result.pages) if hasattr(result, "pages") and isinstance(result.pages, list) else 0
    num_tables = len(result.tables) if hasattr(result, "tables") and isinstance(result.tables, list) else 0
    num_styles = len(result.styles) if hasattr(result, "styles") and result.styles is not None else 0
    logging.info(f"Document has {num_pages} page(s), {num_tables} table(s), and {num_styles} style(s).")
    return result

def extract_layout_data(result: AnalyzeResult, visual_cues: Optional[List[Dict[str, Any]]] = None, source_file: str = "unknown") -> Dict[str, Any]:
    logging.info("Extracting layout data from analysis result.")

    layout_data = {
        "id": str(uuid.uuid4()),
        "metadata": {
            "processed_at": datetime.utcnow().isoformat(),
            "source_file": source_file,
            "pages_count": len(result.pages) if hasattr(result, "pages") else 0,
            "tables_count": len(result.tables) if hasattr(result, "tables") else 0,
            "visual_cues_count": len(visual_cues) if visual_cues else 0
        },
        "pages": []
    }
    visual_cues = visual_cues or []  # List of dicts with visual cue info per cell

    # Log styles
    if hasattr(result, "styles") and result.styles:
        for idx, style in enumerate(result.styles):
            content_type = "handwritten" if style.is_handwritten else "no handwritten"
            logging.info(f"Document contains {content_type} content")

    # Process each page
    for page in result.pages:
        logging.info(f"--- Page {page.page_number} ---")
        page_data = {
            "page_number": page.page_number,
            "lines": [line.content for line in page.lines],
            "tables": [],
            "selection_marks": [
                {"state": mark.state, "confidence": mark.confidence}
                for mark in page.selection_marks
            ] if hasattr(page, 'selection_marks') and page.selection_marks else []
        }

        # Log extracted lines
        for line_idx, line in enumerate(page.lines):
            logging.info(f"Line {line_idx}: '{line.content}'")

        # Log selection marks
        if hasattr(page, 'selection_marks') and page.selection_marks:
            for selection_mark in page.selection_marks:
                logging.info(
                    f"Selection mark is '{selection_mark.state}' with confidence {selection_mark.confidence}"
                )

        # Extract tables
        page_tables = [
            table for table in result.tables
            if any(region.page_number == page.page_number for region in table.bounding_regions)
        ] if hasattr(result, 'tables') and result.tables else []

        for table_index, table in enumerate(page_tables):
            logging.info(f"Table {table_index}: {table.row_count} rows, {table.column_count} columns")

            table_data = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": []
            }

            for cell in table.cells:
                content = cell.content.strip()
                # Find matching visual cue for this cell (if any)
                cue = next((vc for vc in visual_cues if vc.get("page_number") == page.page_number and vc.get("row_index") == cell.row_index and vc.get("column_index") == cell.column_index), None)
                cell_info = {
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "content": content,
                    "visual_cue": cue["cue_type"] if cue else None
                }
                table_data["cells"].append(cell_info)
                logging.info(f"Cell[{cell.row_index}][{cell.column_index}]: '{content}', visual_cue: {cell_info['visual_cue']}")

            page_data["tables"].append(table_data)

        layout_data["pages"].append(page_data)

    try:
        preview = json.dumps(layout_data, indent=2)
        logging.info("Structured layout data preview:\n" + preview)
    except Exception as e:
        logging.warning(f"Could not serialize layout data for preview: {e}")

    return layout_data

def save_layout_data_to_cosmos(layout_data: Dict[str, Any]) -> None:
    try:
        endpoint = os.getenv("COSMOS_DB_ENDPOINT")
        key = os.getenv("COSMOS_DB_KEY")
        aad_credentials = DefaultAzureCredential()
        client = CosmosClient(endpoint, credential=aad_credentials, consistency_level='Session')
        logging.info("Successfully connected to Cosmos DB using AAD default credential")
    except Exception as e:
        logging.error(f"Error connecting to Cosmos DB: {e}")
        return
    
    database_name = "ContosoDBDocIntellig"
    container_name = "Layouts"

    try:
        database = client.create_database_if_not_exists(database_name)
        logging.info(f"Database '{database_name}' does not exist. Creating it.")
    except exceptions.CosmosResourceExistsError:
        database = client.get_database_client(database_name)
        logging.info(f"Database '{database_name}' already exists.")

    database.read()
    logging.info(f"Reading into '{database_name}' DB")

    try:
        container = database.create_container(
            id=container_name,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=400
        )
        logging.info(f"Container '{container_name}' does not exist. Creating it.")
    except exceptions.CosmosResourceExistsError:
        container = database.get_container_client(container_name)
        logging.info(f"Container '{container_name}' already exists.")
    except exceptions.CosmosHttpResponseError:
        raise

    container.read()
    logging.info(f"Reading into '{container}' container")

    try:
        response = container.upsert_item(layout_data)
        logging.info(f"Saved processed layout data to Cosmos DB. Response: {response}")
    except Exception as e:
        logging.error(f"Error inserting item into Cosmos DB: {e}")

def call_vision_api(image_bytes: bytes, subscription_key: str, endpoint: str, max_retries: int = 3) -> Dict[str, Any]:
    vision_url = endpoint + "/vision/v3.2/analyze"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream'
    }
    params = {
        'visualFeatures': 'Objects,Color,Text',  # Added Text feature for better text detection
        'language': 'en',
        'model-version': 'latest'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(vision_url, headers=headers, params=params, data=image_bytes)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if hasattr(http_err, 'response') and http_err.response.status_code == 429:  # Too Many Requests
                if attempt < max_retries - 1:
                    retry_after = int(http_err.response.headers.get('Retry-After', 1))
                    logging.warning(f"Rate limit hit, waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
            logging.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logging.error(f"Error calling Vision API: {err}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
    
    raise Exception("Max retries exceeded for Vision API call")

def extract_visual_cues_from_vision(vision_result: Dict[str, Any], page_number: int) -> List[Dict[str, Any]]:
    """
    Extract visual cues from Azure Vision API results with enhanced detection capabilities.
    Detects: checkboxes, filled areas, handwritten text, signatures, tables, and form elements
    
    Args:
        vision_result: The response from Azure Vision API
        page_number: Current page being processed
        
    Returns:
        List of detected visual cues with their properties and confidence scores
    """
    cues: List[Dict[str, Any]] = []
    
    if not vision_result:
        logging.warning(f"Empty vision result for page {page_number}")
        return cues
    
    # Enhanced object detection with better classification
    if 'objects' in vision_result:
        for obj in vision_result['objects']:
            if 'rectangle' in obj:
                rect = obj['rectangle']
                x, y = rect.get('x', 0), rect.get('y', 0)
                w, h = rect.get('w', 0), rect.get('h', 0)
                confidence = obj.get('confidence', 0.0)
                
                # Improved checkbox detection with confidence threshold
                if 0.8 <= w/h <= 1.2 and 10 <= w <= 50 and 10 <= h <= 50 and confidence > 0.6:
                    cues.append({
                        "page_number": page_number,
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h,
                        "cue_type": "checkbox",
                        "confidence": confidence,
                        "metadata": {
                            "aspect_ratio": w/h,
                            "area": w * h
                        }
                    })
                
                # Detect possible table structures
                elif w > 100 and h > 100 and 'table' in obj.get('tags', []):
                    cues.append({
                        "page_number": page_number,
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h,
                        "cue_type": "table",
                        "confidence": confidence
                    })

    # Enhanced color analysis for form elements
    if 'color' in vision_result:
        color_info = vision_result['color']
        dominant_colors = color_info.get('dominantColors', [])
        for color in dominant_colors:
            color_lower = color.lower()
            if color_lower in ['gray', 'grey']:
                cues.append({
                    "page_number": page_number,
                    "cue_type": "filled_area",
                    "color": color_lower,
                    "confidence": color_info.get('dominantColorConfidence', 0.0),
                    "metadata": {
                        "color_scheme": color_info.get('accentColor'),
                        "is_black_and_white": color_info.get('isBWImg', False)
                    }
                })

    # Enhanced text analysis with better handwriting and signature detection
    if 'text' in vision_result:
        for text_result in vision_result.get('text', {}).get('lines', []):
            content = text_result.get('content', '').strip()
            confidence = text_result.get('confidence', 0.0)
            
            if text_result.get('isHandwritten', False):
                cue_type = "signature" if _is_likely_signature(content) else "handwritten"
                cues.append({
                    "page_number": page_number,
                    "text": content,
                    "cue_type": cue_type,
                    "confidence": confidence,
                    "metadata": {
                        "length": len(content),
                        "position": text_result.get('boundingBox', {}),
                        "detected_language": text_result.get('language', 'unknown')
                    }
                })

    # Log what we found
    if cues:
        logging.info(f"Found {len(cues)} visual cues on page {page_number}: {[c['cue_type'] for c in cues]}")
    else:
        logging.info(f"No visual cues detected on page {page_number}")

    return cues

def _is_likely_signature(text: str) -> bool:
    """
    Detect if the given text is likely to be a signature based on heuristics.
    
    Args:
        text: The text content to analyze
        
    Returns:
        bool: True if the text matches signature patterns
    """
    # Common signature indicators
    signature_indicators = [
        lambda t: len(t.split()) <= 3,  # Most signatures are 1-3 words
        lambda t: any(c.isalpha() for c in t),  # Contains letters
        lambda t: len(t) < 50,  # Not too long
        lambda t: not t.isupper(),  # Not all uppercase (unlikely for signatures)
        lambda t: not any(c.isdigit() for c in t)  # Usually no numbers in signatures
    ]
    
    return all(indicator(text) for indicator in signature_indicators)

def convert_pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    images = convert_from_bytes(pdf_bytes)
    return images

def extract_skill_selections_from_table(table_data):
    """
    Given a table_data dict (as in your layout_data['pages'][x]['tables'][y]),
    returns a list of dicts: [{"skill": ..., "selected": ...}, ...]
    Assumes first column is skill name, columns 2-7 are options 0-5.
    """
    skills = []
    for row in range(table_data["row_count"]):
        skill_name = None
        selected = None
        for cell in table_data["cells"]:
            if cell["row_index"] == row:
                col = cell["column_index"]
                content = cell["content"].replace("\n", " ").strip()
                # First column is skill name
                if col == 0:
                    skill_name = content
                # Columns 2-7 are options 0-5
                elif 2 <= col <= 7:
                    if ":selected:" in content:
                        selected = col - 2  # 0-based
        if skill_name and selected is not None:
            skills.append({"skill": skill_name, "selected": selected})
    return skills

def infer_table_title(table_data, page_lines):
    """
    Try to infer the table title by looking for text above the table or in the first row/merged cells.
    page_lines: list of all lines on the page (in order)
    """
    # Find the minimum row_index in the table (should be 0)
    min_row = min(cell["row_index"] for cell in table_data["cells"])
    # Get all cells in the first row
    first_row_cells = [cell for cell in table_data["cells"] if cell["row_index"] == min_row]
    # If any cell in the first row spans all columns, treat as title
    for cell in first_row_cells:
        if cell.get("column_span", 1) == table_data["column_count"] and cell["content"].strip():
            return cell["content"].strip()
    # Otherwise, look for a line above the first row that is not in the table
    # Find the topmost cell's content
    top_cell_content = None
    if first_row_cells:
        top_cell_content = first_row_cells[0]["content"].strip()
    # Try to find a line above the table that is not the top cell content
    if page_lines and top_cell_content:
        for idx, line in enumerate(page_lines):
            if line.strip() == top_cell_content and idx > 0:
                # Return the previous line as the title
                prev_line = page_lines[idx-1].strip()
                if prev_line:
                    return prev_line
    # Fallback: use the top cell content if not empty
    if top_cell_content:
        return top_cell_content
    return "Unknown Table"

@app.blob_trigger(arg_name="myblob", path="pdfinvoices/{name}",
                  connection="invoicecontosostorage_STORAGE")
def BlobTriggerContosoPDFLayoutsDocIntelligence(myblob: func.InputStream) -> None:
    logging.info(f"Python blob trigger function processed blob\n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    try:
        form_recognizer_client = initialize_form_recognizer_client()
        pdf_bytes = read_pdf_content(myblob)
        logging.info("Successfully read PDF content from blob.")
    except Exception as e:
        logging.error(f"Error reading PDF: {e}")
        return

    try:
        result = analyze_pdf(form_recognizer_client, pdf_bytes)
        logging.info("Successfully analyzed PDF using Document Intelligence.")
    except Exception as e:
        logging.error(f"Error analyzing PDF: {e}")
        return

    # --- Step: Convert PDF to image and call Azure AI Vision ---
    visual_cues = []
    try:
        # Validate Vision API credentials
        vision_key = os.getenv("VISION_API_KEY")
        vision_endpoint = os.getenv("VISION_API_ENDPOINT")
        
        if not vision_key or not vision_endpoint:
            logging.warning("Vision API credentials not configured - skipping visual cue detection")
        else:
            images = convert_pdf_to_images(pdf_bytes)
            if not images:
                logging.warning("No images extracted from PDF")
            else:
                for page_num, image in enumerate(images, start=1):
                    img_bytes_io = BytesIO()
                    image.save(img_bytes_io, format='JPEG')
                    img_bytes = img_bytes_io.getvalue()
                    vision_result = call_vision_api(img_bytes, vision_key, vision_endpoint)
                    cues = extract_visual_cues_from_vision(vision_result, page_num)
                    visual_cues.extend(cues)
                logging.info(f"Visual cues extracted: {visual_cues}")
    except Exception as e:
        logging.error(f"Error processing visual cues with AI Vision: {e}")
        # Continue processing without visual cues

    try:
        layout_data = extract_layout_data(result, visual_cues, myblob.name)
        logging.info("Successfully extracted and merged layout data.")
    except Exception as e:
        logging.error(f"Error extracting layout data: {e}")
        return

    try:
        save_layout_data_to_cosmos(layout_data)
        logging.info("Successfully saved layout data to Cosmos DB.")
    except Exception as e:
        logging.error(f"Error saving layout data to Cosmos DB: {e}")

    # For each table, infer the title, create both DataFrame-like and summary JSON, log both, and save only the summary JSON
    for page in layout_data["pages"]:
        page_lines = page.get("lines", [])
        for table in page["tables"]:
            # --- Table Title Inference ---
            table_title = infer_table_title(table, page_lines)

            # --- DataFrame-like JSON ---
            # Build a 2D array of cell contents
            df_like = [[None for _ in range(table["column_count"])] for _ in range(table["row_count"]) ]
            for cell in table["cells"]:
                r, c = cell["row_index"], cell["column_index"]
                df_like[r][c] = cell["content"].strip()
            df_json = {
                "table_title": table_title,
                "data": df_like
            }

            # --- Pretty-print table as grid ---
            def pretty_print_table(table_title, df_like):
                # Find max width for each column
                if not df_like or not df_like[0]:
                    return "(Empty table)"
                col_widths = [max(len(str(row[c])) if row[c] is not None else 0 for row in df_like) for c in range(len(df_like[0]))]
                lines = []
                lines.append(f"Table: {table_title}")
                border = "+" + "+".join("-" * (w+2) for w in col_widths) + "+"
                lines.append(border)
                for i, row in enumerate(df_like):
                    row_str = "|" + "|".join(f" {str(cell) if cell is not None else '' :<{col_widths[j]}} " for j, cell in enumerate(row)) + "|"
                    lines.append(row_str)
                    lines.append(border)
                return "\n".join(lines)

            pretty_table_str = pretty_print_table(table_title, df_like)
            logging.info(f"\n{pretty_table_str}")

            # --- Summary JSON ---
            skill_selections = extract_skill_selections_from_table(table)
            summary = {
                "table_title": table_title,
                "skills": skill_selections
            }

            # Log both outputs for user inspection
            logging.info(f"Table DataFrame-like JSON: {json.dumps(df_json, indent=2)}")
            logging.info(f"Table summary JSON: {json.dumps(summary, indent=2)}")
            # Only save the summary JSON if needed (e.g., to Cosmos DB or elsewhere)
            # (Current implementation saves only the main layout_data to Cosmos DB)
