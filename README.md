# tech-challenge-lambda-authorizer

## Descrição
Este repositório contém uma função Lambda, que atua como lambda authorizer do api gateway [**fast-food-tech-challenge**](https://github.com/leosaglia/tech-challenge-infra-api-gateway).

A Lambda pode validar 2 tipos de token:

- Um personalizado criado a partir da lambda [tech-challenge-lambda-token-generation](https://github.com/leosaglia/tech-challenge-lambda-token-generation)
- O outro criado através de uma ação de sign in para um usuário registrado no [cognito](https://github.com/leosaglia/tech-challenge-infra-cognito).

**Tecnologia:** Python

## Pré requisitos
Deve existir o secret com o nome **"jwt_secret"** no Secrets manager.
Deve exitir a user poll **fast-food-user-pool** no cognito.

## Integrações e Dependências
- Integrações com AWS (Lambda, Secrets Manager) e gerenciamento de infraestrutura com Terraform.
- Dependências da aplição: 
  - ***PyJWT*** para lidar com tokens JWT.
  - ***boto3*** para se comunicar com o AWS Secrets Manager.
  - ***requests*** para obter as chaves jwks usada na lógica de validação do token cognito.
  - ***python-jose*** Possui recursos para analisar o token do cognito.

## Workflow
Todo o deploy CI/CD é automatizado utilizado o github actions.

Segue o ***Github flow***. Possui a branch main protegida, com as alterações sendo realizadas em outras branchs, e quando concluídas, realizado o PR para main.

- O workflow é definido em *.github/workflows/deploy-lambda.yml*.
- Instalação das dependências do projeto Python.
- Configuração de credenciais AWS para acessar serviços e fazer deploy.
- Passos do Terraform (init, validate, plan) como ações de CI para gerenciar a infraestrutura da função Lambda.
- Terraform apply após passar nos steps anterior o o merge for efetivado para main.
