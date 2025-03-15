data "aws_iam_role" "role" {
  name = "LabRole"
}

data "archive_file" "lambda_package" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "authorizer_lambda" {
  function_name    = "tech-challenge-authorizer"
  filename         = data.archive_file.lambda_package.output_path
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  role             = data.aws_iam_role.role.arn
  source_code_hash = filebase64sha256(data.archive_file.lambda_package.output_path)
}