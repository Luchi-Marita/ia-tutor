import os
from pathlib import Path

MODELO = "llama3.2"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
TEMPERATURA_DEFECTO = 0.7
MAX_TOKENS_DEFECTO = 512
BASE_DIR = Path(__file__).resolve().parent