# Python MCP Chat – Explicación Paso a Paso

En este documento vamos a estudiar juntos cómo está construida la aplicación **Python MCP Chat**, qué tecnologías utiliza, cuál es su propósito y cómo encajan las distintas piezas. Lo haré como si estuviera explicándotelo en clase, paso a paso.

---

## 1. ¿Qué es Python MCP Chat?

Imagina que tienes un asistente de IA (como Claude) y quieres que pueda **leer y escribir en un chat persistente**, con hilos (threads), canales y reacciones con emojis. La IA no sabe hacer eso por sí sola: necesita que tú le des una "ventana" hacia una aplicación externa.

Esa "ventana" es el **Model Context Protocol (MCP)**: un protocolo que define cómo un modelo se comunica con servicios externos mediante **herramientas**.

**Python MCP Chat** es precisamente eso:

- Un **servidor MCP** escrito en **Python**
- Que implementa **14 herramientas MCP** relacionadas con un sistema de chat
- Que guarda la información en una base de datos SQLite usando **SQLAlchemy**
- Y que opcionalmente expone una **API REST** con **FastAPI** para acceder al mismo chat desde HTTP.

En resumen: es un **backend de chat especializado para ser usado como herramienta por modelos de IA**, pero también accesible como API clásica.

---

## 2. Visión general de la arquitectura

La estructura del proyecto (simplificada) es:

```text
python-mcp-chat/
├── app/
│   ├── main.py        # Servidor MCP (entrada principal para MCP)
│   ├── api.py         # API REST opcional con FastAPI
│   ├── database.py    # Conexión a la base de datos y sesión
│   ├── models.py      # Modelos SQLAlchemy (Message, Reaction)
│   ├── schemas.py     # Esquemas Pydantic (validación)
│   ├── crud.py        # Lógica de acceso a datos (queries)
│   ├── config.py      # Constantes y configuración (ej. emojis permitidos)
│   └── __init__.py    # Metadata del paquete
├── seed.py            # Script para inicializar la base de datos con datos
├── README.md          # Documentación principal
└── EXPLICACION_APP.md # Este documento
```

La idea es separar claramente **responsabilidades**:

- `main.py`: habla el lenguaje MCP (herramientas, entrada/salida por stdio) y traduce peticiones en llamadas a funciones Python.
- `api.py`: expone prácticamente la misma funcionalidad por HTTP usando FastAPI.
- `database.py`: configura SQLAlchemy, la conexión a SQLite y la creación de tablas.
- `models.py`: define las tablas `messages` y `reactions` como clases Python.
- `schemas.py`: define las formas de entrada/salida de datos (inputs de herramientas, requests/responses de la API) usando Pydantic.
- `crud.py`: contiene las operaciones de lectura y escritura (create, read, update, delete) sobre la base de datos.
- `config.py`: define constantes como la lista de emojis permitidos.

---

## 3. Stack tecnológico

La aplicación utiliza varias tecnologías modernas en el ecosistema Python:

- **Python 3.10+**: versión mínima recomendada por el proyecto.
- **FastAPI** (`app/api.py`): framework web asíncrono para exponer una API REST.
- **SQLAlchemy 2.0** (`app/models.py`, `app/database.py`): ORM para mapear clases Python a tablas SQL.
- **Pydantic v2** (`app/schemas.py`): validación de datos de entrada y salida.
- **mcp library** (`app/main.py`): implementación de un servidor MCP.
- **SQLite**: base de datos ligera para persistir mensajes y reacciones.
- **Uvicorn**: servidor ASGI para ejecutar la API FastAPI.

Cada pieza tiene un rol:

- SQLAlchemy + SQLite → persistencia de datos
- Pydantic → validación y documentación de estructuras de datos
- FastAPI → endpoints HTTP
- MCP server → interfaz para el modelo de IA

---

## 4. El modelo de datos: mensajes y reacciones

La base de datos define dos entidades principales: `Message` y `Reaction`, implementadas en `app/models.py` con SQLAlchemy.

### 4.1. Modelo `Message`

`Message` representa un mensaje en el chat:

- `id`: identificador único (clave primaria).
- `parent_id`: referencia opcional a otro mensaje; si es `NULL`, el mensaje es "principal"; si tiene valor, es una **respuesta** (thread).
- `name`: nombre del usuario que envía el mensaje (máx. 50 caracteres).
- `content`: contenido del mensaje (máx. 500 caracteres).
- `channel`: canal donde se envía el mensaje (ej: `general`, `python`).
- `created_at` y `updated_at`: marcas de tiempo de creación y actualización.

Relaciones importantes:

- `parent`: referencia al mensaje padre (self‑referential).
- `replies`: lista de respuestas a este mensaje (relación uno‑a‑muchos sobre sí mismo).
- `reactions`: lista de reacciones (emojis) asociadas al mensaje.

