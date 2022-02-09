from app.core.security.api_key_generator import ApiKeyGenerator, DefaultApiKeyGenerator


def get_api_generator() -> ApiKeyGenerator:
    return DefaultApiKeyGenerator()
