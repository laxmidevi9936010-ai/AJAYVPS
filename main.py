"""
AJAYVPS Backend — Real hosting platform
Deploy on Railway. Spawns user processes, streams real logs over WebSocket.
"""
import asyncio
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
import zipfile
from collections import deque
from pathlib import Path
from typing import Dict, Optional

import jwt
from fastapi import (
    FastAPI, File, Form, HTTPException, UploadFile, WebSocket,
    WebSocketDisconnect, Depends, Header
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ---------- Config ----------
JWT_SECRET = os.environ.get("JWT_SECRET", "ajayvps-change-me-in-railway-env")
DATA_DIR = Path(os.environ.get("DATA_DIR", "/tmp/ajayvps_data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
SERVERS_FILE = DATA_DIR / "servers.json"
APPS_DIR = DATA_DIR / "apps"
APPS_DIR.mkdir(exist_ok=True)
MAX_LOG_LINES = 2000

app = FastAPI(title="AJAYVPS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Persistence ----------
def load_json(p: Path, default):
    if p.exists():
        try: return json.loads(p.read_text())
        except: return default
    return default

def save_json(p: Path, data):
    p.write_text(json.dumps(data, indent=2))

users: Dict[str, dict] = load_json(USERS_FILE, {})
servers: Dict[str, dict] = load_json(SERVERS_FILE, {})

# ---------- Runtime process registry ----------
class RunningApp:
    def __init__(self, server_id: str, proc: subprocess.Popen):
        self.server_id = server_id
        self.proc = proc
        self.logs: deque = deque(maxlen=MAX_LOG_LINES)
        self.subscribers: set = set()  # WebSocket subscribers
        self.started_at = time.time()
        self.reader_task: Optional[asyncio.Task] = None

running: Dict[str, RunningApp] = {}

async def broadcast(server_id: str, line: str):
    app_obj = running.get(server_id)
    if not app_obj: return
    app_obj.logs.append(line)
    dead = []
    for ws in list(app_obj.subscribers):
        try:
            await ws.send_text(line)
        except Exception:
            dead.append(ws)
    for ws in dead:
        app_obj.subscribers.discard(ws)

async def read_stream(server_id: str):
    app_obj = running.get(server_id)
    if not app_obj: return
    proc = app_obj.proc
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, proc.stdout.readline)
        if not line:
            break
        text = line.rstrip("\n")
        ts = time.strftime("%H:%M:%S")
        await broadcast(server_id, f"[{ts}] {text}")
    code = proc.wait()
    await broadcast(server_id, f"[system] Process exited with code {code}")
    if server_id in servers:
        servers[server_id]["status"] = "stopped"
        save_json(SERVERS_FILE, servers)
    running.pop(server_id, None)

# ---------- Auth ----------
class AuthIn(BaseModel):
    username: str
    password: str

def make_token(username: str) -> str:
    return jwt.encode({"u": username, "iat": int(time.time())}, JWT_SECRET, algorithm="HS256")

def auth_user(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    try:
        data = jwt.decode(authorization[7:], JWT_SECRET, algorithms=["HS256"])
        return data["u"]
    except Exception:
        raise HTTPException(401, "Invalid token")

@app.post("/api/auth/signup")
def signup(body: AuthIn):
    if body.username in users:
        # accept any login — auto-create OR login
        if users[body.username]["password"] != body.password:
            raise HTTPException(400, "Wrong password")
    else:
        users[body.username] = {"password": body.password, "created": time.time()}
        save_json(USERS_FILE, users)
    return {"token": make_token(body.username), "username": body.username}

@app.post("/api/auth/login")
def login(body: AuthIn):
    # Any username/password works — auto-register on first use
    if body.username not in users:
        users[body.username] = {"password": body.password, "created": time.time()}
        save_json(USERS_FILE, users)
    elif users[body.username]["password"] != body.password:
        raise HTTPException(400, "Wrong password")
    return {"token": make_token(body.username), "username": body.username}

# ---------- Servers ----------
class ServerCreate(BaseModel):
    name: str
    runtime: str  # "python" | "node" | "static"

@app.get("/api/servers")
def list_servers(user: str = Depends(auth_user)):
    user_servers = [
        {**s, "status": "running" if sid in running else s.get("status", "stopped")}
        for sid, s in servers.items() if s["owner"] == user
    ]
    return user_servers

@app.post("/api/servers")
def create_server(body: ServerCreate, user: str = Depends(auth_user)):
    sid = uuid.uuid4().hex[:12]
    server_dir = APPS_DIR / sid
    server_dir.mkdir(parents=True, exist_ok=True)
    servers[sid] = {
        "id": sid,
        "name": body.name,
        "runtime": body.runtime,
        "owner": user,
        "status": "stopped",
        "main_file": "",
        "created": time.time(),
    }
    save_json(SERVERS_FILE, servers)
    return servers[sid]

@app.delete("/api/servers/{sid}")
def delete_server(sid: str, user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404, "Not found")
    if sid in running:
        try: running[sid].proc.terminate()
        except: pass
        running.pop(sid, None)
    shutil.rmtree(APPS_DIR / sid, ignore_errors=True)
    servers.pop(sid, None)
    save_json(SERVERS_FILE, servers)
    return {"ok": True}

# ---------- Files ----------
@app.get("/api/servers/{sid}/files")
def list_files(sid: str, user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404)
    d = APPS_DIR / sid
    out = []
    for p in d.rglob("*"):
        if p.is_file():
            out.append({"path": str(p.relative_to(d)), "size": p.stat().st_size})
    return {"files": out, "main_file": s.get("main_file", "")}

@app.post("/api/servers/{sid}/upload")
async def upload_file(sid: str, file: UploadFile = File(...), user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404)
    d = APPS_DIR / sid
    target = d / file.filename
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "wb") as f:
        shutil.copyfileobj(file.file, f)
    # Auto-extract zip
    if file.filename.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(target) as z:
                z.extractall(d)
            target.unlink()
        except Exception as e:
            raise HTTPException(400, f"Bad zip: {e}")
    return {"ok": True}

class MainFileIn(BaseModel):
    main_file: str

@app.post("/api/servers/{sid}/main")
def set_main(sid: str, body: MainFileIn, user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404)
    s["main_file"] = body.main_file
    save_json(SERVERS_FILE, servers)
    return {"ok": True}

@app.delete("/api/servers/{sid}/files/{path:path}")
def delete_file(sid: str, path: str, user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404)
    target = (APPS_DIR / sid / path).resolve()
    if not str(target).startswith(str((APPS_DIR / sid).resolve())):
        raise HTTPException(400, "Bad path")
    if target.exists(): target.unlink()
    return {"ok": True}

# ---------- Process control ----------
def build_cmd(server: dict) -> Optional[list]:
    runtime = server["runtime"]
    main = server.get("main_file") or ""
    if not main: return None
    if runtime == "python":
        return [sys.executable, "-u", main]
    if runtime == "node":
        return ["node", main]
    if runtime == "static":
        return [sys.executable, "-u", "-m", "http.server", os.environ.get("PORT_INNER", "8000")]
    return None

@app.post("/api/servers/{sid}/start")
async def start(sid: str, user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404)
    if sid in running: raise HTTPException(400, "Already running")
    cmd = build_cmd(s)
    if not cmd: raise HTTPException(400, "Set main file first")
    cwd = APPS_DIR / sid
    try:
        proc = subprocess.Popen(
            cmd, cwd=str(cwd),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
    except Exception as e:
        raise HTTPException(500, f"Spawn failed: {e}")
    app_obj = RunningApp(sid, proc)
    running[sid] = app_obj
    s["status"] = "running"
    save_json(SERVERS_FILE, servers)
    app_obj.reader_task = asyncio.create_task(read_stream(sid))
    await broadcast(sid, f"[system] AJAYVPS started: {' '.join(cmd)}")
    return {"ok": True, "status": "running"}

@app.post("/api/servers/{sid}/stop")
async def stop(sid: str, user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404)
    app_obj = running.get(sid)
    if app_obj:
        try: app_obj.proc.terminate()
        except: pass
        try: app_obj.proc.wait(timeout=5)
        except: app_obj.proc.kill()
        await broadcast(sid, "[system] AJAYVPS stopped by user")
        running.pop(sid, None)
    s["status"] = "stopped"
    save_json(SERVERS_FILE, servers)
    return {"ok": True}

@app.post("/api/servers/{sid}/restart")
async def restart(sid: str, user: str = Depends(auth_user)):
    await stop(sid, user)
    await asyncio.sleep(0.5)
    return await start(sid, user)

# ---------- pip install ----------
class PipIn(BaseModel):
    module: str

@app.post("/api/servers/{sid}/pip")
async def pip_install(sid: str, body: PipIn, user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404)
    module = body.module.strip()
    if not module or any(c in module for c in [";", "&", "|", "`", "$", "\n"]):
        raise HTTPException(400, "Invalid module name")
    # Ensure log channel exists even if app not running
    if sid not in running:
        # create a placeholder for logs broadcast
        class _Dummy: pass
        proc = subprocess.Popen(
            [sys.executable, "-u", "-m", "pip", "install", module],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
        )
        app_obj = RunningApp(sid, proc)
        running[sid] = app_obj
        await broadcast(sid, f"[pip] Installing {module}...")
        app_obj.reader_task = asyncio.create_task(read_stream(sid))
    else:
        await broadcast(sid, f"[pip] Module install requested: {module} (stop app first to install)")
    return {"ok": True}
    
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def page_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/server/{sid}", response_class=HTMLResponse)
def page_server(request: Request, sid: str):
    return templates.TemplateResponse("server.html", {"request": request, "sid": sid})

@app.get("/healthz")
def healthz():
    return {"service": "AJAYVPS", "status": "ok", "servers": len(servers)}
        
# ---------- Logs (REST snapshot) ----------
@app.get("/api/servers/{sid}/logs")
def get_logs(sid: str, user: str = Depends(auth_user)):
    s = servers.get(sid)
    if not s or s["owner"] != user: raise HTTPException(404)
    app_obj = running.get(sid)
    return {"logs": list(app_obj.logs) if app_obj else []}

# ---------- WebSocket: real-time logs ----------
@app.websocket("/ws/logs/{sid}")
async def ws_logs(ws: WebSocket, sid: str, token: str):
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = data["u"]
    except Exception:
        await ws.close(code=4401); return
    s = servers.get(sid)
    if not s or s["owner"] != user:
        await ws.close(code=4404); return
    await ws.accept()
    app_obj = running.get(sid)
    if app_obj:
        for line in list(app_obj.logs):
            await ws.send_text(line)
        app_obj.subscribers.add(ws)
    else:
        await ws.send_text("[system] App is not running. Press Start to launch.")
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        if app_obj:
            app_obj.subscribers.discard(ws)

@app.get("/")
def root():
    return {"service": "AJAYVPS", "status": "ok", "servers": len(servers)}
    