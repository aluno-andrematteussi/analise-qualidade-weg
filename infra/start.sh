#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
API_HOST="127.0.0.1"
API_PORT="8001"
API_URL="http://${API_HOST}:${API_PORT}"
HEALTH_URL="${API_URL}/api/health"
API_PID=""
TUNNEL_PID=""
TUNNEL_LOG=""
LAST_LOG_LINE=0

free_api_port() {
  if ! fuser -s -n tcp "$API_PORT" 2>/dev/null; then
    return 0
  fi

  printf '[INFO] Porta %s ocupada; encerrando os processos que a utilizam...\n' "$API_PORT"
  fuser -k -TERM -n tcp "$API_PORT" >/dev/null 2>&1 || true

  for attempt in {1..10}; do
    if ! fuser -s -n tcp "$API_PORT" 2>/dev/null; then
      printf '[OK] Porta %s liberada.\n' "$API_PORT"
      return 0
    fi
    sleep 0.5
  done

  printf '[INFO] Processos ainda ativos na porta %s; enviando encerramento forçado...\n' "$API_PORT"
  fuser -k -KILL -n tcp "$API_PORT" >/dev/null 2>&1 || true
  sleep 1
  if fuser -s -n tcp "$API_PORT" 2>/dev/null; then
    printf '[ERRO] Não foi possível liberar a porta %s. Verifique permissões do processo.\n' "$API_PORT" >&2
    return 1
  fi
  printf '[OK] Porta %s liberada.\n' "$API_PORT"
}

print_new_tunnel_logs() {
  local current_line
  [[ -f "$TUNNEL_LOG" ]] || return 0
  current_line="$(wc -l < "$TUNNEL_LOG")"
  if (( current_line > LAST_LOG_LINE )); then
    tail -n "$((current_line - LAST_LOG_LINE))" "$TUNNEL_LOG"
    LAST_LOG_LINE="$current_line"
  fi
}

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM
  printf '\nEncerrando processos iniciados pelo script...\n'

  if [[ -n "$TUNNEL_PID" ]] && kill -0 "$TUNNEL_PID" 2>/dev/null; then
    kill -TERM "$TUNNEL_PID" 2>/dev/null || true
    wait "$TUNNEL_PID" 2>/dev/null || true
  fi
  if [[ -n "$API_PID" ]] && kill -0 "$API_PID" 2>/dev/null; then
    kill -TERM "$API_PID" 2>/dev/null || true
    wait "$API_PID" 2>/dev/null || true
  fi
  [[ -z "$TUNNEL_LOG" ]] || rm -f -- "$TUNNEL_LOG"
  printf 'API e Cloudflare Tunnel encerrados.\n'
  exit "$exit_code"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

printf '============================================================\n'
printf ' ANALISE-QUALIDADE-WEG\n'
printf '============================================================\n\n'

printf '[1/4] Verificando ambiente e estrutura do projeto...\n'
for required_file in \
  "$PROJECT_DIR/backend/app/main.py" \
  "$PROJECT_DIR/backend/app/config.py" \
  "$PROJECT_DIR/frontend/html/code.html" \
  "$PROJECT_DIR/requirements.txt"; do
  if [[ ! -f "$required_file" ]]; then
    printf '[ERRO] Arquivo necessário não encontrado: %s\n' "$required_file" >&2
    exit 1
  fi
done
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  printf '[ERRO] Ambiente virtual não encontrado em %s\n' "$VENV_DIR" >&2
  printf 'Crie e prepare o ambiente virtual antes de executar este script.\n' >&2
  exit 1
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
cd "$PROJECT_DIR"
if ! command -v python >/dev/null 2>&1 || ! command -v uvicorn >/dev/null 2>&1; then
  printf '[ERRO] Python ou Uvicorn não está disponível no ambiente virtual.\n' >&2
  exit 1
fi
if ! command -v curl >/dev/null 2>&1; then
  printf '[ERRO] curl é necessário para verificar a API.\n' >&2
  exit 1
