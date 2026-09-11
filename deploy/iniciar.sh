#!/bin/sh
# Punto de entrada para el servicio Ollama en Render.
# Inicia el servidor, descarga el modelo y mantiene el proceso vivo.
set -e

MODELO="${MODELO:-llama3.2}"
echo "Iniciando Ollama..."
ollama serve &
SERVE_PID=$!

sleep 6

echo "Descargando modelo ${MODELO}..."
ollama pull "${MODELO}"

wait $SERVE_PID