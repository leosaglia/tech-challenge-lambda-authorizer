terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  required_version = ">= 0.14"
}

provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket = "state-terraform-tech-v2"
    key = "tech-challenge-lambda-authorizer/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}