from typing import List
from backend.app.schemas.quality_schemas import DefeitoResumo, ParetoItem
from backend.app.services.analytics_service import AnalyticsService
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Pareto & Defeitos"])


@router.get("/pareto", response_model=List[ParetoItem])
def obter_pareto():
    return AnalyticsService.get_pareto_defeitos()


@router.get("/defeitos", response_model=List[DefeitoResumo])
def obter_resumo_defeitos():
    return AnalyticsService.get_resumo_defeitos()