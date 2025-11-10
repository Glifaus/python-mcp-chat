# Python MCP Chat

Implementación profesional de un servidor MCP (Model Context Protocol) Chat en Python usando FastAPI y SQLAlchemy, basado en [laravel-mcp-chat](https://github.com/Glifaus/laravel-mcp-chat).

## 🚀 Características

- **14 herramientas MCP** completas para chat
- **SQLAlchemy 2.0** con relaciones y cascadas
- **FastAPI** para API REST opcional
- **Pydantic v2** para validación de datos
- **Threads de mensajes** con respuestas anidadas
- **Reacciones con emojis** (16 emojis permitidos)
- **Múltiples canales** (#general, #python, #jobs, etc.)
- **Búsqueda avanzada** por contenido, usuario y fechas
- **Estadísticas** de usuarios y canales

## 📋 Stack Tecnológico

- **Python 3.10+**
- **FastAPI** - Framework web moderno
- **SQLAlchemy 2.0+** - ORM con relaciones
- **Pydantic v2** - Validación de datos
- **mcp library** - Servidor MCP
- **SQLite** - Base de datos

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Glifaus/python-mcp-chat.git
cd python-mcp-chat
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Inicializar base de datos con datos de ejemplo

```bash
python seed.py
```

## 🎯 Uso

### Servidor MCP (para Claude Desktop)

```bash
python -m app.main
```

### API REST opcional (para desarrollo)

```bash
uvicorn app.api:api --reload
```

Acceder a la documentación interactiva: http://localhost:8000/docs

## 🔧 Configuración para Claude Desktop

Editar el archivo de configuración de Claude Desktop y agregar:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

**Importante**: Reemplazar `/ruta/completa/a/python-mcp-chat` con la ruta absoluta a tu proyecto.

## 🛠️ Las 14 Herramientas MCP

| # | Herramienta | Descripción | Parámetros |
|---|-------------|-------------|------------|
| 1 | `send-message` | Enviar mensaje a un canal | `name`, `content`, `channel` |
| 2 | `get-messages` | Obtener mensajes recientes | `limit` (1-100) |
| 3 | `reply-to-message` | Responder a un mensaje (thread) | `parent_message_id`, `name`, `content` |
| 4 | `get-message-thread` | Ver thread completo con respuestas | `message_id` |
| 5 | `get-channels` | Listar canales con estadísticas | - |
| 6 | `get-channel-messages` | Mensajes de un canal específico | `channel`, `limit` |
| 7 | `add-reaction` | Añadir emoji a un mensaje | `message_id`, `user_name`, `emoji` |
| 8 | `remove-reaction` | Quitar emoji de un mensaje | `message_id`, `user_name`, `emoji` |
| 9 | `get-message-reactions` | Ver reacciones agrupadas por emoji | `message_id` |
| 10 | `get-users-list` | Listar usuarios con estadísticas | `limit`, `sort_by` |
| 11 | `search-messages` | Buscar mensajes por contenido | `query`, `limit` |
| 12 | `get-messages-by-user` | Filtrar mensajes por autor | `name`, `limit` |
| 13 | `get-messages-by-date-range` | Filtrar mensajes por fechas | `start_date`, `end_date`, `limit` |

### Emojis Permitidos (16)

👍 ❤️ 😂 🎉 🚀 👏 🔥 💯 👎 😮 😢 😡 🤔 💡 ✅ ❌

## 📝 Ejemplos de Uso

### 1. Enviar mensaje

```json
{
  "name": "send-message",
  "arguments": {
    "name": "Alice",
    "content": "¡Hola mundo!",
    "channel": "general"
  }
}
```

### 2. Obtener mensajes recientes

```json
{
  "name": "get-messages",
  "arguments": {
    "limit": 20
  }
}
```

### 3. Responder a un mensaje

```json
{
  "name": "reply-to-message",
  "arguments": {
    "parent_message_id": 1,
    "name": "Bob",
    "content": "¡Hola Alice!"
  }
}
```

### 4. Añadir reacción

```json
{
  "name": "add-reaction",
  "arguments": {
    "message_id": 1,
    "user_name": "Charlie",
    "emoji": "👍"
  }
}
```

### 5. Buscar mensajes

```json
{
  "name": "search-messages",
  "arguments": {
    "query": "Python",
    "limit": 50
  }
}
```

### 6. Listar usuarios por actividad

```json
{
  "name": "get-users-list",
  "arguments": {
    "limit": 10,
    "sort_by": "last_activity"
  }
}
```

### 7. Filtrar por rango de fechas

```json
{
  "name": "get-messages-by-date-range",
  "arguments": {
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-12-31T23:59:59",
    "limit": 100
  }
}
```

## 🗄️ Estructura de la Base de Datos

### Tabla: messages

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Primary key |
| parent_id | INTEGER | FK a messages.id (nullable) |
| name | VARCHAR(50) | Nombre del usuario |
| content | VARCHAR(500) | Contenido del mensaje |
| channel | VARCHAR(50) | Canal del mensaje |
| created_at | DATETIME | Fecha de creación |
| updated_at | DATETIME | Fecha de actualización |

**Índices**: `channel`, `parent_id`, `created_at`

### Tabla: reactions

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | Primary key |
| message_id | INTEGER | FK a messages.id |
| user_name | VARCHAR(50) | Nombre del usuario |
| emoji | VARCHAR(10) | Emoji de reacción |
| created_at | DATETIME | Fecha de creación |
| updated_at | DATETIME | Fecha de actualización |

**Constraint único**: `(message_id, user_name, emoji)`  
**Índice**: `message_id`

### Relaciones

- `Message.parent` → Mensaje padre (self-referential)
- `Message.replies` → Lista de respuestas (cascade delete)
- `Message.reactions` → Lista de reacciones (cascade delete)
- `Reaction.message` → Mensaje asociado

## 🏗️ Arquitectura del Proyecto

```
python-mcp-chat/
├── app/
│   ├── __init__.py          # Metadata del paquete
│   ├── main.py              # Servidor MCP con 14 herramientas
│   ├── api.py               # API REST con FastAPI (opcional)
│   ├── database.py          # Configuración SQLAlchemy
│   ├── models.py            # Modelos Message y Reaction
│   ├── schemas.py           # Schemas Pydantic para validación
│   ├── crud.py              # Operaciones CRUD optimizadas
│   └── config.py            # Configuración y constantes
├── requirements.txt         # Dependencias Python
├── seed.py                  # Script para poblar BD
├── README.md                # Este archivo
├── .mcp.json                # Configuración MCP
└── .gitignore               # Archivos ignorados por Git
```

## 🔍 Validaciones

### Límites de Campos

- **name**: 1-50 caracteres
- **content**: 1-500 caracteres
- **channel**: máximo 50 caracteres
- **query** (búsqueda): 1-200 caracteres
- **limit**: 1-100 (default: 50)

### Reglas de Negocio

- Los mensajes principales tienen `parent_id = NULL`
- Las respuestas heredan el `channel` del mensaje padre
- Las reacciones son únicas por `(message_id, user_name, emoji)`
- Solo se permiten los 16 emojis definidos en `ALLOWED_EMOJIS`
- Las búsquedas son case-insensitive
- El cascade delete elimina respuestas y reacciones al borrar un mensaje

## 📊 Queries Optimizadas

El módulo `crud.py` utiliza:

- **Subqueries** para contar replies y reactions eficientemente
- **GROUP BY** para estadísticas de canales y usuarios
- **Índices** en campos frecuentemente consultados
- **SQLAlchemy 2.0 style** con `select()` y `Mapped` types
- **Eager loading** para reducir queries N+1

## 🆚 Diferencias con laravel-mcp-chat

| Aspecto | Laravel MCP Chat | Python MCP Chat |
|---------|------------------|-----------------|
| Lenguaje | PHP 8.2+ | Python 3.10+ |
| Framework Web | Laravel 11 | FastAPI |
| ORM | Eloquent | SQLAlchemy 2.0 |
| Validación | Form Requests | Pydantic v2 |
| Async | No nativo | Nativo (asyncio) |
| Migraciones | Artisan migrations | SQLAlchemy Base.metadata |
| Testing | PHPUnit | pytest (recomendado) |

### Funcionalidad Idéntica

✅ Las 14 herramientas MCP  
✅ Mismo modelo de datos (Message + Reaction)  
✅ Mismas validaciones y límites  
✅ Mismo comportamiento de threads y reacciones  
✅ Mismos emojis permitidos  

## 🧪 Testing (Opcional)

Para agregar tests con pytest:

```bash
pip install pytest pytest-asyncio
```

Crear `tests/test_crud.py`:

```python
from app.database import SessionLocal, init_db
from app import crud

def test_send_message():
    init_db()
    db = SessionLocal()
    msg_id = crud.send_message(db, "Test", "Hello", "general")
    assert msg_id > 0
    db.close()
```

Ejecutar tests:

```bash
pytest
```

## 📄 API REST Endpoints (Opcional)

Si ejecutas `uvicorn app.api:api --reload`:

- `GET /` - Estado de la API
- `GET /messages` - Listar mensajes
- `POST /messages` - Crear mensaje
- `GET /messages/{id}` - Obtener mensaje
- `GET /messages/{id}/thread` - Ver thread
- `POST /messages/{id}/replies` - Crear respuesta
- `GET /channels` - Listar canales
- `GET /channels/{channel}/messages` - Mensajes de canal
- `POST /messages/{id}/reactions` - Añadir reacción
- `DELETE /messages/{id}/reactions` - Quitar reacción
- `GET /messages/{id}/reactions` - Ver reacciones
- `GET /users` - Listar usuarios
- `GET /search` - Buscar mensajes
- `GET /users/{name}/messages` - Mensajes por usuario
- `GET /messages/date-range` - Mensajes por fechas

Documentación interactiva: http://localhost:8000/docs

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📜 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

## 🔗 Referencias

- Proyecto base: [laravel-mcp-chat](https://github.com/Glifaus/laravel-mcp-chat)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 👥 Autor

Glifaus - [GitHub](https://github.com/Glifaus)

---

**¡Disfruta usando Python MCP Chat! 🚀**
