terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstatewxstor12345"
    container_name       = "tfstate"
    key                  = "weather/infra.tfstate"
  }
}
