# src/config.py

# SAP SuccessFactors OData API Configuration (V2)
# IMPORTANT: Em um ambiente de produção, informações sensíveis
# como credenciais devem ser carregadas de variáveis de ambiente
# ou de um sistema de gerenciamento de configurações seguro,
# NUNCA hardcoded diretamente no código.

# URL base para o seu servidor SAP SuccessFactors OData V2 API
# Exemplo: "https://api17.sapsf.com/odata/v2"
# Substitua <YOUR_SF_API_SERVER_V2> pelo servidor API real da sua instância.
SF_API_SERVER_V2 = "https://<YOUR_SF_API_SERVER_V2>"

# ID da sua empresa SAP SuccessFactors
# Substitua <YOUR_SF_COMPANY_ID> pelo ID real da sua empresa.
SF_COMPANY_ID = "<YOUR_SF_COMPANY_ID>"

# --- Configuração OAuth 2.0 (Recomendado) ---
# Para o fluxo SAML Assertion, você normalmente precisaria de:
# SF_OAUTH_CLIENT_ID = "<YOUR_OAUTH_CLIENT_ID>"
# SF_SAML_ASSERTION_PATH = "/caminho/para/sua/saml_assertion.xml" # Ou gerar dinamicamente
# SF_OAUTH_TOKEN_URL = "https://<YOUR_API_SERVER>/oauth/token"

# --- Autenticação Básica (Obsoleta, para testes iniciais ou cenários específicos) ---
# Use com extrema cautela e apenas como medida temporária.
# Substitua pelo seu nome de usuário e senha reais se usar Autenticação Básica para testes.
SF_USERNAME = "<YOUR_SF_USERNAME>"
SF_PASSWORD = "<YOUR_SF_PASSWORD>"

# Configuração da aplicação Flask
FLASK_APP_HOST = '0.0.0.0'
FLASK_APP_PORT = 5000
