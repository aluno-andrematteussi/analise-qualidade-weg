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
    return conn