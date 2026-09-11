# IA-Tutor · Servidor de IA + Aplicativo web con Llama 3.2

Proyecto final de la actividad de **infraestructura y despliegue de IA generativa de código abierto**.
Consiste en un **tutor académico interactivo** que usa `Ollama` como servidor de inferencia con el
modelo `llama3.2` (Meta, cuantizado GGUF) y una **aplicación web** con backend `FastAPI` y frontend
HTML/JS que consume la API vía **streaming** en tiempo real.

## Arquitectura

```
┌─────────────┐   HTTP/JSON    ┌──────────────────┐   REST + SSE   ┌──────────────┐
│  Cliente    │──────────────▶ │ Gateway FastAPI  │──────────────▶ │ Ollama (LLM) │
│ (Navegador) │                │  /api/chat       │                │ llama3.2     │
└─────────────┘                │  /health         │                └──────────────┘
                               │  /api/metrics    │
```

- **Ollama** expone `/api/chat` (REST, streaming) sobre `llama3.2` (GGUF Q4_K_M, ~2 GB).
- **Gateway FastAPI** (`server/`) sirve el frontend, retransmite el streaming al navegador y acumula
  métricas de rendimiento (latencia, primer token, tokens/segundo).
- **Frontend** (`webapp/`) permite ajustar temperatura, máximo de tokens y rol de tutor, además de
  mostrar la respuesta token a token.

## Requisitos previos

- Python 3.10+ (probado con 3.12/3.14)
- Windows, Linux o macOS
- Opcional: GPU NVIDIA (6 GB VRAM suficientes para llama3.2). Sin GPU, funciona por CPU.
- RAM recomendada: 8 GB o más.

## Instalación

### Opción A: Instalador automático

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1
```

**Linux/macOS:**
```bash
bash scripts/instalar.sh
```

### Opción B: Manual

1. Instalar Ollama desde https://ollama.com/download (Windows/macOS) o
   `curl -fsSL https://ollama.com/install.sh | sh` (Linux).
2. Iniciar Ollama y descargar el modelo:
   ```bash
   ollama serve        # deja el servicio corriendo
   ollama pull llama3.2
   ```
3. Crear el entorno Python e instalar dependencias:
   ```bash
   python -m venv .venv
   .venv\Scripts\pip install -r server\requirements.txt        # Windows
   source .venv/bin/activate && pip install -r server/requirements.txt   # Linux/macOS
   ```

### Opción C: Docker (GPU opcional)

```bash
docker compose up -d --build
```

## Ejecución

```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000
# o: .venv\Scripts\uvicorn server.main:app --host 0.0.0.0 --port 8000
```

Abrir **http://localhost:8000**.

## Endpoints de la API

| Método | Ruta           | Descripción                                        |
|--------|----------------|----------------------------------------------------|
| GET    | `/`            | Aplicativo web                                     |
| GET    | `/health`      | Estado de Ollama y modelo cargado                  |
| GET    | `/api/models`  | Lista de modelos disponibles en Ollama             |
| POST   | `/api/chat`    | Genera respuesta (streaming). Body: `prompt`, `temperatura`, `max_tokens`, `historial`, `sistema` |
| GET    | `/api/metrics` | Métricas acumuladas (latencia, tokens/s, errores)  |

Ejemplo con `curl`:

```bash
curl -N http://localhost:8000/api/chat -H "Content-Type: application/json" \
  -d '{"prompt":"Explica qué es una neurona artificial","temperatura":0.5,"max_tokens":256}'
```

## Pruebas y benchmark

```bash
# Prueba de humo de la API
python pruebas/test_api.py

# Benchmark de latencia y tokens/segundo
python pruebas/benchmark.py -n 5 -t 256 -o pruebas/resultados.json
```

Los resultados quedan en `pruebas/resultados.json` (promedios de latencia y tokens/s).

## Estructura del repositorio

```
TALLER/
├── server/            # Gateway FastAPI (API REST + métricas + streaming)
├── webapp/static/     # Frontend (HTML, CSS, JS)
├── pruebas/           # test_api.py, benchmark.py y resultados
├── scripts/           # Instaladores automáticos (Windows y Linux/macOS)
├── informe/           # Generador y archivos del informe (PDF y DOCX)
├── docker-compose.yml # Despliegue contenerizado opcional
└── Dockerfile
```

## Troubleshooting

- **"Ollama no disponible"**: inicia el servicio con `ollama serve` y verifica `http://localhost:11434`.
- **"Modelo no descargado"**: ejecuta `ollama pull llama3.2`.
- **Respuestas lentas**: reduce `max_tokens`, usa un modelo más pequeño (`ollama pull llama3.2:1b`) o
  activa el uso de GPU instalando CUDA en Windows.