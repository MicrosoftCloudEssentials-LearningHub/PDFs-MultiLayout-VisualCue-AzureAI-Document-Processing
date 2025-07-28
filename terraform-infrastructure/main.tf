# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  # Output the resource group name
  provisioner "local-exec" {
    command = "echo Resource Group: ${self.name}"
  }
}

# Storage Account
resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  depends_on = [azurerm_resource_group.rg]

  # Output the storage account name
  provisioner "local-exec" {
    command = "echo Storage Account: ${self.name}"
  }
}

# Blob Container for Input Files
resource "azurerm_storage_container" "input_container" {
  name                  = "pdfinvoices"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"

  depends_on = [azurerm_storage_account.storage]

  # Output the container name
  provisioner "local-exec" {
    command = "echo Input Container: ${self.name}"
  }
}

# Blob Container for Output Files
resource "azurerm_storage_container" "output_container" {
  name                  = "output"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"

  depends_on = [azurerm_storage_account.storage]

  # Output the container name
  provisioner "local-exec" {
    command = "echo Output Container: ${self.name}"
  }
}

# Storage Account
resource "azurerm_storage_account" "runtime" {
  name                     = var.storage_account_name_runtime
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  depends_on = [azurerm_resource_group.rg]

  # Output the storage account name
  provisioner "local-exec" {
    command = "echo Storage Account: ${self.name}"
  }
}

# Assign Storage Blob Data Contributor role
resource "azurerm_role_assignment" "blob_data_contributor" {
  scope                = azurerm_storage_account.runtime.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id


  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_storage_account.runtime
  ]

}

# Assign Storage File Data SMB Share Contributor role
resource "azurerm_role_assignment" "file_data_smb_share_contributor" {
  scope                = azurerm_storage_account.runtime.id
  role_definition_name = "Storage File Data SMB Share Contributor"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_storage_account.runtime
  ]
}

# Assign Storage Blob Data Reader role
resource "azurerm_role_assignment" "blob_data_reader" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_storage_account.storage # Replace with the actual resource name
  ]
}


# Service Plan
resource "azurerm_service_plan" "asp" {
  name                = var.app_service_plan_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "Y1" # Consumption plan

  depends_on = [azurerm_resource_group.rg]

  # Output the service plan name
  provisioner "local-exec" {
    command = "echo Service Plan: ${self.name}"
  }
}

# Application Insights
resource "azurerm_application_insights" "appinsights" {
  name                = var.app_insights_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.loganalytics.id

  depends_on = [azurerm_resource_group.rg]

  provisioner "local-exec" {
    command = "echo Application Insights: ${self.name}"
  }
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "loganalytics" {
  name                = var.log_analytics_workspace_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"

  depends_on = [azurerm_resource_group.rg]

  # Output the log analytics workspace name
  provisioner "local-exec" {
    command = "echo Log Analytics Workspace: ${self.name}"
  }
}

# Key Vault
resource "azurerm_key_vault" "keyvault" {
  name                = var.key_vault_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  depends_on = [azurerm_resource_group.rg]

  # Output the key vault name
  provisioner "local-exec" {
    command = "echo Key Vault: ${self.name}"
  }
}

# Data source to get tenant ID
data "azurerm_client_config" "current" {}

# CosmosDB
resource "azurerm_cosmosdb_account" "cosmosdb" {
  name                = var.cosmosdb_account_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }

  depends_on = [azurerm_resource_group.rg]
}

# Cosmos DB SQL Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = var.cosmosdb_sqldb_name
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.cosmosdb.name
}

resource "azurerm_cosmosdb_sql_container" "outputcvscontainer" {
  name                  = var.sql_container_name
  resource_group_name   = azurerm_resource_group.rg.name
  account_name          = azurerm_cosmosdb_account.cosmosdb.name
  database_name         = azurerm_cosmosdb_sql_database.main.name
  throughput            = var.throughput
  partition_key_paths   = ["/transactionId"]
  partition_key_version = 1

  indexing_policy {
    indexing_mode = "consistent"

    included_path {
      path = "/*"
    }

    included_path {
      path = "/included/?"
    }

    excluded_path {
      path = "/excluded/?"
    }
  }

  unique_key {
    paths = ["/definition/idlong", "/definition/idshort"]
  }
}

