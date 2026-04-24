# --- CONFIGURACIÓN DE RUTAS ---
$baseDir = "D:\flisol"
$rutaApp = "$baseDir\Ollama"
$rutaModelos = "$baseDir\OllamaModels"
$lanzadorPath = "$baseDir\Iniciar_Ollama.ps1"

Write-Host "--- Iniciando configuración de Ollama para FLISoL ---" -ForegroundColor Cyan

# 1. CREAR CARPETA BASE OCULTA
if (!(Test-Path $baseDir)) {
    $carpetaBase = New-Item -ItemType Directory -Path $baseDir -Force
    $carpetaBase.Attributes = $carpetaBase.Attributes -bor [System.IO.FileAttributes]::Hidden
    Write-Host "[OK] Carpeta base oculta creada en $baseDir" -ForegroundColor Green
}

# 2. CREAR SUBCARPETAS
if (!(Test-Path $rutaApp)) {
    New-Item -ItemType Directory -Path $rutaApp -Force | Out-Null
    Write-Host "[OK] Carpeta de aplicación creada en $rutaApp" -ForegroundColor Green
}

if (!(Test-Path $rutaModelos)) {
    New-Item -ItemType Directory -Path $rutaModelos -Force | Out-Null
    Write-Host "[OK] Carpeta de modelos creada en $rutaModelos" -ForegroundColor Green
}

# 3. EJECUTAR INSTALACIÓN
Write-Host "Descargando e instalando Ollama..." -ForegroundColor Yellow
$env:OLLAMA_INSTALL_DIR = $rutaApp
$env:OLLAMA_MODELS = $rutaModelos

irm https://ollama.com/install.ps1 | iex

# 4. CREAR SCRIPT LANZADOR (Método seguro, sin caracteres de escape)
Write-Host "Creando script lanzador..." -ForegroundColor Yellow

$linea1 = '$env:OLLAMA_MODELS = "' + $rutaModelos + '"'
$linea2 = '$env:PATH += ";' + $rutaApp + '"'
$linea_host = '$env:OLLAMA_HOST = "0.0.0.0"'
$linea3 = 'Write-Host "Configurando entorno de Ollama para FLISoL..." -ForegroundColor Cyan'
$linea4 = 'Write-Host "Modelos en: ' + $rutaModelos + '" -ForegroundColor Gray'
$linea_aviso = 'Write-Host "Servidor abierto para conexiones externas (WSL/LAN)" -ForegroundColor Yellow'
$linea5 = 'ollama serve'

# Guardamos las líneas en el archivo
$linea1, $linea2, $linea_host, $linea3, $linea4, $linea_aviso, $linea5 | Out-File -FilePath $lanzadorPath -Encoding utf8

Write-Host "[OK] Lanzador creado en $lanzadorPath" -ForegroundColor Green

Write-Host '--- INSTALACIÓN COMPLETADA ---' -ForegroundColor Cyan
Write-Host 'Todo el entorno, binarios y carpetas para modelos fueron instalados correctamente.' -ForegroundColor Magenta
Write-Host 'Para usar Ollama tras reiniciar, ejecuta el archivo Iniciar_Ollama.ps1' -ForegroundColor White