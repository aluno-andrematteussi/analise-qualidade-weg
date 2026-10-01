from typing import List
from backend.app.schemas.quality_schemas import CausaRaizItem, CausaTurnoItem
from backend.app.services.analytics_service import AnalyticsService
from fastapi import APIRouter

router = APIRouter(prefix="/api/causas", tags=["Causas Raiz"])


@router.get("", response_model=List[CausaRaizItem])
def obter_distribuicao_causas():
    return AnalyticsService.get_distribuicao_causas()


@router.get("/turnos", response_model=List[CausaTurnoItem])
def obter_causas_por_turno():
    return AnalyticsService.get_causas_por_turno()