# Cosmos DB Operator
resource "azurerm_role_assignment" "cosmosdb_operator" {
  scope                = azurerm_cosmosdb_account.cosmosdb.id
  role_definition_name = "Cosmos DB Operator"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_cosmosdb_account.cosmosdb
  ]
}

# DocumentDB Account Contributor
resource "azurerm_role_assignment" "documentdb_contributor" {
  scope                = azurerm_cosmosdb_account.cosmosdb.id
  role_definition_name = "DocumentDB Account Contributor"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_cosmosdb_account.cosmosdb
  ]
}

# Azure AI Administrator
resource "azurerm_role_assignment" "azure_ai_admin" {
  scope                = azurerm_cosmosdb_account.cosmosdb.id
  role_definition_name = "Azure AI Administrator"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_cosmosdb_account.cosmosdb
  ]
}

# Cosmos DB Account Reader Role
resource "azurerm_role_assignment" "cosmosdb_reader" {
  scope                = azurerm_cosmosdb_account.cosmosdb.id
  role_definition_name = "Cosmos DB Account Reader Role"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_cosmosdb_account.cosmosdb
  ]
}

# Contributor
resource "azurerm_role_assignment" "contributor" {
  scope                = azurerm_cosmosdb_account.cosmosdb.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_cosmosdb_account.cosmosdb
  ]
}


# Azure Form Recognizer (Document Intelligence)
resource "azurerm_cognitive_account" "form_recognizer" {
  name                = var.form_recognizer_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "FormRecognizer"
  sku_name            = "S0"

  depends_on = [azurerm_resource_group.rg]

  provisioner "local-exec" {
    command = "echo Form Recognizer: ${self.name}"
  }
}

# Azure AI Vision (Cognitive Services)
resource "azurerm_cognitive_account" "ai_vision" {
  name                = var.ai_vision_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "CognitiveServices"
  sku_name            = var.ai_vision_sku
  tags                = var.ai_vision_tags

  depends_on = [azurerm_resource_group.rg]

  provisioner "local-exec" {
    command = "echo AI Vision: ${self.name}"
  }
}

# We need to assign custom or built-in Cosmos DB SQL roles 
# (like Cosmos DB Built-in Data Reader, etc.) at the data plane level, 
# which is not currently supported directly in Terraform as of now.
# Workaround: Use null_resource with local-exec integrating the CLI command into 
# Terraform using a null_resource as follow:
locals {
  cosmosdb_role_assignment_id_function = uuid()
  cosmosdb_role_assignment_id_user     = uuid()
}

resource "null_resource" "cosmosdb_sql_role_assignment" {
  provisioner "local-exec" {
    command = "az cosmosdb sql role assignment create --resource-group ${azurerm_resource_group.rg.name} --account-name ${azurerm_cosmosdb_account.cosmosdb.name} --role-definition-id /subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${azurerm_resource_group.rg.name}/providers/Microsoft.DocumentDB/databaseAccounts/${azurerm_cosmosdb_account.cosmosdb.name}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002 --principal-id ${azurerm_linux_function_app.function_app.identity[0].principal_id} --scope ${azurerm_cosmosdb_account.cosmosdb.id} --role-assignment-id ${local.cosmosdb_role_assignment_id_function}"
  }

  depends_on = [
    azurerm_linux_function_app.function_app,
    azurerm_cosmosdb_account.cosmosdb
  ]
}

# Assign the Cosmos DB role to the user running the deployment 
resource "null_resource" "cosmosdb_sql_role_assignment_user" {
  provisioner "local-exec" {
    command = "az cosmosdb sql role assignment create --resource-group ${azurerm_resource_group.rg.name} --account-name ${azurerm_cosmosdb_account.cosmosdb.name} --role-definition-id /subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${azurerm_resource_group.rg.name}/providers/Microsoft.DocumentDB/databaseAccounts/${azurerm_cosmosdb_account.cosmosdb.name}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002 --principal-id ${data.azurerm_client_config.current.object_id} --scope ${azurerm_cosmosdb_account.cosmosdb.id} --role-assignment-id ${local.cosmosdb_role_assignment_id_user}"
  }

  depends_on = [
    azurerm_cosmosdb_account.cosmosdb
  ]
}

