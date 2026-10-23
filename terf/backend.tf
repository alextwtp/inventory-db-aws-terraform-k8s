#####################################################################################
# To use Remote S3 State, uncomment the section below and enter your S3 Bucket name.# 
#####################################################################################

# terraform {
#   backend "s3" {
#     bucket = "your-tf-state-bucket"
#     key    = "your state.tfstate"
#     region = "your region"
#     dynamodb_table = "terraform-locks"
#     encrypt        = true
#  } 