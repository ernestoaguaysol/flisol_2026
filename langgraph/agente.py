# agente.py
import sqlite3
import requests
from bs4 import BeautifulSoup
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# ==========================================
# 1. DEFINICIÓN DE HERRAMIENTAS (TOOLS)
# ==========================================

@tool
def consultar_base_datos(query_sql: str) -> str:
    """Útil para ejecutar consultas SQL en la base de datos de la tienda (clientes, productos, compras).
    El input debe ser una query SQL válida en texto plano."""
    try:
        print("Usando la tool BD. Query:")
        print(query_sql)
        conn = sqlite3.connect('tienda.db')
        cursor = conn.cursor()
        cursor.execute(query_sql)
        resultados = cursor.fetchall()
        conn.close()
        print("Resultados de la query:")
        print(resultados)
        return str(resultados) if resultados else "No se encontraron resultados."
    except Exception as e:
        return f"Error ejecutando SQL: {e}"

@tool
def consultar_documentacion_tienda() -> str:
    """Útil para buscar información, horarios o datos de la tienda. 
    Lee la documentación con la información de la tienda."""
    try:
        # Hacemos scraping del contenedor Docker local
        response = requests.get("https://docs.google.com/document/d/15y58dFleZJfrxDl_e075vkIKJe8plUIlIQSOpXQVZEs/export?format=html")
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extraemos solo el texto para no marear al LLM con etiquetas HTML
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        return f"Error accediendo a la web: {e}"

# Lista de herramientas disponibles para el agente
herramientas = [consultar_base_datos, consultar_documentacion_tienda]

# ==========================================
# 2. CONFIGURACIÓN DEL LLM Y EL ESTADO
# ==========================================

# Definimos el estado del grafo (básicamente, el historial de mensajes)
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Instanciamos el modelo local y le "enseñamos" qué herramientas tiene
# llm = ChatOllama(model="llama3.1:8b", temperature=0)
llm = ChatOllama(model="gemma4:31b-cloud", temperature=0, base_url="http://172.18.0.1:11434")
# llm = ChatOllama(model="qwen3.5:9b", temperature=0)
llm_con_herramientas = llm.bind_tools(herramientas)

# ==========================================
# 3. CREACIÓN DE LOS NODOS DEL GRAFO
# ==========================================

