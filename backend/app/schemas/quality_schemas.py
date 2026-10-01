from typing import List, Optional
from pydantic import BaseModel


# 1. Pareto e Defeitos
class ParetoItem(BaseModel):
    codigo_defeito: str
    descricao_defeito: str
    total_ocorrencias: int
    porcentagem: float
    porcentagem_acumulada: float


class DefeitoResumo(BaseModel):
    codigo_defeito: str
    descricao_defeito: str
    total_refugos: int
    custo_total_brl: float


# 2. Refugo (Scrap) e Lotes
class ScrapKPIs(BaseModel):
    total_produzido: int
    total_aprovado: int
    total_refugo: int
    total_retrabalho: int
    taxa_scrap_percent: float
    custo_total_scrap_brl: float


class ScrapPorLote(BaseModel):
    lote: str
    familia_motor: str
    total_produzido: int
    total_refugo: int
    taxa_scrap_percent: float


# 3. Causas e Turnos
class CausaRaizItem(BaseModel):
    causa_raiz: str
    total: int
    porcentagem: float


class CausaTurnoItem(BaseModel):
    turno: str
    causa_raiz: str
    total: int