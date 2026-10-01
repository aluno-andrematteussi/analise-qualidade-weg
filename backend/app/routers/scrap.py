from typing import List
from backend.app.schemas.quality_schemas import ScrapKPIs, ScrapPorLote
from backend.app.services.analytics_service import AnalyticsService
from fastapi import APIRouter

router = APIRouter(prefix="/api/scrap", tags=["Controle de Refugo (Scrap)"])


@router.get("", response_model=ScrapKPIs)
def obter_kpis_scrap():
    return AnalyticsService.get_scrap_kpis()


@router.get("/lotes", response_model=List[ScrapPorLote])
def obter_scrap_por_lotes():
    return AnalyticsService.get_scrap_por_lote()