También define índices para optimizar:

- `parent_id` → para navegar threads
- `created_at` → para ordenar/filtrar por fecha
- `channel` (index=True) → para filtrar por canal

### 4.2. Modelo `Reaction`

`Reaction` representa una reacción con emoji a un mensaje:

- `id`: identificador único.
- `message_id`: referencia al mensaje al que reacciona.
- `user_name`: nombre del usuario que reaccionó.
- `emoji`: emoji usado.
- `created_at`, `updated_at`: timestamps.

Restricciones clave:

- **Constraint único** `(message_id, user_name, emoji)`: un mismo usuario no puede poner el mismo emoji varias veces al mismo mensaje.
- Índice `message_id`: para recuperar rápidamente todas las reacciones de un mensaje.

Relación:

- `message`: referencia al mensaje asociado (lado inverso de `Message.reactions`).

### 4.3. Cascadas

Ambos modelos usan `ondelete="CASCADE"` y relaciones con `cascade="all, delete-orphan"`. ¿Qué implica?

- Si borras un mensaje, se borran **automáticamente**:
  - sus respuestas (`replies`)
  - sus reacciones (`reactions`)
  - y recursivamente los threads asociados

De esta forma, la base de datos se mantiene limpia y coherente.

---

## 5. Capa de acceso a datos (CRUD)

Aunque en este documento no copiamos el contenido completo de `app/crud.py`, según el `README.md` esta capa contiene funciones como:

- `send_message(db, name, content, channel)` → crear un nuevo mensaje.
- `get_messages(db, limit)` → obtener mensajes recientes, incluyendo conteos de respuestas y reacciones.
- `reply_to_message(db, parent_message_id, name, content)` → crear una respuesta en un thread.
- `get_message_thread(db, message_id)` → obtener un mensaje y todas sus respuestas anidadas.
- `get_channels(db)` → listar canales con estadísticas (número de mensajes, última actividad).
- `get_channel_messages(db, channel, limit)` → mensajes de un canal concreto.
- `add_reaction(db, message_id, user_name, emoji)` → añadir una reacción.
- `remove_reaction(db, message_id, user_name, emoji)` → quitar una reacción.
- `get_message_reactions(db, message_id)` → ver las reacciones de un mensaje agrupadas.
- `get_users_list(db, limit, sort_by)` → estadísticas de usuarios.
- `search_messages(db, query, limit)` → búsqueda por texto.
- `get_messages_by_user(db, name, limit)` → mensajes de un usuario.
- `get_messages_by_date_range(db, start_date, end_date, limit)` → mensajes dentro de un intervalo de fechas.

Esta capa se encarga de traducir las necesidades de negocio a **consultas SQL eficientes**, usando:

- `select()` de SQLAlchemy 2.0
- subqueries para contar respuestas/reacciones
- `GROUP BY` para estadísticas
- uso de índices en columnas consultadas frecuentemente

Tú, como consumidor (desde MCP o desde la API), no trabajas directamente con SQL: llamas a funciones de `crud.py`.

---

## 6. Esquemas y validación con Pydantic

En `app/schemas.py` (no lo hemos listado aquí, pero se describe en el README) se definen los **esquemas Pydantic** que sirven para:

1. Describir los **parámetros de entrada** de las herramientas MCP
2. Describir los **parámetros de entrada y salida** de la API REST

Ejemplos de esquemas (por nombre):

- `SendMessageInput`: campos `name`, `content`, `channel`.
- `GetMessagesInput`: campo `limit`.
- `ReplyToMessageInput`: `parent_message_id`, `name`, `content`.
- `AddReactionInput`: `message_id`, `user_name`, `emoji`.
- etc.

Estos esquemas incluyen validaciones como:

- `name`: longitud entre 1 y 50.
- `content`: longitud entre 1 y 500.
- `channel`: máx. 50 caracteres.
- `limit`: entre 1 y 100.
- `emoji`: debe estar en `ALLOWED_EMOJIS`.

Pydantic se encarga de:

- Convertir tipos (por ejemplo, strings a `datetime`).
- Lanzar errores de validación si algo no cumple las reglas.

Esto lo aprovechan tanto MCP como FastAPI para validar automáticamente los datos entrantes.

---

## 7. Configuración y constantes (`config.py`)

En `app/config.py` (mencionado en el código) se define, entre otras cosas, la lista de **emojis permitidos** (`ALLOWED_EMOJIS`), que incluye 16 emojis:

> 👍 ❤️ 😂 🎉 🚀 👏 🔥 💯 👎 😮 😢 😡 🤔 💡 ✅ ❌

Esta lista se usa en:

