variable "subscription_id" {
  description = "The subscription ID for the Azure account."
  type        = string
}

variable "resource_group_name" {
  description = "The name of the resource group."
  type        = string
}

variable "location" {
  description = "The Azure region where resources will be created."
  type        = string
}


variable "storage_account_name" {
  description = "The name of the storage account"
  type        = string
}

variable "storage_account_name_runtime" {
  description = "The name of the storage account runtime (Function App Storage)"
  type        = string
}

variable "function_app_name" {
  description = "The name of the Linux Function App."
  type        = string
}

variable "app_service_plan_name" {
  description = "The name of the App Service plan"
  type        = string
}

variable "app_insights_name" {
  description = "The name of the Application Insights instance"
  type        = string
}

variable "log_analytics_workspace_name" {
  description = "The name of the Log Analytics workspace"
  type        = string
}

variable "key_vault_name" {
  description = "The name of the Key Vault"
  type        = string
}

variable "ai_vision_name" {
  description = "The name of the AI Vision Cognitive Services account"
  type        = string
}

variable "ai_vision_sku" {
  description = "The SKU of the AI Vision Cognitive Services account"
  type        = string
  default     = "S0"
}

variable "ai_vision_tags" {
  description = "Tags to be applied to the AI Vision resource"
  type        = map(string)
  default     = {
    Environment = "Development"
    Service     = "AI Vision"
  }
}
variable "cosmosdb_account_name" {
  description = "The name of the CosmosDB account."
  type        = string
}

variable "form_recognizer_name" {
  description = "The name of the Form Recognizer resource."
  type        = string
}

variable "cosmosdb_sqldb_name" {
  description = "The name of the Cosmos DB SQL database to be created."
  default     = "ContosoDBDocIntellig"
}

variable "sql_container_name" {
  description = "The name of the Cosmos DB SQL container to be created within the database."
  default     = "Invoices"
}

variable "throughput" {
  description = "The throughput (RU/s) to be allocated to the Cosmos DB SQL database or container."
  default     = 400
}