def nodo_asistente(state: State):
    """Este nodo llama al LLM para que decida qué hacer."""
    
    # === NUEVO: INSPECTOR DE HISTORIAL ===
    print("\n📚 --- LEYENDO EL HISTORIAL ACUMULADO ---")
    for i, mensaje in enumerate(state["messages"]):
        tipo = type(mensaje).__name__
        texto = mensaje.content
        
        # Si es un AIMessage pero el texto está vacío, significa que es un llamado a herramienta
        if tipo == "AIMessage" and not texto and hasattr(mensaje, 'tool_calls') and mensaje.tool_calls:
            texto = f"[Llamando a herramienta: {mensaje.tool_calls[0]['name']}]"
        
        # Si es un ToolMessage (resultado de la BD), lo truncamos para no inundar la consola
        elif tipo == "ToolMessage":
            texto = f"[Resultado de la herramienta: {texto[:50]}...]"
            
        print(f"{i}. {tipo}: {texto}")
    print("------------------------------------------\n")
    # =====================================


    # Le damos un contexto fuerte al modelo (System Prompt)
    instrucciones = SystemMessage(content="""
        Eres un agente de sistema con ejecución directa de código. Tienes ACCESO TOTAL a las herramientas.
        REGLA ESTRICTA: NUNCA te disculpes ni digas que no tienes acceso a la base de datos o a internet. 

        Para responder, DEBES invocar OBLIGATORIAMENTE la herramienta correspondiente:

        1. Herramienta 'consultar_base_datos': 
        Úsala SIEMPRE que pregunten por clientes, emails, productos, precios o compras.
        Esquema SQLite exacto:
        - Tabla 'clientes' (id, nombre, email)
        - Tabla 'productos' (id, nombre, precio)
        - Tabla 'compras' (id, cliente_id, producto_id, fecha)
        Tu tarea es generar la query SQL (ej: "SELECT email FROM clientes") y pasarla a la herramienta. NO expliques cómo hacerlo, solo ejecuta la herramienta.

        2. Herramienta 'consultar_documentacion_tienda': 
        Úsala SIEMPRE que pregunten por información de la tienda, horarios o datos generales.

        REGLA FINAL Y MUY IMPORTANTE (CÓMO RESPONDER AL USUARIO):
        Cuando recibas el mensaje con el resultado de la herramienta, TU ÚNICA TAREA es leer los datos y redactar una respuesta natural y directa para el usuario.
        - ESTÁ ESTRICTAMENTE PROHIBIDO mencionar las herramientas. NUNCA digas "Usé la herramienta X" ni "La respuesta fue generada por...".
        - NUNCA expliques tu proceso interno.
        - Si la herramienta te devuelve "HORARIO DE APERTURA: 11hs", tú simplemente respondes: "¡Hola! El horario de apertura de la tienda es a las 11hs."
    """)
    
    # Armamos la lista de mensajes: Instrucciones + Historial del usuario
    mensajes_completos = [instrucciones] + state["messages"]
    
    # Invocamos al modelo con las instrucciones inyectadas
    respuesta = llm_con_herramientas.invoke(mensajes_completos)
    
    # === EL CÓDIGO PARA INSPECCIONAR ===
    print("\n--- [MODO INSPECCIÓN: LO QUE EL LLM PENSÓ] ---")
    print(f"Contenido de texto normal: '{respuesta.content}'")
    print(f"Llamados a herramientas (JSON): {respuesta.tool_calls}")
    print("---------------------------------------------\n")

    return {"messages": [respuesta]}

# ToolNode es una utilidad de LangGraph que ejecuta automáticamente 
# la herramienta que el LLM haya solicitado.
nodo_herramientas = ToolNode(herramientas)

# ==========================================
# 4. CONSTRUCCIÓN DEL GRAFO (LANGGRAPH)
# ==========================================

builder = StateGraph(State)

# Agregamos los nodos al grafo
builder.add_node("asistente", nodo_asistente)
builder.add_node("tools", nodo_herramientas)

# Definimos el flujo lógico
builder.add_edge(START, "asistente")

# "tools_condition" es la magia: si el LLM pidió usar una herramienta,
# rutea hacia el nodo "herramientas". Si el LLM dio una respuesta final en texto, rutea al END.
builder.add_conditional_edges(
    "asistente",
    tools_condition, 
)

# Después de usar la herramienta, siempre vuelve al asistente para que lea el resultado
builder.add_edge("tools", "asistente")

# Memoria de corto plazo - Guarda checkpoints en 
memoria_agente = MemorySaver()

# Compilamos el grafo
sistema_multiagente = builder.compile(checkpointer=memoria_agente)

# ==========================================
# 5. BUCLE DE EJECUCIÓN (CLI)
# ==========================================

if __name__ == "__main__":
    print("Sistema Multiagente Iniciado (Escribe 'salir' para terminar)")

    # Creamos un identificador de sesión. 
    # Todo lo que se ejecute bajo este ID compartirá la misma memoria.
    configuracion_hilo = {"configurable": {"thread_id": "demo_flisol_1"}}

    while True:
        prompt_usuario = input("\nUsuario: ")
        if prompt_usuario.lower() in ['salir', 'exit', 'quit']:
            break
            
        # Ejecutamos el grafo pasándole el mensaje del usuario
        estado_final = sistema_multiagente.invoke(
            {"messages": [HumanMessage(content=prompt_usuario)]},
            config=configuracion_hilo
        )
        
        # Imprimimos la respuesta final del agente
        print(f"\nAgente: {estado_final['messages'][-1].content}")
        # print(f"\nAgente: {estado_final['messages'][-1]}")