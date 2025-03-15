variable "role_arn" {
    description = "The ARN of the IAM role that the Lambda function will assume"
    type        = string

    default = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/tech-challenge-lambda-role"
}