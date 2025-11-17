variable "resource_group_name" { type = string }
variable "location" { type = string default = "eastus" }
variable "function_app_name" { type = string description = "Must be globally unique" }
variable "weather_lat" { type = string }
variable "weather_lon" { type = string }
variable "timer_schedule" { type = string default = "0 0 * * * *" } # every hour
variable "weather_user_agent" { type = string default = "wxdemo/1.0 (you@example.com)" }