# Linux Function App
resource "azurerm_linux_function_app" "function_app" {
  name                       = var.function_app_name
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  service_plan_id            = azurerm_service_plan.asp.id
  storage_account_name       = azurerm_storage_account.runtime.name
  storage_account_access_key = azurerm_storage_account.runtime.primary_access_key

  identity {
    type = "SystemAssigned"
  }

  site_config {
    # Other configurations can go here
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME"                  = "python"
    "FUNCTIONS_EXTENSION_VERSION"               = "~4"
    "FUNCTIONS_NODE_BLOCK_ON_ENTRY_POINT_ERROR" = "true"
    "WEBSITE_RUN_FROM_PACKAGE"                  = "1"

    # === Core Azure Services Configuration ===
    "COSMOS_DB_ENDPOINT" = azurerm_cosmosdb_account.cosmosdb.endpoint
    "COSMOS_DB_KEY"      = azurerm_cosmosdb_account.cosmosdb.primary_key

    "invoicecontosostorage_STORAGE" = azurerm_storage_account.storage.primary_connection_string

    # Document Intelligence (Form Recognizer) for PDF layout analysis
    "FORM_RECOGNIZER_ENDPOINT" = azurerm_cognitive_account.form_recognizer.endpoint
    "FORM_RECOGNIZER_KEY"      = azurerm_cognitive_account.form_recognizer.primary_access_key

    # Application Insights for monitoring and telemetry
    "APPINSIGHTS_INSTRUMENTATIONKEY"        = azurerm_application_insights.appinsights.instrumentation_key
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.appinsights.connection_string

    # === AI Vision Services Configuration ===
    # Azure AI Vision for visual cue detection and image analysis
    "VISION_API_ENDPOINT" = azurerm_cognitive_account.ai_vision.endpoint
    "VISION_API_KEY"      = azurerm_cognitive_account.ai_vision.primary_access_key

    # === Azure OpenAI Configuration for LLM-Powered PDF Analysis ===
    # Main OpenAI service endpoint and authentication
    "AZURE_OPENAI_ENDPOINT"    = azurerm_cognitive_account.openai.endpoint
    "AZURE_OPENAI_KEY"         = azurerm_cognitive_account.openai.primary_access_key
    "AZURE_OPENAI_API_VERSION" = "2024-02-15-preview" # Latest API version

    # Model deployment names for different LLM capabilities
    "AZURE_OPENAI_GPT4_DEPLOYMENT"      = azurerm_cognitive_deployment.gpt4.name           # For complex reasoning and analysis
    "AZURE_OPENAI_GPT4O_DEPLOYMENT"     = azurerm_cognitive_deployment.gpt4o.name          # For advanced multimodal processing
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" = azurerm_cognitive_deployment.text_embedding.name # For semantic search and similarity

    # === AI Studio Configuration ===
    # AI Studio Hub and Project for model management and MLOps
    "AI_HUB_NAME"              = azurerm_machine_learning_workspace.ai_hub.name
    "AI_PROJECT_NAME"          = azurerm_machine_learning_workspace.ai_project.name
    "AI_HUB_WORKSPACE_URL"     = "https://ml.azure.com/workspaces/${azurerm_machine_learning_workspace.ai_hub.workspace_id}/computes?region=${azurerm_machine_learning_workspace.ai_hub.location}"
    "AI_PROJECT_WORKSPACE_URL" = "https://ml.azure.com/workspaces/${azurerm_machine_learning_workspace.ai_project.workspace_id}/computes?region=${azurerm_machine_learning_workspace.ai_project.location}"

    # AI Storage account for model artifacts and experiment data
    "AI_STORAGE_ACCOUNT_NAME" = azurerm_storage_account.runtime.name
    "AI_STORAGE_CONNECTION"   = azurerm_storage_account.runtime.primary_connection_string

    # === LLM Processing Configuration ===
    # Configuration for LLM-powered PDF processing features
    "ENABLE_LLM_PROCESSING" = "true"
    "LLM_MAX_TOKENS"        = "4000" # Maximum tokens per request
    "LLM_TEMPERATURE"       = "0.1"  # Low temperature for consistent extraction
    "LLM_TIMEOUT_SECONDS"   = "120"  # Timeout for LLM requests
  }

  depends_on = [
    azurerm_service_plan.asp,
    azurerm_application_insights.appinsights,
    azurerm_cosmosdb_account.cosmosdb,
    # AI and ML dependencies for LLM-powered processing
    azurerm_cognitive_account.openai,
    azurerm_cognitive_deployment.gpt4,
    azurerm_cognitive_deployment.gpt4o,
    azurerm_cognitive_deployment.text_embedding,
    azurerm_machine_learning_workspace.ai_hub,
    azurerm_machine_learning_workspace.ai_project,
    azurerm_storage_account.runtime
  ]

  provisioner "local-exec" {
    command = "echo Function App: ${self.name}"
  }
}


