from http import HTTPStatus

from fastapi import APIRouter, Depends

from app.core.security.api_key_generator import ApiKey, ApiKeyGenerator
from app.infra.fastapi.deps import get_api_generator

router = APIRouter()


@router.post("/user", status_code=HTTPStatus.CREATED)  # type: ignore
def create_user(generator: ApiKeyGenerator = Depends(get_api_generator)) -> ApiKey:
    print(generator.generate_api_key())
    return generator.generate_api_key()
