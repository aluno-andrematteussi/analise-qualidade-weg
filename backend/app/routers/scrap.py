from typing import List, Optional
from fastapi import APIRouter, Query
from backend.app.schemas.quality_schemas import ScrapKPIs, ScrapPorLote
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/scrap", tags=["Controle de Refugo (Scrap)"])


@router.get("", response_model=ScrapKPIs)
def obter_kpis_scrap(
    familia_motor: Optional[str] = Query(None, description="Filtrar por família (ex: W12, W22)"),
    turno: Optional[str] = Query(None, description="Filtrar por turno"),
    linha_montagem: Optional[str] = Query(None, description="Filtrar por linha de montagem"),
):
    return AnalyticsService.get_scrap_kpis(familia_motor, turno, linha_montagem)


@router.get("/lotes", response_model=List[ScrapPorLote])
def obter_scrap_por_lotes(
    familia_motor: Optional[str] = Query(None, description="Filtrar por família (ex: W12, W22)"),
    turno: Optional[str] = Query(None, description="Filtrar por turno"),
    linha_montagem: Optional[str] = Query(None, description="Filtrar por linha de montagem"),
):
    return AnalyticsService.get_scrap_por_lote(familia_motor, turno, linha_montagem)