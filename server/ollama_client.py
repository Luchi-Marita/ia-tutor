import httpx

from .config import MODELO, OLLAMA_URL


async def generar_respuesta_stream(
    prompt: str,
    historial: list | None = None,
    temperatura: float = 0.7,
    max_tokens: int = 512,
    sistema: str | None = None,
):
    mensajes = list(historial or [])
    if sistema:
        mensajes.insert(0, {"role": "system", "content": sistema})
    mensajes.append({"role": "user", "content": prompt})

    payload = {
        "model": MODELO,
        "messages": mensajes,
        "stream": True,
        "options": {
            "temperature": temperatura,
            "num_predict": max_tokens,
        },
    }

    async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=None) as cliente:
        async with cliente.stream("POST", "/api/chat", json=payload) as respuesta:
            respuesta.raise_for_status()
            async for linea in respuesta.aiter_lines():
                if linea.strip():
                    yield linea


async def verificar_ollama() -> tuple[bool, dict]:
    try:
        async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=3) as cliente:
            respuesta = await cliente.get("/api/tags")
            if respuesta.status_code != 200:
                return False, {"detalle": f"Ollama respondió {respuesta.status_code}"}
            modelos = respuesta.json().get("models", [])
            nombres = [m.get("name", "") for m in modelos]
            return True, {
                "ollama": True,
                "modelos": nombres,
                "modelo_requerido": MODELO,
                "cargado": any(n.startswith(MODELO) for n in nombres),
            }
    except Exception as exc:  # noqa: BLE001
        return False, {"ollama": False, "detalle": str(exc)}