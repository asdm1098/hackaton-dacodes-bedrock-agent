# 🟢 DaCodes · Bedrock Web Proposal Agent (MVP)

Este proyecto implementa un chat web local en FastAPI para interactuar con un Amazon Bedrock Agent.
Permite conversar con el agente, generar propuestas y (opcionalmente) exportarlas como PDF en un bucket Amazon S3.

Diseñado como MVP demostrativo para el hackatón.

## 🚀 Tecnologías usadas

### Amazon Bedrock
- Bedrock Agents (para lógica de propuestas y flujos de conversación).
- bedrock-agent-runtime (para invocación desde Python).

### Amazon S3
- Almacenamiento de propuestas exportadas en PDF.
- Bucket con política pública para generar URLs cortas.

### AWS Lambda (Action Group)
- Función encargada de convertir Markdown a PDF y subirlo a S3.

### FastAPI + Uvicorn
- Servidor backend ligero para el chat y API.

### Python 3.11+
- dotenv (manejo de variables de entorno).
- boto3 (SDK AWS).

## 📂 Estructura del proyectobedrock_agent/
├─ app.py              # Servidor FastAPI (chat UI + API REST)
├─ requirements.txt    # Dependencias
├─ .env                # Variables de entorno (NO commitear)
├─ conversations/      # Historial JSONL por sesión
└─ README.md


## ⚙️ Configuración

### Clonar el repositorio
git clone
cd bedrock_agent


### Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
### Instalar dependencias
pip install -r requirements.txt


### Configurar .env
Renombrar el archivo `.env.example` a `.env`
AWS_ACCESS_KEY_ID=  "enviadas por correo"
AWS_SECRET_ACCESS_KEY=4 "enviadas por correo"

## 🔑 Acceso para Revisores (Hackathon)

**Importante**: Este proyecto utiliza un agente Bedrock configurado específicamente para la hackathon.

Para revisores del proyecto:
1. Use las credenciales proporcionadas en `.env.example`
2. Estas credenciales tienen acceso controlado al agente Bedrock con ID: `BHQCYAZXTB`
3. Las credenciales son temporales y solo funcionarán durante el período de evaluación
4. No se requiere configuración adicional de permisos entre cuentas

## ▶️ Ejecución
### Iniciar el servidor
uvicorn app:app --reload --port 8000

### Abrir en el navegador
http://127.0.0.1:8000/


### Probar el chat
- Escribir un mensaje → el agente responde usando Amazon Bedrock.
- Los mensajes se guardan en ./conversations/<sessionId>.jsonl.

### Probar vía API
curl -X POST http://127.0.0.1:8000/api/message -H "Content-Type: application/json" -d '{"message":"Crear presupuesto e-commerce","sessionId":"demo-1"}'


## 📑 Exportar PDF (opcional)

El agente incluye un Action Group conectado a una AWS Lambda (export_proposal_pdf).

Esta Lambda:
- Convierte el Markdown de la propuesta a PDF.
- Sube el archivo al bucket Amazon S3 (proposals/generated/...).
- Devuelve un URL público corto si el bucket está configurado con Bucket Policy pública.