import json
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import ollama_client
from .config import MAX_TOKENS_DEFECTO, TEMPERATURA_DEFECTO
from .metricas import metricas

SISTEMA_TUTOR = (
    "Eres 'IA-Tutor', un tutor académico amable y didáctico. "
    "Responde en español, explica paso a paso y con ejemplos sencillos, "
    "y pregunta al estudiante si desea profundizar en algún tema."
)

BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR.parent / "webapp"

app = FastAPI(title="IA-Tutor · Servidor de inferencia LLM", version="1.0.0")
app.mount("/static", StaticFiles(directory=WEBAPP_DIR / "static"), name="static")


@app.get("/")
async def indice():
    return FileResponse(WEBAPP_DIR / "static" / "index.html")


@app.get("/health")
async def health():
    ok, estado = await ollama_client.verificar_ollama()
    return {"status": "ok" if ok else "error", **estado}


@app.get("/api/health")
async def api_health():
    return await health()


@app.get("/api/models")
async def modelos():
    ok, estado = await ollama_client.verificar_ollama()
    if not ok:
        return {"modelos": [], "error": estado.get("detalle")}
    return {"modelos": estado.get("modelos", [])}


@app.post("/api/chat")
async def chat(peticion: Request):
    cuerpo = await peticion.json()
    prompt = (cuerpo.get("prompt") or "").strip()
    if not prompt:
        return {"error": "El prompt no puede estar vacío"}

    temperatura = float(cuerpo.get("temperatura", TEMPERATURA_DEFECTO))
    max_tokens = int(cuerpo.get("max_tokens", MAX_TOKENS_DEFECTO))
    historial = cuerpo.get("historial") or []
    usar_sistema = bool(cuerpo.get("sistema", True))

    t0 = time.perf_counter()
    primer_token = None
    tokens = 0

    async def generador():
        nonlocal primer_token, tokens
        try:
            async for linea in ollama_client.generar_respuesta_stream(
                prompt, historial, temperatura, max_tokens,
                sistema=SISTEMA_TUTOR if usar_sistema else None,
            ):
                if primer_token is None:
                    primer_token = time.perf_counter() - t0
                obj = json.loads(linea)
                tokens += 1
                fragmento = obj.get("message", {}).get("content", "")
                if fragmento:
                    yield fragmento
        except Exception as exc:  # noqa: BLE001
            metricas.registrar_error()
            yield f"\n[Error de inferencia: {exc}]"

    async def generar_con_metrica():
        try:
            async for fragmento in generador():
                yield fragmento
        finally:
            t_fin = time.perf_counter() - t0
            metricas.registrar(tokens, t_fin, primer_token or t_fin)

    return StreamingResponse(
        generar_con_metrica(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/metrics")
async def api_metricas():
    return metricas.resumen()