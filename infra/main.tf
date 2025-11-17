resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "random_string" "sa_suffix" {
  length  = 10
  lower   = true
  upper   = false
  numeric = false
  special = false
}

resource "azurerm_storage_account" "sa" {
  name                     = "st${random_string.sa_suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  allow_nested_items_to_be_public = false
  min_tls_version = "TLS1_2"
  kind = "StorageV2"
}

resource "azurerm_storage_container" "weather" {
  name = "weather-data"
  storage_account_name = azurerm_storage_account.sa.name
  container_access_type = "private"
}

resource "azurerm_service_plan" "plan" {
  name = "${var.function_app_name}-plan"
  resource_group_name = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
  os_type = "Linux"
  sku_name = "Y1" # Consumption (pay-per-run)
}

resource "azurerm_linux_function_app" "func" {
  name = var.function_app_name
  resource_group_name = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
  service_plan_id = azurerm_service_plan.plan.id

  storage_account_name = azurerm_storage_account.sa.name
  storage_account_access_key = azurerm_storage_account.sa.primary_access_key

  functions_extension_version = "~4"

  site_config {
    application_stack {
      python_version = "3.10"
    }
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME = "python"
    WEBSITE_RUN_FROM_PACKAGE = "1"
    TIMER_SCHEDULE     = var.timer_schedule
    WEATHER_LAT        = var.weather_lat
    WEATHER_LON        = var.weather_lon
    WEATHER_USER_AGENT = var.weather_user_agent
    DATA_CONTAINER     = azurerm_storage_container.weather.name

    AzureWebJobsStorage = azurerm_storage_account.sa.primary_connection_string
  }
}
