resource "azurerm_resource_group" "rg" {
  name     = "lost-and-found-rg"
  location = var.resource_group_location
}