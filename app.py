import os
import uuid
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AGENT_ID = os.getenv("BEDROCK_AGENT_ID")
ALIAS_ID = os.getenv("BEDROCK_AGENT_ALIAS_ID")
AWS_PROFILE = os.getenv("AWS_PROFILE")
# Agregar credenciales de AWS desde .env
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

if not AGENT_ID or not ALIAS_ID:
    raise RuntimeError("Missing BEDROCK_AGENT_ID or BEDROCK_AGENT_ALIAS_ID in .env")

# Configurar cliente de boto3 con credenciales del .env si están disponibles
if AWS_ACCESS_KEY and AWS_SECRET_KEY:
    # Usar credenciales explícitas del .env
    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        config=Config(retries={"max_attempts": 8})
    )
    print(f"Usando credenciales explícitas para región {AWS_REGION}")
elif AWS_PROFILE:
    # Usar perfil configurado
    boto3.setup_default_session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=AWS_REGION,
        config=Config(retries={"max_attempts": 8})
    )
else:
    # Usar configuración por defecto
    client = boto3.client(
        "bedrock-agent-runtime",
        region_name=AWS_REGION,
        config=Config(retries={"max_attempts": 8})
    )

app = FastAPI(title="Local Bedrock Agent Chat")

# (Opcional) carpeta para datos simples
DATA_DIR = Path("./conversations")
DATA_DIR.mkdir(exist_ok=True)

def invoke_agent_no_streaming(text: str, session_id: str) -> str:
    """
    Llama al agente en modo no-streaming (más simple).
    """
    try:
        resp = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            sessionId=session_id,
            inputText=text,
            enableTrace=False,  # pon True si quieres depuración/trace
        )
        
        # Procesar la respuesta según su estructura
        if "output" in resp:
            # Formato de respuesta no streaming
            return resp["output"]
        elif "completion" in resp:
            # Formato de respuesta streaming (EventStream)
            completion = ""
            for event in resp.get("completion"):
                if "chunk" in event:
                    chunk = event["chunk"]
                    completion += chunk["bytes"].decode()
            return completion.strip()
        else:
            # Formato desconocido, intentar imprimir para depuración
            print(f"Formato de respuesta desconocido: {resp}")
            return "[No se pudo procesar la respuesta del agente]"
            
    except Exception as e:
        print(f"Error al invocar agente: {e}")
        raise e

@app.post("/api/message")
async def api_message(payload: dict):
    message: str = (payload.get("message") or "").strip()
    session_id: Optional[str] = payload.get("sessionId")
    if not message:
        return JSONResponse({"error": "message is required"}, status_code=400)
    if not session_id:
        session_id = str(uuid.uuid4())

    # Guarda historial simple en disco (opcional)
    log = DATA_DIR / f"{session_id}.jsonl"
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"role":"user","text":message}, ensure_ascii=False) + "\n")

    try:
        reply = invoke_agent_no_streaming(message, session_id)
        
        # Si la respuesta está vacía, proporcionar un mensaje más claro
        if not reply:
            reply = "[El agente no proporcionó una respuesta. Verifica la configuración del agente en AWS Bedrock.]"
    except Exception as e:
        reply = f"[error] {str(e)}"
        print(f"Error al procesar mensaje: {e}")

    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"role":"agent","text":reply}, ensure_ascii=False) + "\n")

    return JSONResponse({"sessionId": session_id, "reply": reply})

@app.get("/", response_class=HTMLResponse)
def index():
    # HTML sencillo embebido (sin plantillas)
    return HTMLResponse("""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Bedrock Agent · Local Chat</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial; margin: 0; background: #0d1117; color: #c9d1d9;}
    header { padding: 16px; background: #161b22; border-bottom: 1px solid #30363d; }
    main { display: flex; flex-direction: column; height: calc(100vh - 64px); }
    #chat { flex: 1; overflow-y: auto; padding: 16px; }
    .msg { max-width: 860px; margin: 0 auto 12px; padding: 12px 14px; border-radius: 10px; white-space: pre-wrap; line-height: 1.45; }
    .user { background: #1f6feb22; border: 1px solid #1f6feb55; }
    .agent { background: #161b22; border: 1px solid #30363d; }
    form { display: flex; gap: 8px; padding: 12px; border-top: 1px solid #30363d; background: #0d1117; }
    textarea { flex: 1; resize: none; height: 60px; background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px; padding: 10px; }
    button { background: #238636; color: white; border: 0; border-radius: 8px; padding: 10px 16px; cursor: pointer; }
    .meta { max-width: 860px; margin: 8px auto; color: #8b949e; font-size: 12px; }
    .meta span { margin-right: 12px; }
    .toolbar { max-width: 860px; margin: 8px auto 0; display: flex; gap: 8px; align-items: center; }
    .toolbar button { background: #30363d; color: #c9d1d9; }
    .toolbar input { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 6px 8px; width: 340px; }
  </style>
</head>
<body>
  <header>
    <strong>DaCodes · Bedrock Web Proposal Agent (Local)</strong>
  </header>
  <main>
    <div class="toolbar">
      <button id="new">Nueva sesión</button>
      <input id="sid" placeholder="sessionId" />
      <button id="copy">Copiar</button>
    </div>
    <div class="meta" id="meta"></div>
    <div id="chat"></div>
    <form id="form">
      <textarea id="input" placeholder="Escribe tu mensaje..."></textarea>
      <button type="submit">Enviar</button>
    </form>
  </main>
<script>
const chat = document.getElementById('chat');
const form = document.getElementById('form');
const input = document.getElementById('input');
const sidIn = document.getElementById('sid');
const meta = document.getElementById('meta');
const btnNew = document.getElementById('new');
const btnCopy = document.getElementById('copy');

function ensureSession() {
  let sid = localStorage.getItem('sessionId');
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem('sessionId', sid);
  }
  sidIn.value = sid;
  meta.textContent = `sessionId: ${sid}`;
}
ensureSession();

btnNew.addEventListener('click', () => {
  const sid = crypto.randomUUID();
  localStorage.setItem('sessionId', sid);
  sidIn.value = sid;
  meta.textContent = `sessionId: ${sid}`;
  chat.innerHTML = '';
});

btnCopy.addEventListener('click', async () => {
  const sid = sidIn.value.trim();
  if (sid) {
    await navigator.clipboard.writeText(sid);
    alert('sessionId copiado');
  }
});

sidIn.addEventListener('change', () => {
  const sid = sidIn.value.trim();
  if (sid) {
    localStorage.setItem('sessionId', sid);
    meta.textContent = `sessionId: ${sid}`;
  }
});

function append(role, text) {
  const div = document.createElement('div');
  div.className = 'msg ' + (role === 'user' ? 'user' : 'agent');
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  const sid = localStorage.getItem('sessionId');
  append('user', text);
  input.value = '';
  try {
    const res = await fetch('/api/message', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ message: text, sessionId: sid })
    });
    const data = await res.json();
    append('agent', data.reply || '[sin respuesta]');
  } catch (err) {
    append('agent', '[error] ' + err);
  }
});
</script>
</body>
</html>
    """)
