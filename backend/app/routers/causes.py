from typing import List, Optional
from fastapi import APIRouter, Query
from backend.app.schemas.quality_schemas import CausaRaizItem, CausaTurnoItem
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/causas", tags=["Causas Raiz"])


@router.get("", response_model=List[CausaRaizItem])
def obter_distribuicao_causas(
    familia_motor: Optional[str] = Query(None, description="Filtrar por família (ex: W12, W22)"),
    turno: Optional[str] = Query(None, description="Filtrar por turno"),
    linha_montagem: Optional[str] = Query(None, description="Filtrar por linha de montagem"),
):
    return AnalyticsService.get_distribuicao_causas(familia_motor, turno, linha_montagem)


@router.get("/turnos", response_model=List[CausaTurnoItem])
def obter_causas_por_turno(
    familia_motor: Optional[str] = Query(None, description="Filtrar por família (ex: W12, W22)"),
    turno: Optional[str] = Query(None, description="Filtrar por turno específico"),
    linha_montagem: Optional[str] = Query(None, description="Filtrar por linha de montagem"),
):
    return AnalyticsService.get_causas_por_turno(familia_motor, turno, linha_montagem)