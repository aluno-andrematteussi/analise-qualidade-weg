from pathlib import Path

# Raiz do projeto (/srv/analise-qualidade-weg)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Diretórios de dados
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Arquivos
CSV_FILE_PATH = RAW_DATA_DIR / "producao_motores.csv"
PARQUET_FILE_PATH = PROCESSED_DATA_DIR / "qualidade.parquet"

# Metadados da API
API_TITLE = "WEG Quality Analytics API"
API_VERSION = "1.0.0"
