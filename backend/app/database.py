import duckdb
from backend.app.config import PARQUET_FILE_PATH


def get_db_connection():
    """Retorna uma conexão DuckDB em memória com a view analítica apontando para o Parquet."""
    conn = duckdb.connect(database=":memory:")
    if PARQUET_FILE_PATH.exists():
        conn.execute(
            f"""
            CREATE OR REPLACE VIEW view_qualidade AS 
            SELECT * FROM read_parquet('{PARQUET_FILE_PATH}');
        """
        )
    else:
        # Keep the API available before the first ETL run. Empty results are
        # preferable to failing every endpoint when no source data is present.
        conn.execute("""
            CREATE VIEW view_qualidade AS SELECT
                CAST(NULL AS VARCHAR) AS familia_motor,
                CAST(NULL AS VARCHAR) AS turno,
                CAST(NULL AS VARCHAR) AS linha_montagem,
                CAST(NULL AS VARCHAR) AS lote,
                CAST(NULL AS TIMESTAMP) AS timestamp,
                CAST(NULL AS VARCHAR) AS status_inspecao,
                CAST(NULL AS VARCHAR) AS codigo_defeito,
                CAST(NULL AS VARCHAR) AS descricao_defeito,
                CAST(NULL AS VARCHAR) AS causa_raiz,
                CAST(NULL AS DOUBLE) AS custo_refugo_brl
            WHERE FALSE
        """)
    return conn
