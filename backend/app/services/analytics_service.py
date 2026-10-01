from typing import Any, Dict, List, Optional, Tuple
from backend.app.database import get_db_connection


class AnalyticsService:

    @staticmethod
    def _build_filter(
        base_conditions: List[str],
        familia_motor: Optional[str] = None,
        turno: Optional[str] = None,
        linha_montagem: Optional[str] = None,
        lote: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> Tuple[str, List[Any]]:
        conditions = list(base_conditions)
        params: List[Any] = []

        if familia_motor:
            conditions.append("familia_motor = ?")
            params.append(familia_motor)
        if turno:
            conditions.append("turno = ?")
            params.append(turno)
        if linha_montagem:
            conditions.append("linha_montagem = ?")
            params.append(linha_montagem)

        if lote:
            conditions.append("lote = ?")
            params.append(lote)
        if data_inicio:
            conditions.append("timestamp >= CAST(? AS DATE)")
            params.append(data_inicio)
        if data_fim:
            conditions.append("timestamp < CAST(? AS DATE) + INTERVAL 1 DAY")
            params.append(data_fim)
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        return where_clause, params

    @staticmethod
    def get_pareto_defeitos(
        familia_motor: Optional[str] = None,
        turno: Optional[str] = None,
        linha_montagem: Optional[str] = None,
        lote: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        where_clause, params = AnalyticsService._build_filter(
            [
                "status_inspecao = 'REFUGO'",
                "codigo_defeito IS NOT NULL",
                "codigo_defeito != ''",
            ],
            familia_motor,
            turno,
            linha_montagem, lote, data_inicio, data_fim,
        )

        query = f"""
            WITH DefeitosContagem AS (
                SELECT 
                    codigo_defeito,
                    descricao_defeito,
                    COUNT(*) as total_ocorrencias
                FROM view_qualidade
                {where_clause}
                GROUP BY codigo_defeito, descricao_defeito
            ),
            TotalGeral AS (
                SELECT COALESCE(SUM(total_ocorrencias), 0) as grand_total FROM DefeitosContagem
            )
            SELECT 
                d.codigo_defeito,
                d.descricao_defeito,
                d.total_ocorrencias,
                CASE 
                    WHEN t.grand_total > 0 THEN ROUND((d.total_ocorrencias * 100.0 / t.grand_total), 2)
                    ELSE 0.0 
                END AS porcentagem,
                CASE 
                    WHEN t.grand_total > 0 THEN ROUND(SUM(d.total_ocorrencias * 100.0 / t.grand_total) OVER (
                        ORDER BY d.total_ocorrencias DESC
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ), 2)
                    ELSE 0.0 
                END AS porcentagem_acumulada
            FROM DefeitosContagem d, TotalGeral t
            ORDER BY d.total_ocorrencias DESC;
        """
        result = conn.execute(query, params).df().to_dict(orient="records")
        conn.close()
        return result

    @staticmethod
    def get_resumo_defeitos(
        familia_motor: Optional[str] = None,
        turno: Optional[str] = None,
        linha_montagem: Optional[str] = None,
        lote: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        where_clause, params = AnalyticsService._build_filter(
            ["status_inspecao = 'REFUGO'"],
            familia_motor,
            turno,
            linha_montagem, lote, data_inicio, data_fim,
        )

        query = f"""
            SELECT 
                codigo_defeito,
                descricao_defeito,
                COUNT(*) AS total_refugos,
                ROUND(COALESCE(SUM(custo_refugo_brl), 0), 2) AS custo_total_brl
            FROM view_qualidade
            {where_clause}
            GROUP BY codigo_defeito, descricao_defeito
            ORDER BY custo_total_brl DESC;
        """
        result = conn.execute(query, params).df().to_dict(orient="records")
        conn.close()
        return result

    @staticmethod
    def get_scrap_kpis(
        familia_motor: Optional[str] = None,
        turno: Optional[str] = None,
        linha_montagem: Optional[str] = None,
        lote: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> Dict[str, Any]:
        conn = get_db_connection()
        where_clause, params = AnalyticsService._build_filter(
            [],
            familia_motor,
            turno,
            linha_montagem, lote, data_inicio, data_fim,
        )

        query = f"""
            SELECT 
                COUNT(*) AS total_produzido,
                COUNT(*) AS total_inspecionado,
                COUNT(CASE WHEN status_inspecao = 'APROVADO' THEN 1 END) AS total_aprovado,
                COUNT(CASE WHEN status_inspecao = 'REFUGO' THEN 1 END) AS total_refugo,
                COUNT(CASE WHEN status_inspecao = 'RETRABALHO' THEN 1 END) AS total_retrabalho,
                CASE 
                    WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN status_inspecao = 'REFUGO' THEN 1 END) * 100.0 / COUNT(*), 2)
                    ELSE 0.0 
                END AS taxa_scrap_percent,
                ROUND(COALESCE(SUM(CASE WHEN status_inspecao = 'REFUGO' THEN custo_refugo_brl ELSE 0 END), 0), 2) AS custo_total_scrap_brl
            FROM view_qualidade
            {where_clause};
        """
        result = conn.execute(query, params).df().to_dict(orient="records")
        conn.close()
        return (
            result[0]
            if result
            else {
                "total_produzido": 0,
                "total_inspecionado": 0,
                "total_aprovado": 0,
                "total_refugo": 0,
                "total_retrabalho": 0,
                "taxa_scrap_percent": 0.0,
                "custo_total_scrap_brl": 0.0,
            }
        )

    @staticmethod
    def get_scrap_por_lote(
        familia_motor: Optional[str] = None,
        turno: Optional[str] = None,
        linha_montagem: Optional[str] = None,
        lote: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        where_clause, params = AnalyticsService._build_filter(
            [],
            familia_motor,
            turno,
            linha_montagem, lote, data_inicio, data_fim,
        )

        query = f"""
            SELECT 
                lote,
                familia_motor,
                COUNT(*) AS total_produzido,
                COUNT(CASE WHEN status_inspecao = 'REFUGO' THEN 1 END) AS total_refugo,
                CASE 
                    WHEN COUNT(*) > 0 THEN ROUND(COUNT(CASE WHEN status_inspecao = 'REFUGO' THEN 1 END) * 100.0 / COUNT(*), 2)
                    ELSE 0.0 
                END AS taxa_scrap_percent
            FROM view_qualidade
            {where_clause}
            GROUP BY lote, familia_motor
            ORDER BY lote ASC;
        """
        result = conn.execute(query, params).df().to_dict(orient="records")
        conn.close()
        return result

    @staticmethod
    def get_distribuicao_causas(
        familia_motor: Optional[str] = None,
        turno: Optional[str] = None,
        linha_montagem: Optional[str] = None,
        lote: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        where_clause, params = AnalyticsService._build_filter(
            [
                "status_inspecao = 'REFUGO'",
                "causa_raiz IS NOT NULL",
                "causa_raiz != ''",
            ],
            familia_motor,
            turno,
            linha_montagem, lote, data_inicio, data_fim,
        )

        query = f"""
            WITH Causas AS (
                SELECT causa_raiz, COUNT(*) AS total
                FROM view_qualidade
                {where_clause}
                GROUP BY causa_raiz
            ),
            Total AS (SELECT COALESCE(SUM(total), 0) as grand_total FROM Causas)
            SELECT 
                c.causa_raiz,
                c.total,
                CASE 
                    WHEN t.grand_total > 0 THEN ROUND(c.total * 100.0 / t.grand_total, 2)
                    ELSE 0.0 
                END AS porcentagem
            FROM Causas c, Total t
            ORDER BY c.total DESC;
        """
        result = conn.execute(query, params).df().to_dict(orient="records")
        conn.close()
        return result

    @staticmethod
    def get_causas_por_turno(
        familia_motor: Optional[str] = None,
        turno: Optional[str] = None,
        linha_montagem: Optional[str] = None,
        lote: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        where_clause, params = AnalyticsService._build_filter(
            [
                "status_inspecao = 'REFUGO'",
                "causa_raiz IS NOT NULL",
                "causa_raiz != ''",
            ],
            familia_motor,
            turno,
            linha_montagem, lote, data_inicio, data_fim,
        )

        query = f"""
            SELECT 
                turno,
                causa_raiz,
                COUNT(*) AS total
            FROM view_qualidade
            {where_clause}
            GROUP BY turno, causa_raiz
            ORDER BY turno, total DESC;
        """
        result = conn.execute(query, params).df().to_dict(orient="records")
        conn.close()
        return result
