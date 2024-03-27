from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import app_config

# Your Key Vault URL and the name of the secret where your certificate is stored
key_vault_url = f"https://{app_config.KEY_VAULT_NAME}.vault.azure.net"

# Authenticate to Azure Key Vault
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)

def get_secret(secret_name):
    return client.get_secret(secret_name).value
