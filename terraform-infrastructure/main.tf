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

    "COSMOS_DB_ENDPOINT" = azurerm_cosmosdb_account.cosmosdb.endpoint
    "COSMOS_DB_KEY"      = azurerm_cosmosdb_account.cosmosdb.primary_key

    "invoicecontosostorage_STORAGE" = azurerm_storage_account.storage.primary_connection_string

    "FORM_RECOGNIZER_ENDPOINT" = azurerm_cognitive_account.form_recognizer.endpoint
    "FORM_RECOGNIZER_KEY"      = azurerm_cognitive_account.form_recognizer.primary_access_key

    "APPINSIGHTS_INSTRUMENTATIONKEY"        = azurerm_application_insights.appinsights.instrumentation_key
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.appinsights.connection_string

    # Azure AI Vision settings
    "VISION_API_ENDPOINT" = azurerm_cognitive_account.ai_vision.endpoint
    "VISION_API_KEY"      = azurerm_cognitive_account.ai_vision.primary_access_key
  }

  depends_on = [
    azurerm_service_plan.asp,
    azurerm_application_insights.appinsights,
    azurerm_cosmosdb_account.cosmosdb

  ]

  provisioner "local-exec" {
    command = "echo Function App: ${self.name}"
  }
}
