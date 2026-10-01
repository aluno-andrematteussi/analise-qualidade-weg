from typing import Any, Dict, List
from backend.app.database import get_db_connection


class AnalyticsService:

    @staticmethod
    def get_pareto_defeitos() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        query = """
            WITH DefeitosContagem AS (
                SELECT 
                    codigo_defeito,
                    descricao_defeito,
                    COUNT(*) as total_ocorrencias
                FROM view_qualidade
                WHERE status_inspecao = 'REFUGO' 
                  AND codigo_defeito IS NOT NULL 
                  AND codigo_defeito != ''
                GROUP BY codigo_defeito, descricao_defeito
            ),
            TotalGeral AS (
                SELECT SUM(total_ocorrencias) as grand_total FROM DefeitosContagem
            )
            SELECT 
                d.codigo_defeito,
                d.descricao_defeito,
                d.total_ocorrencias,
                ROUND((d.total_ocorrencias * 100.0 / t.grand_total), 2) AS porcentagem,
                ROUND(SUM(d.total_ocorrencias * 100.0 / t.grand_total) OVER (
                    ORDER BY d.total_ocorrencias DESC
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ), 2) AS porcentagem_acumulada
            FROM DefeitosContagem d, TotalGeral t
            ORDER BY d.total_ocorrencias DESC;
        """
        result = conn.execute(query).df().to_dict(orient="records")
        conn.close()
        return result

    @staticmethod
    def get_resumo_defeitos() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        query = """
            SELECT 
                codigo_defeito,
                descricao_defeito,
                COUNT(*) AS total_refugos,
                ROUND(SUM(custo_refugo_brl), 2) AS custo_total_brl
            FROM view_qualidade
            WHERE status_inspecao = 'REFUGO'
            GROUP BY codigo_defeito, descricao_defeito
            ORDER BY custo_total_brl DESC;
        """
        result = conn.execute(query).df().to_dict(orient="records")
        conn.close()
        return result

    @staticmethod
    def get_scrap_kpis() -> Dict[str, Any]:
        conn = get_db_connection()
        query = """
            SELECT 
                COUNT(*) AS total_produzido,
                COUNT(CASE WHEN status_inspecao = 'APROVADO' THEN 1 END) AS total_aprovado,
                COUNT(CASE WHEN status_inspecao = 'REFUGO' THEN 1 END) AS total_refugo,
                COUNT(CASE WHEN status_inspecao = 'RETRABALHO' THEN 1 END) AS total_retrabalho,
                ROUND(COUNT(CASE WHEN status_inspecao = 'REFUGO' THEN 1 END) * 100.0 / COUNT(*), 2) AS taxa_scrap_percent,
                ROUND(COALESCE(SUM(CASE WHEN status_inspecao = 'REFUGO' THEN custo_refugo_brl ELSE 0 END), 0), 2) AS custo_total_scrap_brl
            FROM view_qualidade;
        """
        result = conn.execute(query).df().to_dict(orient="records")
        conn.close()
        return (
            result[0]
            if result
            else {
                "total_produzido": 0,
                "total_aprovado": 0,
                "total_refugo": 0,
                "total_retrabalho": 0,
                "taxa_scrap_percent": 0.0,
                "custo_total_scrap_brl": 0.0,
            }
        )

    @staticmethod
    def get_scrap_por_lote() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        query = """
            SELECT 
                lote,
                familia_motor,
                COUNT(*) AS total_produzido,
                COUNT(CASE WHEN status_inspecao = 'REFUGO' THEN 1 END) AS total_refugo,
                ROUND(COUNT(CASE WHEN status_inspecao = 'REFUGO' THEN 1 END) * 100.0 / COUNT(*), 2) AS taxa_scrap_percent
            FROM view_qualidade
            GROUP BY lote, familia_motor
            ORDER BY lote ASC;
        """
        result = conn.execute(query).df().to_dict(orient="records")
        conn.close()
        return result

    @staticmethod
    def get_distribuicao_causas() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        query = """
            WITH Causas AS (
                SELECT causa_raiz, COUNT(*) AS total
                FROM view_qualidade
                WHERE status_inspecao = 'REFUGO'
                GROUP BY causa_raiz
            ),
            Total AS (SELECT SUM(total) as grand_total FROM Causas)
            SELECT 
                c.causa_raiz,
                c.total,
                ROUND(c.total * 100.0 / t.grand_total, 2) AS porcentagem
            FROM Causas c, Total t
            ORDER BY c.total DESC;
        """
        result = conn.execute(query).df().to_dict(orient="records")
        conn.close()
        return result

    @staticmethod
    def get_causas_por_turno() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        query = """
            SELECT 
                turno,
                causa_raiz,
                COUNT(*) AS total
            FROM view_qualidade
            WHERE status_inspecao = 'REFUGO'
            GROUP BY turno, causa_raiz
            ORDER BY turno, total DESC;
        """
        result = conn.execute(query).df().to_dict(orient="records")
        conn.close()
        return result