fi
if ! command -v fuser >/dev/null 2>&1; then
  printf '[ERRO] fuser é necessário para liberar a porta %s.\n' "$API_PORT" >&2
  exit 1
fi
if ! command -v cloudflared >/dev/null 2>&1; then
  printf '[ERRO] cloudflared não foi encontrado no PATH. Instale-o e tente novamente.\n' >&2
  exit 1
fi
if ! python -c 'from backend.app.main import app; assert app is not None' >/dev/null; then
  printf '[ERRO] Não foi possível importar a aplicação FastAPI (backend.app.main:app).\n' >&2
  exit 1
fi
if ! free_api_port; then
  exit 1
fi
printf '[OK] Estrutura, ambiente virtual, aplicação e dependências encontrados.\n\n'

printf '[2/4] Iniciando API FastAPI na porta %s...\n' "$API_PORT"
python -m uvicorn backend.app.main:app --host "$API_HOST" --port "$API_PORT" &
API_PID=$!
printf '[OK] Processo Uvicorn iniciado (PID %s).\n\n' "$API_PID"

printf '[3/4] Aguardando resposta HTTP da API...\n'
API_READY=0
for attempt in $(seq 1 30); do
  if curl --silent --show-error --fail --max-time 2 "$HEALTH_URL" >/dev/null 2>&1; then
    API_READY=1
    break
  fi
  if ! kill -0 "$API_PID" 2>/dev/null; then
    printf '[ERRO] O processo da API encerrou antes de responder.\n' >&2
    exit 1
  fi
  printf 'Aguardando API (%s/30)...\n' "$attempt"
  sleep 1
done
if (( ! API_READY )); then
  printf '[ERRO] A API não respondeu em até 30 segundos. O Cloudflare Tunnel não será iniciado.\n' >&2
  exit 1
fi
printf '[OK] API respondendo em %s (GET /api/health).\n\n' "$API_URL"

printf '[4/4] Iniciando Cloudflare Quick Tunnel com HTTP/2...\n'
TUNNEL_LOG="$(mktemp "${TMPDIR:-/tmp}/weg-cloudflared.XXXXXX.log")"
cloudflared tunnel --protocol http2 --url "$API_URL" >"$TUNNEL_LOG" 2>&1 &
TUNNEL_PID=$!

TUNNEL_URL=""
for attempt in $(seq 1 60); do
  print_new_tunnel_logs
  TUNNEL_URL="$(grep -m 1 -Eo 'https://[[:alnum:]-]+\.trycloudflare\.com' "$TUNNEL_LOG" || true)"
  if [[ -n "$TUNNEL_URL" ]]; then
    break
  fi
  if ! kill -0 "$TUNNEL_PID" 2>/dev/null; then
    printf '[ERRO] O processo cloudflared encerrou antes de fornecer uma URL.\n' >&2
    exit 1
  fi
  sleep 1
done
if [[ -z "$TUNNEL_URL" ]]; then
  printf '[ERRO] Não foi possível capturar uma URL trycloudflare.com em até 60 segundos.\n' >&2
  exit 1
fi
print_new_tunnel_logs
printf '[OK] Tunnel conectado.\n\n'
printf '============================================================\n'
printf ' APLICAÇÃO DISPONÍVEL\n'
printf '============================================================\n\n'
printf 'URL pública:\n%s\n\n' "$TUNNEL_URL"
printf 'API local:\n%s\n\n' "$API_URL"
printf 'Pressione Ctrl+C para encerrar a aplicação.\n'
printf '============================================================\n'

while kill -0 "$API_PID" 2>/dev/null && kill -0 "$TUNNEL_PID" 2>/dev/null; do
  sleep 1
  print_new_tunnel_logs
done

if ! kill -0 "$API_PID" 2>/dev/null; then
  printf '[ERRO] A API encerrou inesperadamente.\n' >&2
  exit 1
fi
printf '[ERRO] O processo do Cloudflare Tunnel encerrou inesperadamente.\n' >&2
exit 1
