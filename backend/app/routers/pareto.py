from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Query
from backend.app.schemas.quality_schemas import DefeitoResumo, ParetoItem
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api", tags=["Pareto & Defeitos"])


@router.get("/pareto", response_model=List[ParetoItem])
def obter_pareto(
    familia_motor: Optional[str] = Query(None, description="Filtrar por família (ex: W12, W22)"),
    turno: Optional[str] = Query(None, description="Filtrar por turno (ex: Turno 1, Turno 2, Turno 3)"),
    linha_montagem: Optional[str] = Query(None, description="Filtrar por linha de montagem"),
    lote: Optional[str] = Query(None, description="Filtrar por lote"),
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data final inclusiva (YYYY-MM-DD)"),
):
    return AnalyticsService.get_pareto_defeitos(familia_motor, turno, linha_montagem, lote, data_inicio, data_fim)


@router.get("/defeitos", response_model=List[DefeitoResumo])
def obter_resumo_defeitos(
    familia_motor: Optional[str] = Query(None, description="Filtrar por família (ex: W12, W22)"),
    turno: Optional[str] = Query(None, description="Filtrar por turno"),
    linha_montagem: Optional[str] = Query(None, description="Filtrar por linha de montagem"),
    lote: Optional[str] = Query(None, description="Filtrar por lote"),
    data_inicio: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data final inclusiva (YYYY-MM-DD)"),
):
    return AnalyticsService.get_resumo_defeitos(familia_motor, turno, linha_montagem, lote, data_inicio, data_fim)