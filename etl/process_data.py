from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Ajuste de path para importação do config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from backend.app.config import CSV_FILE_PATH, PARQUET_FILE_PATH, RAW_DATA_DIR


def gerar_dados_simulados(total_linhas: int = 5000):
    """Gera massa de dados industriais simulados de motores WEG (19 colunas)."""
    np.random.seed(42)
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    familias = ["W12", "W22"]
    potencias = [1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 50.0]
    turnos = ["Turno 1", "Turno 2", "Turno 3"]
    linhas = ["Linha A", "Linha B", "Linha C"]

    defeitos = [
        ("DEF-01", "Falha de Isolamento no Bobinado", "Falta de Verniz"),
        ("DEF-02", "Desbalanceamento do Rotor", "Falha de Usinagem"),
        ("DEF-03", "Excesso de Ruído Mecânico", "Rolamento Danificado"),
        ("DEF-04", "Sobretemperatura na Carcaça", "Erro de Projeto/Fluxo"),
        ("DEF-05", "Trinca na Tampa Defletora", "Impacto no Transporte"),
    ]

    datas = pd.date_range(end=pd.Timestamp.now(), periods=total_linhas, freq="min")

    registros = []
    for i in range(total_linhas):
        familia = np.random.choice(familias, p=[0.4, 0.6])
        status = np.random.choice(["APROVADO", "REFUGO", "RETRABALHO"], p=[0.88, 0.08, 0.04])
        
        cod_def, desc_def, causa = (None, None, None)
        custo = 0.0

        if status == "REFUGO":
            idx = np.random.choice(len(defeitos), p=[0.35, 0.25, 0.20, 0.12, 0.08])
            cod_def, desc_def, causa = defeitos[idx]
            custo = np.random.uniform(150.0, 850.0)
        elif status == "RETRABALHO":
            idx = np.random.choice(len(defeitos))
            cod_def, desc_def, causa = defeitos[idx]
            custo = np.random.uniform(30.0, 120.0)

        registros.append({
            "id_teste": f"TST-{100000 + i}",
            "timestamp": datas[i],
            "familia_motor": familia,
            "potencia_cv": float(np.random.choice(potencias)),
            "linha_montagem": np.random.choice(linhas),
            "turno": np.random.choice(turnos),
            "operador_id": f"OP-{np.random.randint(10, 30)}",
            "lote": f"LOT-2026-{np.random.randint(100, 120)}",
            "resistencia_isolamento_mohm": round(float(np.random.normal(500, 50)), 2),
            "tensao_ensaio_v": int(np.random.choice([220, 380, 440])),
            "corrente_vazio_a": round(float(np.random.normal(3.5, 0.4)), 2),
            "vibracao_de_mms": round(float(np.random.normal(1.2, 0.3)), 2),
            "temperatura_carcaca_c": round(float(np.random.normal(65, 8)), 2),
            "ruido_db": round(float(np.random.normal(70, 5)), 2),
            "status_inspecao": status,
            "codigo_defeito": cod_def,
            "descricao_defeito": desc_def,
            "causa_raiz": causa,
            "custo_refugo_brl": round(float(custo), 2)
        })

    df = pd.DataFrame(registros)
    df.to_csv(CSV_FILE_PATH, index=False)
    print(f"[+] Gerados {total_linhas} registros simulados em: {CSV_FILE_PATH}")
    return df


def run_etl():
    if not CSV_FILE_PATH.exists():
        print(f"[*] Base bruta não encontrada. Gerando dados de teste...")
        df = gerar_dados_simulados()
    else:
        print(f"[*] Carregando base existente: {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH)

    print("[*] Aplicando transformações e tipagem estrita...")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["custo_refugo_brl"] = df["custo_refugo_brl"].fillna(0.0).astype(float)

    PARQUET_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, PARQUET_FILE_PATH, compression="snappy")
    print(f"[+] Base analítica exportada com sucesso: {PARQUET_FILE_PATH}")


if __name__ == "__main__":
    run_etl()