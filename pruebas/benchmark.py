"""Benchmark de rendimiento: latencia y tokens/segundo del servidor.

Uso:
    python pruebas/benchmark.py --acumuladas N --prompt "..."

Mide latencia end-to-end a través del gateway FastAPI.
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

import httpx

BASE = "http://localhost:8000"

PROMPTS = [
    "¿Qué es la fotosíntesis? Explícalo sencillo.",
    "Crea un ejemplo de lista en Python con un bucle for.",
    "Resume las causas de la Primera Guerra Mundial.",
    "Explica la ley de gravitación universal con un ejemplo cotidiano.",
]


async def un_prompt(cliente: httpx.AsyncClient, texto: str, max_tokens: int) -> dict:
    t0 = time.perf_counter()
    acumulado = ""
    async with cliente.stream(
        "POST", "/api/chat",
        json={"prompt": texto, "temperatura": 0.4, "max_tokens": max_tokens},
    ) as r:
        r.raise_for_status()
        async for frag in r.aiter_text():
            acumulado += frag
    t_total = time.perf_counter() - t0
    tokens = len(acumulado.split())
    return {
        "prompt": texto[:60],
        "tokens": tokens,
        "latencia_s": round(t_total, 3),
        "tokens_s": round(tokens / t_total, 2),
    }


async def principal(concurrente: int, acumuladas: int, max_tokens: int, salida: Path):
    cola = asyncio.Queue()
    for p in PROMPTS * acumuladas:
        await cola.put(p)

    async def trabajador(cliente, nombre):
        resultados = []
        while not cola.empty():
            try:
                texto = cola.get_nowait()
            except asyncio.QueueEmpty:
                break
            resultados.append(await un_prompt(cliente, texto, max_tokens))
        return resultados

    async with httpx.AsyncClient(base_url=BASE, timeout=300) as cliente:
        salud = await cliente.get("/health")
        estado = salud.json()
        print("Estado del servidor:", estado["status"], "| modelo cargado:", estado.get("cargado"))

        t0 = time.perf_counter()
        batches = await asyncio.gather(*[trabajador(cliente, f"w{i}") for i in range(concurrente)])
        total_s = time.perf_counter() - t0

    filas = [r for b in batches for r in b]
    total_tokens = sum(r["tokens"] for r in filas)
    latencias = [r["latencia_s"] for r in filas]
    tps = [r["tokens_s"] for r in filas]

    resumen = {
        "peticiones": len(filas),
        "concurrentes": concurrente,
        "max_tokens": max_tokens,
        "total_tokens": total_tokens,
        "tiempo_total_s": round(total_s, 3),
        "resumen_por_peticion": {
            "latencia_promedio_s": round(sum(latencias) / len(latencias), 3),
            "tokens_s_promedio": round(sum(tps) / len(tps), 2),
            "mejor_latencia_s": round(min(latencias), 3),
            "peor_latencia_s": round(max(latencias), 3),
            "tokens_s_min": round(min(tps), 2),
            "tokens_s_max": round(max(tps), 2),
        },
        "detalle": filas,
    }
    salida.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen["resumen_por_peticion"], ensure_ascii=False, indent=2))
    print("Resultados guardados en", salida)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--concurrente", type=int, default=1)
    parser.add_argument("-n", "--acumuladas", type=int, default=3)
    parser.add_argument("-t", "--max_tokens", type=int, default=256)
    parser.add_argument("-o", "--salida", default="resultados.json")
    args = parser.parse_args()
    asyncio.run(principal(args.concurrente, args.acumuladas, args.max_tokens, Path(args.salida)))