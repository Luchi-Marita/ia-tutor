# instalador para Windows (PowerShell)
# Instala Ollama, descarga el modelo y deja listo el entorno del proyecto.

Write-Host "=== Instalador IA-Tutor (Windows) ===" -ForegroundColor Cyan

# 1. Instalar Ollama (si no existe)
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "[1/4] Instalando Ollama via winget..." -ForegroundColor Yellow
    winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Falló winget. Descarga manual en https://ollama.com/download" -ForegroundColor Red
        exit 1
    }
    # recargar PATH para usar 'ollama'
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "[1/4] Ollama ya está instalado" -ForegroundColor Green
}

# 2. Asegurar que el servicio de Ollama esté en ejecución
Write-Host "[2/4] Verificando servicio de Ollama..." -ForegroundColor Yellow
try { Invoke-WebRequest -UseBasicParsing http://localhost:11434 -TimeoutSec 2 | Out-Null }
catch {
    Write-Host "Iniciando Ollama..." -ForegroundColor Yellow
    Start-Process ollama -ArgumentList "serve"
    Start-Sleep -Seconds 5
}

# 3. Descargar el modelo llama3.2 (cuantizado, ~2 GB)
Write-Host "[3/4] Descargando modelo llama3.2..." -ForegroundColor Yellow
ollama pull llama3.2
if ($LASTEXITCODE -ne 0) { Write-Host "Error al descargar el modelo" -ForegroundColor Red; exit 1 }

# 4. Crear entorno Python e instalar dependencias
Write-Host "[4/4] Preparando entorno Python..." -ForegroundColor Yellow
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r server\requirements.txt

Write-Host ""
Write-Host "Instalación completada." -ForegroundColor Green
Write-Host "Ejecuta la app con:"
Write-Host "   .\.venv\Scripts\python.exe -m uvicorn server.main:app --host 0.0.0.0 --port 8000"
Write-Host "Luego abre http://localhost:8000"