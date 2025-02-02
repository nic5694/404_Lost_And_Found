variable "resource_group_location" {
  type        = string
  default     = "canadacentral"
  description = "Location of the resource group."
}
variable "resource_group_name_prefix" {
  type        = string
  default     = "rg"
  description = "Prefix of the resource group name that's combined with a random value so name is unique in your Azure subscription."
}
variable "subscription_id" {
  type        = string
  description = "The Azure subscription ID."
}