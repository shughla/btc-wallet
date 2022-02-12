from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.facade import IFacade
from app.core.models.statistics import Statistics
from app.infra.fastapi.deps import can_access_admin, get_facade

router = APIRouter()


class StatisticsResponse(BaseModel):
    total_transactions: int
    profit: int


@router.post(
    "/statistics", status_code=HTTPStatus.OK, response_model=StatisticsResponse
)
def show_statistics(
    facade: IFacade = Depends(get_facade),
    is_admin: bool = Depends(can_access_admin),
) -> Statistics:
    if not is_admin:
        raise HTTPException(HTTPStatus.FORBIDDEN)
    return facade.get_statistics()
