# analise-qualidade-weg

Dashboard de controle e análise da qualidade de uma linha de montagem de motores. O FastAPI lê `data/processed/qualidade.parquet` via DuckDB e serve também a interface HTML com Chart.js.

## Executar

Na raiz do projeto, instale as dependências e inicie a API:

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Acesse o dashboard em <http://localhost:8000/> e a documentação interativa da API em <http://localhost:8000/docs>.

Para reconstruir o Parquet a partir de `data/raw/producao_motores.csv`:

```bash
python -m etl.process_data
```

Se o CSV não existir, o ETL cria uma base simulada para demonstração. A API também inicia sem Parquet e retorna KPIs zerados e listas vazias até que os dados estejam disponíveis.

## Endpoints do dashboard

- `GET /api/scrap`: KPIs de produção, inspeção, refugo e retrabalho.
- `GET /api/pareto`: ocorrências por defeito e percentual acumulado.
- `GET /api/scrap/lotes`: produção e refugo por lote e família.
- `GET /api/causas/turnos`: causas-raiz por turno.
- `GET /api/health`: estado da API.

Os endpoints analíticos aceitam os filtros `familia_motor`, `turno`, `lote`, `data_inicio` e `data_fim` (datas no formato `YYYY-MM-DD`).
