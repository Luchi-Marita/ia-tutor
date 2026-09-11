import asyncio
import json

import httpx

BASE = "http://localhost:8000"


async def probar():
    async with httpx.AsyncClient(base_url=BASE, timeout=60) as cliente:
        salud = await cliente.get("/health")
        print("GET /health ->", salud.status_code, salud.json())

        modelos = await cliente.get("/api/models")
        print("GET /api/models ->", modelos.json()["modelos"])

        print("POST /api/chat (streaming)…")
        carga = {"prompt": "Explica en 3 pasos qué es una función en Python.", "temperatura": 0.5, "max_tokens": 256}
        acumulado = ""
        async with cliente.stream("POST", "/api/chat", json=carga) as r:
            r.raise_for_status()
            async for frag in r.aiter_text():
                acumulado += frag
        print("Respuesta completa:\n", acumulado)

        metrica = await cliente.get("/api/metrics")
        print("GET /api/metrics ->", json.dumps(metrica.json(), indent=2))


if __name__ == "__main__":
    asyncio.run(probar())