- La descripción de la herramienta MCP `add-reaction` en `main.py`.
- La validación de Pydantic (`schemas.AddReactionInput`).

Así evitamos que se guarden reacciones con emojis arbitrarios.

---

## 8. Servidor MCP (`app/main.py`)

Este archivo es el **corazón MCP** del proyecto. Veamos sus partes principales.

### 8.1. Creación del servidor MCP

```python
from mcp.server import Server

app = Server("python-mcp-chat")
```

Con esto se crea una instancia de servidor MCP llamada `python-mcp-chat`. Esta instancia tendrá:

- Un listado de herramientas (`@app.list_tools()`)
- Un manejador para ejecutar herramientas (`@app.call_tool()`)

### 8.2. Definición de herramientas MCP

La función decorada con `@app.list_tools()` devuelve la lista de herramientas disponibles:

- `send-message`
- `get-messages`
- `reply-to-message`
- `get-message-thread`
- `get-channels`
- `get-channel-messages`
- `add-reaction`
- `remove-reaction`
- `get-message-reactions`
- `get-users-list`
- `search-messages`
- `get-messages-by-user`
- `get-messages-by-date-range`

Cada herramienta se define como un objeto `Tool` con:

- `name`: nombre de la herramienta MCP.
- `description`: descripción legible para humanos.
- `inputSchema`: esquema JSON derivado de un modelo Pydantic (`.model_json_schema()`).

Esto permite que el cliente MCP (por ejemplo, Claude Desktop) entienda cómo llamar correctamente a cada herramienta.

### 8.3. Ejecución de herramientas (`call_tool`)

La función `@app.call_tool()` es llamada cuando el modelo invoca una herramienta. Su estructura general es:

1. Crea una sesión de base de datos: `db = SessionLocal()`.
2. Según el `name` de la herramienta, valida `arguments` con el esquema Pydantic correspondiente.
3. Llama a la función adecuada de `crud.py`.
4. Devuelve un `TextContent` con un mensaje formateado (tipo texto) para el modelo.
5. Cierra la sesión en un `finally`.

Ejemplo simplificado para `send-message`:

```python
if name == "send-message":
    data = schemas.SendMessageInput(**arguments)
    msg_id = crud.send_message(db, data.name, data.content, data.channel)
    return [TextContent(
        type="text",
        text=f"✅ Message {msg_id} sent to #{data.channel} by {data.name}"
    )]
```

Fíjate cómo se combinan:

- **Pydantic** → valida `arguments`.
- **CRUD** → hace la operación real en la BD.
- **MCP** → empaqueta la respuesta para que el modelo la vea de forma amigable.

### 8.4. Manejo de errores

En `call_tool` se capturan errores típicos:

- `ValueError`: normalmente derivado de validaciones de negocio (por ejemplo, mensaje no encontrado).
- `Exception`: cualquier otro error inesperado.

Se devuelve siempre un `TextContent` con un mensaje de error legible:

```python
except ValueError as e:
    return [TextContent(type="text", text=f"❌ Validation error: {str(e)}")]
except Exception as e:
    return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
```

### 8.5. Función `main()` y stdio

La función `main()` hace varias cosas:

1. Llama a `init_db()` para asegurarse de que la base de datos y las tablas existen.
2. Opcionalmente arranca el servidor FastAPI (`app.api:api`) con Uvicorn **en segundo plano**, si está definida la variable de entorno `MCP_HTTP_PORT`.
3. Inicia el servidor MCP sobre stdio:

```python
async with stdio_server() as (read_stream, write_stream):
    await app.run(
        read_stream,
        write_stream,
        app.create_initialization_options()
    )
```

Esto significa que el servidor MCP se comunica con el cliente (Claude, etc.) por **entrada estándar/salida estándar**. Es la forma usual en que Claude Desktop lanza servidores MCP.

Cuando ejecutas:

```bash
python -m app.main
```

se arranca este bucle asincrónico MCP.

---

## 9. API REST opcional (`app/api.py`)

Además del servidor MCP, la aplicación ofrece una **API REST** con FastAPI. Esto es útil para:

- Probar la lógica de negocio con herramientas como `curl` o Postman.
- Integrar el chat con otras aplicaciones que hablen HTTP.

### 9.1. Creación de la app FastAPI

```python
from fastapi import FastAPI

api = FastAPI(
    title="Python MCP Chat API",
    description="REST API for Python MCP Chat",
    version="1.0.0"
)
```

### 9.2. Dependencia de base de datos

Las rutas usan `Depends(get_db)` (definido en `app.database`) para obtener una sesión SQLAlchemy por petición y cerrarla adecuadamente.

### 9.3. Endpoints principales

Los endpoints cubren prácticamente las mismas funciones que las herramientas MCP:

