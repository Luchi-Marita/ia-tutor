import time


class Metricas:
    def __init__(self) -> None:
        self._reiniciar()

    def _reiniciar(self) -> None:
        self.peticiones = 0
        self.tokens_generados = 0
        self.tiempo_inferencia_total = 0.0
        self.tiempo_primer_token_total = 0.0
        self.errores = 0
        self.ultima = {}

    def registrar(self, tokens: int, tiempo_inferencia: float, primer_token: float) -> None:
        self.peticiones += 1
        self.tokens_generados += tokens
        self.tiempo_inferencia_total += tiempo_inferencia
        self.tiempo_primer_token_total += primer_token
        self.ultima = {
            "tokens": tokens,
            "tiempo_inferencia_s": round(tiempo_inferencia, 3),
            "tiempo_primer_token_s": round(primer_token, 3),
            "tokens_por_segundo": round(tokens / tiempo_inferencia, 2) if tiempo_inferencia > 0 else 0.0,
            "timestamp": time.time(),
        }

    def registrar_error(self) -> None:
        self.errores += 1

    def resumen(self) -> dict:
        if self.peticiones == 0:
            return {
                "peticiones": 0,
                "errores": 0,
                "promedio_tokens_s": 0.0,
                "promedio_latencia_s": 0.0,
                "promedio_primer_token_s": 0.0,
                "ultima": None,
            }
        return {
            "peticiones": self.peticiones,
            "errores": self.errores,
            "promedio_tokens_s": round(self.tokens_generados / max(self.tiempo_inferencia_total, 1e-9), 2),
            "promedio_latencia_s": round(self.tiempo_inferencia_total / self.peticiones, 3),
            "promedio_primer_token_s": round(self.tiempo_primer_token_total / self.peticiones, 3),
            "ultima": self.ultima,
        }


metricas = Metricas()