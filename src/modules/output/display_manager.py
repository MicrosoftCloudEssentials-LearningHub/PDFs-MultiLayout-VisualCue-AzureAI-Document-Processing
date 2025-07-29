"""
Output Displayer Module
Handles comprehensive output display for all processing results
"""

import logging
import json


def display_complete_vision_output(vision_result, processing_stage=""):
    """Display complete AI Vision analysis output"""
    logging.info("=" * 80)
    logging.info(f"== COMPLETE AI VISION ANALYSIS OUTPUT {processing_stage} ==")
    logging.info("=" * 80)
    try:
        complete_vision_output = json.dumps(vision_result, indent=2, ensure_ascii=False)
        logging.info(f"Full AI Vision Analysis Results:\n{complete_vision_output}")
    except Exception as e:
        logging.warning(f"Could not display complete Vision analysis: {e}")
        logging.info(f"Vision Analysis (string format): {str(vision_result)}")
    logging.info("=" * 80)


def display_complete_llm_output(llm_result):
    """Display complete LLM analysis output"""
    logging.info("=" * 80)
    logging.info("== COMPLETE LLM ANALYSIS OUTPUT ==")
    logging.info("=" * 80)
    try:
        complete_llm_output = json.dumps(llm_result, indent=2, ensure_ascii=False)
        logging.info(f"Full LLM Analysis Results:\n{complete_llm_output}")
    except Exception as e:
        logging.warning(f"Could not display complete LLM analysis: {e}")
        logging.info(f"LLM Analysis (string format): {str(llm_result)}")
    logging.info("=" * 80)


def display_final_concatenated_output(layout_data):
    """Display the final concatenated output with all processing results"""
    logging.info("=" * 80)
    logging.info("== FINAL CONCATENATED PDF INFORMATION OUTPUT ==")
    logging.info("== ALL PROCESSING RESULTS COMBINED ==")
    logging.info("=" * 80)
    
    try:
        final_complete_output = json.dumps(layout_data, indent=2, ensure_ascii=False)
        logging.info("COMPLETE FINAL OUTPUT (All AI Processing Results):")
        logging.info(final_complete_output)
    except Exception as e:
        logging.warning(f"Could not display complete final output as JSON: {e}")
        _display_structured_fallback(layout_data)
    
    logging.info("=" * 80)
    logging.info("== END OF COMPLETE PDF INFORMATION ==")
    logging.info("=" * 80)


def _display_structured_fallback(layout_data):
    """Fallback structured display when JSON fails"""
    logging.info("COMPLETE FINAL OUTPUT (Structured Display):")
    logging.info(f"Document ID: {layout_data.get('id', 'Unknown')}")
    logging.info(f"File Type: {layout_data.get('file_type', 'Unknown')}")
    logging.info(f"Original Filename: {layout_data.get('original_filename', 'Unknown')}")
    
    # Display pages information
    if 'pages' in layout_data:
        logging.info(f"Number of Pages: {len(layout_data['pages'])}")
        for page_idx, page in enumerate(layout_data['pages']):
            logging.info(f"--- PAGE {page_idx + 1} ---")
            
            if 'lines' in page:
                logging.info(f"Text Lines ({len(page['lines'])}):")
                for line in page['lines']:
                    logging.info(f"  {line}")
            
            if 'tables' in page:
                logging.info(f"Tables ({len(page['tables'])}):")
                for table_idx, table in enumerate(page['tables']):
                    logging.info(f"  Table {table_idx + 1}: {table.get('row_count', 0)} rows × {table.get('column_count', 0)} columns")
                    if 'cells' in table:
                        for cell in table['cells']:
                            logging.info(f"    [R{cell.get('row_index', 0)},C{cell.get('column_index', 0)}]: {cell.get('content', '')}")
    
    # Display Vision Analysis if available
    if 'vision_analysis' in layout_data:
        logging.info("--- AI VISION ANALYSIS ---")
        for key, value in layout_data['vision_analysis'].items():
            logging.info(f"  {key}: {value}")
    
    # Display LLM Analysis if available
    if 'llm_analysis' in layout_data:
        logging.info("--- LLM ANALYSIS ---")
        llm_data = layout_data['llm_analysis']
        if isinstance(llm_data, dict):
            for key, value in llm_data.items():
                logging.info(f"  {key}: {value}")
        else:
            logging.info(f"  {llm_data}")