- `GET /` → estado de la API.
- `GET /messages` → listar mensajes recientes.
- `POST /messages` → crear mensaje.
- `GET /messages/{message_id}` → obtener un mensaje concreto.
- `GET /messages/{message_id}/thread` → obtener el thread completo.
- `POST /messages/{message_id}/replies` → crear respuesta.
- `GET /channels` → listar canales.
- `GET /channels/{channel}/messages` → mensajes de un canal.
- `POST /messages/{message_id}/reactions` → añadir reacción.
- `DELETE /messages/{message_id}/reactions` → quitar reacción.
- `GET /messages/{message_id}/reactions` → ver reacciones.
- `GET /users` → listar usuarios.
- `GET /search` → buscar mensajes por texto.
- `GET /users/{name}/messages` → mensajes de un usuario.
- `GET /messages/date-range` → mensajes por rango de fechas.

Cada endpoint:

- Recibe datos validados por Pydantic (a través de `schemas.*`).
- Llama a funciones de `crud.py`.
- Devuelve diccionarios (o listas de diccionarios) que FastAPI convierte a JSON.
- Lanza `HTTPException` si hay errores (ej. mensaje no encontrado).

### 9.4. Ejecución de la API

Para arrancar la API REST en desarrollo:

```bash
uvicorn app.api:api --reload
```

Y luego visitar `http://localhost:8000/docs` para ver la documentación interactiva generada automáticamente por FastAPI (Swagger UI).

---

## 10. Inicialización y datos de ejemplo (`seed.py`)

El script `seed.py` se usa para:

- Crear la base de datos y tablas (si no existen).
- Insertar datos de ejemplo (usuarios, mensajes, reacciones, canales).

Esto te permite tener un entorno de prueba listo para explorar las herramientas sin tener que crear todo manualmente.

Se ejecuta con:

```bash
python seed.py
```

---

## 11. ¿Cómo se usa desde Claude / un cliente MCP?

1. Configuras Claude Desktop (u otro cliente MCP) para que lance el comando:

   ```json
   {
     "mcpServers": {
       "python-mcp-chat": {
         "command": "python",
         "args": ["-m", "app.main"],
         "cwd": "/ruta/completa/a/python-mcp-chat"
       }
     }
   }
   ```

2. Cuando el modelo necesita interactuar con el chat (por ejemplo: "muéstrame los últimos mensajes"), el cliente MCP:
   - Llama a `list_tools` para saber qué herramientas hay.
   - Llama a `call_tool` con el `name` adecuado y los `arguments` correctos.

3. El servidor MCP:
   - Valida los argumentos con Pydantic.
   - Ejecuta la operación en la base de datos vía `crud.py`.
   - Devuelve una respuesta textual estructurada al modelo.

Así, el modelo puede:

- Leer mensajes recientes.
- Escribir nuevos mensajes.
- Responder creando threads.
- Añadir o quitar reacciones.
- Buscar por contenido, usuario o fecha.
- Consultar estadísticas de canales y usuarios.

---

## 12. Resumen conceptual (como profesor)

Si tuviera que resumirte esta aplicación en pocas ideas clave:

1. **Dominio**: es un **chat con threads, canales y reacciones**.
2. **Persistencia**: usa **SQLAlchemy + SQLite** para guardar todo de forma relacional y consistente.
3. **Validación**: confía en **Pydantic** para asegurar que los datos entrantes son correctos (longitudes, rangos, emojis permitidos...).
4. **Capa de negocio**: `crud.py` implementa las operaciones de alto nivel sobre el chat, optimizadas con buenas consultas SQL.
5. **Interfaces de acceso**:
   - **MCP** (`main.py`): pensada para que **modelos de IA** utilicen el chat como herramienta.
   - **API REST** (`api.py`): pensada para humanos/desarrolladores o integraciones HTTP.
6. **Extensibilidad**: al estar todo bien separado (modelos, crud, esquemas, API, MCP), es fácil:
   - Añadir nuevas herramientas MCP.
   - Crear nuevos endpoints REST.
   - Cambiar la base de datos por otra (PostgreSQL, MySQL) con pocos cambios.

Como alumno, te recomiendo que explores el código siguiendo este orden:

1. `app/models.py` → para entender el modelo de datos.
2. `app/crud.py` → para ver cómo se consulta y modifica la base de datos.
3. `app/schemas.py` → para entender qué datos esperan las herramientas.
4. `app/main.py` → para ver cómo se exponen estas operaciones como herramientas MCP.
5. `app/api.py` → para ver el paralelismo con una API REST clásica.

Si quieres, en un siguiente paso puedo hacer un recorrido más "línea a línea" por alguno de estos archivos (por ejemplo `main.py` o `models.py`) y explicarte cada instrucción con más detalle.
