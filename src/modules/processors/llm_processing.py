"""
LLM Analyzer Module
Handles Azure OpenAI LLM processing
"""

import logging
import json
import os


def analyze_content_with_llm(client, content_text, deployment_name=None, images=None, prompt=None):
    """Process content using Azure OpenAI with or without images"""
    if not client:
        logging.warning("No Azure OpenAI client available, skipping LLM analysis")
        return None
        
    try:
        if not prompt:
            prompt = """You are an expert document analyzer. Analyze the provided content and extract key information.
            Identify:
            1. Document type (invoice, form, report, etc.)
            2. Key entities (people, companies, places)
            3. Important dates and amounts
            4. Main purpose of the document
            5. Any notable observations
            
            Format your response as a structured JSON with these sections.
            """
        
        # Use the provided deployment or fall back to environment variable
        deployment_id = deployment_name or os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT", "gpt-4")
        messages = [{"role": "system", "content": prompt}]
        
        # Add text content
        messages.append({"role": "user", "content": content_text[:8000]})
        
        # Add image content if available
        if images and len(images) > 0:
            content_items = [{"type": "text", "text": "Analyze this document:"}]
            
            for i, img_base64 in enumerate(images[:5]):
                content_items.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                })
            
            messages.append({"role": "user", "content": content_items})
        
        logging.info(f"Calling Azure OpenAI with deployment: {deployment_id}")
        response = client.chat.completions.create(
            model=deployment_id,
            messages=messages,
            max_tokens=1024,
            temperature=0.0
        )
        
        result_text = response.choices[0].message.content
        
        # Try to parse JSON response
        try:
            if "```json" in result_text and "```" in result_text.split("```json", 1)[1]:
                json_str = result_text.split("```json", 1)[1].split("```", 1)[0]
                result = json.loads(json_str)
            else:
                result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"analysis": result_text}
            
        logging.info("Successfully received and processed LLM response")
        return result
        
    except Exception as e:
        logging.error(f"Error in LLM processing: {e}")
        return {"error": str(e)}


def prepare_content_for_llm(layout_data, file_format):
    """Prepare content text from layout data for LLM processing"""
    content_text = ""
    
    if file_format == 'pdf':
        for page in layout_data['pages']:
            content_text += f"\n--- PAGE {page['page_number']} ---\n"
            content_text += "\n".join(page['lines'])
            
            for i, table in enumerate(page['tables']):
                content_text += f"\n--- TABLE {i+1} ---\n"
                for cell in table['cells']:
                    content_text += f"[Row {cell['row_index']}, Col {cell['column_index']}]: {cell['content']}\n"
    elif file_format == 'image':
        content_text = f"Image caption: {layout_data['vision_analysis']['caption']}\n"
        content_text += "Extracted text:\n"
        for line in layout_data['pages'][0]['lines']:
            content_text += f"{line}\n"
    
    return content_text
