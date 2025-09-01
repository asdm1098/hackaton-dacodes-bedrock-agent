# 🟢 DaCodes · Bedrock Web Proposal Agent (MVP)

Este proyecto implementa un chat web local en FastAPI para interactuar con un Amazon Bedrock Agent.
Permite conversar con el agente, generar propuestas y (opcionalmente) exportarlas como PDF en un bucket Amazon S3.

Diseñado como MVP demostrativo para el hackatón.

## 📋 Índice
- [🚀 Tecnologías](#-tecnologías)
- [📂 Estructura del proyecto](#-estructura-del-proyecto)
- [⚙️ Configuración](#️-configuración)
- [🔑 Credenciales para Revisores](#-credenciales-para-revisores)
- [▶️ Ejecución](#️-ejecución)
- [📑 Exportar PDF](#-exportar-pdf-opcional)

## 🚀 Tecnologías

### Amazon Bedrock
- **Bedrock Agents**: Para lógica de propuestas y flujos de conversación.
- **bedrock-agent-runtime**: Para invocación desde Python.

### Amazon S3
- Almacenamiento de propuestas exportadas en PDF.
- Bucket con política pública para generar URLs cortas.

### AWS Lambda (Action Group)
- Función encargada de convertir Markdown a PDF y subirlo a S3.

### FastAPI + Uvicorn
- Servidor backend ligero para el chat y API.

### Python 3.11+
- **dotenv**: Manejo de variables de entorno.
- **boto3**: SDK AWS.

## 📂 Estructura del proyectobedrock_agent/
├─ app.py              # Servidor FastAPI (chat UI + API REST)
├─ requirements.txt    # Dependencias
├─ .env                # Variables de entorno (NO commitear)
├─ conversations/      # Historial JSONL por sesión
└─ README.md


## ⚙️ Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/asdm1098/hackaton-dacodes-bedrock-agent.git
cd hackaton-dacodes-bedrock-agent
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar .env
Renombrar el archivo `.env.example` a `.env` y configurar con las credenciales proporcionadas.

## 🔑 Credenciales para Revisores

**Importante**: Este proyecto utiliza un agente Bedrock configurado específicamente para la hackathon.

Para revisores del proyecto:
1. Las credenciales de AWS han sido enviadas por correo
2. Estas credenciales tienen acceso controlado al agente Bedrock con ID: `BHQCYAZXTB`
3. Las credenciales son temporales y solo funcionarán durante el período de evaluación
4. No se requiere configuración adicional de permisos entre cuentas

## ▶️ Ejecución

### 1. Iniciar el servidor
```bash
uvicorn app:app --reload --port 8000
```

### 2. Abrir en el navegador
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 3. Probar el chat
- Escribir un mensaje → el agente responde usando Amazon Bedrock.
- Los mensajes se guardan en `./conversations/<sessionId>.jsonl`.

### 4. Probar vía API
```bash
curl -X POST http://127.0.0.1:8000/api/message -H "Content-Type: application/json" -d '{"message":"Crear presupuesto e-commerce","sessionId":"demo-1"}'
```

## 📑 Exportar PDF (opcional)

El agente incluye un Action Group conectado a una AWS Lambda (`export_proposal_pdf`).

Esta Lambda:
- Convierte el Markdown de la propuesta a PDF.
- Sube el archivo al bucket Amazon S3 (`proposals/generated/...`).
- Devuelve un URL público corto si el bucket está configurado con Bucket Policy pública.