# Azure AI Foundry (AI Studio) Infrastructure


# Azure OpenAI Service for LLM capabilities
resource "azurerm_cognitive_account" "openai" {
  name                = var.openai_account_name
  location            = var.openai_location # Must be a region that supports OpenAI
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = "S0"

  # Enable custom subdomain for OpenAI
  custom_subdomain_name = var.openai_account_name

  # Network access configuration
  network_acls {
    default_action = "Allow" # Can be restricted to "Deny" with specific IP rules
  }

  # Enable identity for secure access
  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = var.environment
    Purpose     = "LLM-powered PDF extraction"
  }

  depends_on = [azurerm_resource_group.rg]

  provisioner "local-exec" {
    command = "echo Azure OpenAI Account: ${self.name}"
  }
}

# GPT-4 Model Deployment for PDF Analysis and Extraction
resource "azurerm_cognitive_deployment" "gpt4" {
  name                 = "gpt-4"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4"
    version = "turbo-2024-04-09" # Current stable version for GPT-4 Turbo
  }

  sku {
    name     = "Standard"
    capacity = 20 # Tokens per minute (TPM) in thousands
  }

  depends_on = [azurerm_cognitive_account.openai]

  provisioner "local-exec" {
    command = "echo GPT-4 Deployment: ${self.name}"
  }
}

# GPT-4o Model Deployment for Advanced PDF Processing (Recommended for PDF extraction)
resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-08-06" # Latest GPT-4o version with improved multimodal capabilities
  }

  sku {
    name     = "Standard"
    capacity = 30 # Higher capacity for complex PDF processing
  }

  depends_on = [azurerm_cognitive_account.openai]

  provisioner "local-exec" {
    command = "echo GPT-4o Deployment: ${self.name}"
  }
}

# Text Embedding Model for Semantic Search and Document Analysis
resource "azurerm_cognitive_deployment" "text_embedding" {
  name                 = "text-embedding-ada-3-large"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    # Example: Use "text-embedding-3-large" as an embedding model
    # You can use one of the following models for text embedding:
    # - "text-embedding-3-small" (recommended for most use cases)
    # - "text-embedding-3-large" (higher accuracy, higher cost)
    # - "text-search-ada-doc-001" (legacy, for backward compatibility)
    # - "text-embedding-ada-002" (legacy, for backward compatibility)
    # - "text-search-babbage-doc-001" (legacy, for backward compatibility)
    # - "text-search-curie-doc-001" (legacy, for backward compatibility)
    # - "text-search-davinci-doc-001" (legacy, for backward compatibility)
    name    = "text-embedding-3-large"
    version = "1" # This depends on the model
  }

  sku {
    name     = "Standard"
    # Capacity is the number of 1,000 tokens per minute (TPM) units.
    # Allowed values depend on your Azure OpenAI quota and region.
    # Common values: 1, 2, 5, 10, 20, 40, 80, 160, etc.
    # You can only set up to your available quota for this model.
    capacity = 1 # Example: set to 1 to fit within available quota
  }

  depends_on = [azurerm_cognitive_account.openai]

  provisioner "local-exec" {
    command = "echo Text Embedding Deployment: ${self.name}"
  }
}

# AI Studio Hub - Central resource for AI projects
resource "azurerm_machine_learning_workspace" "ai_hub" {
  name                    = var.ai_hub_name
  location                = azurerm_resource_group.rg.location
  resource_group_name     = azurerm_resource_group.rg.name
  application_insights_id = azurerm_application_insights.appinsights.id
  key_vault_id            = azurerm_key_vault.keyvault.id
  storage_account_id      = azurerm_storage_account.runtime.id

  # Enable identity for secure resource access
  identity {
    type = "SystemAssigned"
  }

  # Hub-specific settings
  description   = "AI Studio Hub for PDF Intelligence and LLM Processing"
  friendly_name = "PDF Intelligence Hub"

  # Enable public network access (can be restricted)
  public_network_access_enabled = true

  tags = {
    Environment = var.environment
    Purpose     = "AI Hub for PDF processing and LLM capabilities"
    Component   = "AIFoundry"
  }

  depends_on = [
    azurerm_resource_group.rg,
    azurerm_application_insights.appinsights,
    azurerm_key_vault.keyvault,
    azurerm_storage_account.runtime
  ]

  provisioner "local-exec" {
    command = "echo AI Studio Hub: ${self.name}"
  }
}

