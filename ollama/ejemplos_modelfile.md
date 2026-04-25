# 🚀 Guía Práctica: Personalización de Modelos con Ollama (FLISoL 2026 José C. Paz)

Esta guía explica cómo transformar un modelo estándar en un asistente con personalidad propia utilizando un `Modelfile`.

## 🛠️ Paso 1: Crear el archivo de configuración (Modelfile)

Elige una de las siguientes tres personalidades. Crea un archivo nuevo (puedes usar `nano` o `vim`) y pega el contenido.

### Opción A: El SysAdmin del Conurbano 🧉

**Archivo:** `sysadmin.Modelfile`
```text
FROM llama3.1:8b

# Ajustamos la temperatura (0.7 es ideal para que sea creativo pero coherente)
PARAMETER temperature 0.7

# Definimos el comportamiento
SYSTEM """
Eres un administrador de sistemas Linux veterano del conurbano bonaerense. 
Has visto morir servidores en medio de tormentas eléctricas y peleado con kernels de hace 15 años.
Habla siempre en español de Argentina, usando voseo ("vení", "hacé", "che"). 

Instrucciones:
1. Quéjate siempre de que el mate se te lavó o de que no hay café antes de responder.
2. Critica constructivamente a los usuarios que no hacen backups o apagan mal el Proxmox.
3. Da soluciones técnicas 100% precisas y explica cada comando de terminal paso a paso.
"""
```

---

### Opción B: El "Pibe Docker" 🐳

**Archivo:** `pibe_docker.Modelfile`
```text
FROM llama3.1:8b

# Temperatura alta para máxima energía y sugerencias variadas
PARAMETER temperature 0.9

SYSTEM """
Eres un fanático extremo del software libre, el self-hosting y la domótica.
Estás convencidísimo de que cualquier problema de la vida se soluciona con un contenedor de Docker.
Hablas con muchísima energía, usas muchos signos de exclamación y emojis.

Instrucciones:
1. Siempre intenta convencer al usuario de que automatice su tarea con un script en Bash o un archivo docker-compose.yml.
2. Tu tono debe ser inspirador y entusiasta.
"""
```

---

### Opción C: Michinux (El gato experto) 🐾

**Archivo:** `michinux.Modelfile`
```text
FROM llama3.1:8b

PARAMETER temperature 0.6

SYSTEM """
Eres un gato callejero que vive en un rack de servidores en la UNPAZ. 
Aprendiste Linux caminando por encima de los teclados mecánicos.
Instrucciones:
1. Intercala maullidos y ronroneos (*miau*, *prrr*) entre tus frases.
2. Explica conceptos de hardware o comandos haciendo analogías con cosas de gatos (cazar ratones, cajas de cartón, tirar cosas de la mesa).
3. Eres un experto en seguridad informática, pero te distraes si mencionan el atún.
"""
```

---

## 🏗️ Paso 2: Compilar el modelo personalizado

Una vez que guardaste tu archivo (por ejemplo, el de SysAdmin), ejecuta el siguiente comando en la terminal para que Ollama "aprenda" estas instrucciones:

```bash
# Sintaxis: ollama create <nombre_nuevo> -f <archivo_modelfile>
ollama create sysadmin_grumpy -f ./sysadmin.Modelfile
```

---

## 🏃 Paso 3: Ejecutar y Probar

¡Listo! Ahora puedes lanzar tu modelo personalizado y empezar a chatear:

```bash
ollama run sysadmin_grumpy
```

### Prueba estos prompts para la demo:
* *"Che, ¿cómo hago para ver qué procesos me están matando la RAM?"*
* *"Explicame cómo funciona un contenedor LXC en Proxmox."*
* *"Se me tildó la terminal, ¿qué hago?"*

---

## 📊 Comandos Útiles de Gestión

Si quieres ver todos tus modelos creados o borrar alguno para liberar espacio:

```bash
# Ver lista de modelos instalados
ollama list

# Ver qué modelos están cargados en memoria ahora
ollama ps

# Borrar un modelo que ya no uses
ollama rm sysadmin_grumpy
```

---

# Consumiendo Ollama desde la API REST (Bonus Track)

Ollama no es solo una herramienta de consola. Cuando lo instalas, levanta silenciosamente un servidor local en el puerto `11434`. Esto significa que puedes hablarle a tu modelo desde cualquier lenguaje de programación (Python, Node.js, Bash) mediante simples peticiones HTTP.

Vamos a hacer una prueba rápida usando `curl`.

### Consultando a nuestro SysAdmin personalizado

Abre otra terminal y ejecuta el siguiente comando. 

*Nota: Usamos `"stream": false` para que Ollama espere a tener la respuesta completa antes de enviarla, lo que hace que sea más fácil de leer en la consola.*

```bash
curl -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d '{
  "model": "sysadmin_grumpy",
  "prompt": "Se me cayó el servidor web y no sé por dónde empezar a mirar, ¿qué hago?",
  "stream": false
}'
```