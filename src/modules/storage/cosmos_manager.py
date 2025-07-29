"""
Storage Manager Module
Handles data persistence operations with Azure Cosmos DB
"""

import logging
import json
from datetime import datetime
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions


def initialize_cosmos_client(endpoint, key):
    """Initialize and return a Cosmos DB client"""
    return cosmos_client.CosmosClient(endpoint, key)


def create_database_if_not_exists(client, database_name):
    """Create database if it doesn't exist"""
    try:
        database = client.create_database_if_not_exists(id=database_name)
        logging.info(f"Database '{database_name}' ready")
        return database
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Failed to create/access database: {e}")
        raise


def create_container_if_not_exists(database, container_name, partition_key_path="/id"):
    """Create container if it doesn't exist"""
    try:
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key={"paths": [partition_key_path], "kind": "Hash"},
            offer_throughput=400
        )
        logging.info(f"Container '{container_name}' ready")
        return container
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Failed to create/access container: {e}")
        raise


def prepare_document_for_storage(layout_data, original_filename=None):
    """Prepare the layout data for storage with metadata"""
    document = {
        "id": layout_data.get("id", f"doc_{int(datetime.now().timestamp())}"),
        "timestamp": datetime.now().isoformat(),
        "original_filename": original_filename or layout_data.get("original_filename", "unknown"),
        "file_type": layout_data.get("file_type", "pdf"),
        "processing_status": "completed",
        "content": layout_data
    }
    
    # Ensure all nested data is JSON serializable
    try:
        json.dumps(document)
    except (TypeError, ValueError) as e:
        logging.warning(f"Document contains non-serializable data: {e}")
        document["content"] = str(layout_data)
        document["serialization_issue"] = str(e)
    
    return document


def store_document(container, document):
    """Store document in Cosmos DB container"""
    try:
        stored_item = container.create_item(body=document)
        logging.info(f"Document stored successfully with ID: {stored_item['id']}")
        return stored_item
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Failed to store document: {e}")
        raise


def retrieve_document(container, document_id, partition_key=None):
    """Retrieve document from Cosmos DB container"""
    try:
        if partition_key is None:
            partition_key = document_id
        
        item = container.read_item(item=document_id, partition_key=partition_key)
        logging.info(f"Document retrieved successfully: {document_id}")
        return item
    except exceptions.CosmosResourceNotFoundError:
        logging.warning(f"Document not found: {document_id}")
        return None
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Failed to retrieve document: {e}")
        raise


def query_documents(container, query, parameters=None):
    """Query documents from Cosmos DB container"""
    try:
        items = list(container.query_items(
            query=query,
            parameters=parameters or [],
            enable_cross_partition_query=True
        ))
        logging.info(f"Query returned {len(items)} documents")
        return items
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Failed to query documents: {e}")
        raise


def update_document(container, document_id, updates, partition_key=None):
    """Update an existing document in Cosmos DB"""
    try:
        if partition_key is None:
            partition_key = document_id
            
        # First retrieve the existing document
        existing_doc = retrieve_document(container, document_id, partition_key)
        if not existing_doc:
            raise ValueError(f"Document {document_id} not found for update")
        
        # Apply updates
        existing_doc.update(updates)
        existing_doc["last_updated"] = datetime.now().isoformat()
        
        # Replace the document
        updated_item = container.replace_item(item=document_id, body=existing_doc)
        logging.info(f"Document updated successfully: {document_id}")
        return updated_item
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Failed to update document: {e}")
        raise
