#!/usr/bin/env bash
# Instalador para GNU/Linux y macOS.
set -euo pipefail

echo "=== Instalador IA-Tutor (Linux/macOS) ==="

# 1. Instalar Ollama
if ! command -v ollama >/dev/null 2>&1; then
  echo "[1/4] Instalando Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "[1/4] Ollama ya está instalado"
fi

# 2. Iniciar servicio si no está corriendo
echo "[2/4] Verificando Ollama..."
if ! curl -s http://localhost:11434 >/dev/null 2>&1; then
  ollama serve &
  sleep 5
fi

# 3. Descargar modelo
echo "[3/4] Descargando modelo llama3.2..."
ollama pull llama3.2

# 4. Entorno Python
echo "[4/4] Preparando entorno Python..."
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r server/requirements.txt

echo ""
echo "Instalación completada. Ejecuta:"
echo "   .venv/bin/uvicorn server.main:app --host 0.0.0.0 --port 8000"
echo "Luego abre http://localhost:8000"