variable "vpc_id" {
  type        = string
  description = "VPC ID passed from VPC module"
}

variable "ecs_sg_id" {
  type        = string
  default     = ""
  description = "ECS Security Group ID"
}

variable "subnet_ids" {
  type        = list(string)
  default     = []
  description = "Subnet IDs for RDS"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "RDS Password"
}  

variable "db_subnet_group_name" {
  type        = string
  description = "Name of DB Subnet Group from VPC module"
}