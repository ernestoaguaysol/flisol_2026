# Instalar ollama en Windows

## Opción 1 con instalador

Ejecutar el instalador:

Abrir PowerShell como **Administrador**.

Ir hasta al directorio donde se encuentra `PrepararOllama.ps1`

Ejecutar el script: 

```
.\PrepararOllama.ps1
```
> [!WARNING]
> Si da error de ejecución, usa primero: 
>
>```
>Set-ExecutionPolicy Bypass -Scope Process
>```

Si se reinicia la PC, desde el administrador de tareas chequear que no esté el proceso de ollama y ollama app ejecutándose ya que por defecto toma la ruta C:\User\\.ollama, si está ejecutándose entonces hay que **Finalizar tarea** antes de ejecutar el siguiente script.

Ir hasta al directorio donde se encuentra flisol.

Ejecutar el script: .\Iniciar_Ollama.ps1

(Si da error de ejecución, usa primero: Set-ExecutionPolicy Bypass -Scope Process).

## Opción 2 manual 

```
$env:OLLAMA_INSTALL_DIR="D:\Ollama"; $env:OLLAMA_MODELS="D:\OllamaModels"; $env:OLLAMA_HOST="0.0.0.0"; irm https://ollama.com/install.ps1 | iex
```

Si se reinicia la PC, desde el administrador de tareas chequear que no esté el proceso de ollama y ollama app ejecutándose ya que por defecto toma la ruta C:\User\.ollama, si está ejecutándose entonces hay que Finalizar tarea antes de ejecutar ollama serve.

```
$env:OLLAMA_INSTALL_DIR="D:\Ollama"; $env:OLLAMA_MODELS="D:\OllamaModels"; $env:OLLAMA_HOST="0.0.0.0"; ollama serve
```

## Descargar y ejecutar modelos

```
ollama run llama3.1:8b
```

> [!NOTE] 
> Más modelos en https://ollama.com/library

## WSL

Para que se pueda ejecutar ollama en Ubuntu WSL.

```
echo "export OLLAMA_HOST=\"http://\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2}'):11434\"" >> ~/.bashrc
echo "alias ollama='ollama.exe'" >> ~/.bashrc
source ~/.bashrc
```

### Probar comunicación entre WSL y Ollama

```
ollama ls
```

Ver ip para poner en código de langgraph

```
ip route show default | awk '{print $3}'
```

```
ip route show default
```