# AI Project - Specific project for PDF extraction workloads
resource "azurerm_machine_learning_workspace" "ai_project" {
  name                    = var.ai_project_name
  location                = azurerm_resource_group.rg.location
  resource_group_name     = azurerm_resource_group.rg.name
  application_insights_id = azurerm_application_insights.appinsights.id
  key_vault_id            = azurerm_key_vault.keyvault.id
  storage_account_id      = azurerm_storage_account.runtime.id

  # Enable identity for secure resource access
  identity {
    type = "SystemAssigned"
  }

  # Project-specific settings
  description   = "AI Project for PDF Document Intelligence and Skills Extraction"
  friendly_name = "PDF Skills Extraction Project"

  # Enable public network access (can be restricted)
  public_network_access_enabled = true

  tags = {
    Environment = var.environment
    Purpose     = "AI Project for PDF skills extraction and LLM analysis"
    Component   = "AIFoundry"
    ParentHub   = azurerm_machine_learning_workspace.ai_hub.name
  }

  depends_on = [
    azurerm_machine_learning_workspace.ai_hub,
    azurerm_application_insights.appinsights,
    azurerm_key_vault.keyvault,
    azurerm_storage_account.runtime
  ]

  provisioner "local-exec" {
    command = "echo AI Project: ${self.name}"
  }
}

# AI Models Container for storing custom models and artifacts
resource "azurerm_storage_container" "ai_models" {
  name                  = "aimodels"
  storage_account_id    = azurerm_storage_account.runtime.id
  container_access_type = "private"

  depends_on = [azurerm_storage_account.runtime]

  provisioner "local-exec" {
    command = "echo AI Models Container: ${self.name}"
  }
}

# AI Experiments Container for experiment outputs and logs
resource "azurerm_storage_container" "ai_experiments" {
  name                  = "experiments"
  storage_account_id    = azurerm_storage_account.runtime.id
  container_access_type = "private"

  depends_on = [azurerm_storage_account.runtime]

  provisioner "local-exec" {
    command = "echo AI Experiments Container: ${self.name}"
  }
}


# Role Assignments for Function App to access AI Resources
# These assignments enable the Function App's managed identity to securely
# access AI services without storing credentials in application settings


# Grant Function App access to Azure OpenAI Service
resource "azurerm_role_assignment" "function_openai_user" {
  scope                = azurerm_cognitive_account.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [azurerm_linux_function_app.function_app]

  provisioner "local-exec" {
    command = "echo Role Assignment: Function App -> OpenAI User"
  }
}

# Grant Function App access to AI Hub
resource "azurerm_role_assignment" "function_ai_hub_contributor" {
  scope                = azurerm_machine_learning_workspace.ai_hub.id
  role_definition_name = "AzureML Data Scientist" # Allows model deployment and experimentation
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [azurerm_linux_function_app.function_app]

  provisioner "local-exec" {
    command = "echo Role Assignment: Function App -> AI Hub Data Scientist"
  }
}

# Grant Function App access to AI Project
resource "azurerm_role_assignment" "function_ai_project_contributor" {
  scope                = azurerm_machine_learning_workspace.ai_project.id
  role_definition_name = "AzureML Data Scientist"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [azurerm_linux_function_app.function_app]

  provisioner "local-exec" {
    command = "echo Role Assignment: Function App -> AI Project Data Scientist"
  }
}

# Grant Function App access to AI Storage Account
resource "azurerm_role_assignment" "function_ai_storage_contributor" {
  scope                = azurerm_storage_account.runtime.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_linux_function_app.function_app.identity[0].principal_id

  depends_on = [azurerm_linux_function_app.function_app]

  provisioner "local-exec" {
    command = "echo Role Assignment: Function App -> AI Storage Contributor"
  }
}
