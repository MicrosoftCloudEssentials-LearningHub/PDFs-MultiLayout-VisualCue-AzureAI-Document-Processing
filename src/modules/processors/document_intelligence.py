"""
Document Processor Module
Handles Document Intelligence processing and data extraction
"""

import logging
import uuid


def analyze_pdf(form_recognizer_client, pdf_bytes):
    """Analyze PDF using Azure Document Intelligence"""
    logging.info("Starting PDF layout analysis.")
    poller = form_recognizer_client.begin_analyze_document(
        model_id="prebuilt-layout",
        document=pdf_bytes
    )
    logging.info("PDF layout analysis in progress.")
    result = poller.result()
    logging.info("PDF layout analysis completed.")
    logging.info(f"Document has {len(result.pages)} page(s), {len(result.tables)} table(s), and {len(result.styles)} style(s).")
    return result


def extract_layout_data(result):
    """Extract structured data from Document Intelligence results"""
    logging.info("Extracting layout data from analysis result.")

    layout_data = {
        "id": str(uuid.uuid4()),
        "pages": []
    }

    # Log styles
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
            ]
        }

        # Log extracted lines
        for line_idx, line in enumerate(page.lines):
            logging.info(f"Line {line_idx}: '{line.content}'")

        # Log selection marks
        for selection_mark in page.selection_marks:
            logging.info(
                f"Selection mark is '{selection_mark.state}' with confidence {selection_mark.confidence}"
            )

        # Extract tables
        page_tables = [
            table for table in result.tables
            if any(region.page_number == page.page_number for region in table.bounding_regions)
        ]

        for table_index, table in enumerate(page_tables):
            logging.info(f"Table {table_index}: {table.row_count} rows, {table.column_count} columns")
            
            table_data = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": []
            }

            for cell in table.cells:
                cell_data = {
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "content": cell.content,
                    "row_span": cell.row_span,
                    "column_span": cell.column_span
                }
                table_data["cells"].append(cell_data)
            
            page_data["tables"].append(table_data)

        layout_data["pages"].append(page_data)

    return layout_data
