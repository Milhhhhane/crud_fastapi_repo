"""DevOps Monitoring API — FastAPI app exposing CRUD on monitored servers."""
import logging

from fastapi import Depends, FastAPI, Header, HTTPException, Query

from models import Server, ServerIn, ServerOut
from health import HealthChecker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

app = FastAPI(
    title="DevOps Monitoring API",
    description="Real-time server health monitoring.",
    version="1.0.0",
    contact={"name": "Milhane", "email": "milhane@example.com"},
)

# ── In-memory store ─────────────────────────────────────────────────
_store: dict[int, Server] = {}
_counter = 0
checker = HealthChecker()


# ── Optional API-key dependency (stretch goal) ──────────────────────
def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != "ops-secret":
        raise HTTPException(status_code=403, detail="Invalid API key")


# ── System ──────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """API liveness endpoint."""
    return {"status": "ok", "servers_monitored": len(_store)}


# ── CRUD : Servers ──────────────────────────────────────────────────
@app.post(
    "/servers",
    response_model=ServerOut,
    status_code=201,
    tags=["Servers"],
    summary="Register a new server",
    dependencies=[Depends(require_api_key)],
)
async def register_server(server: ServerIn):
    global _counter
    _counter += 1
    record = Server(
        id=_counter,
        name=server.name,
        host=server.host,
        port=server.port,
        tags=server.tags,
    )
    _store[_counter] = record
    return record


@app.get("/servers", response_model=list[ServerOut], tags=["Servers"])
async def list_servers(
    status: str | None = Query(
        default=None,
        description="Filter by status (UP, DEGRADED, DOWN, unknown).",
    ),
):
    servers = list(_store.values())
    if status:
        servers = [s for s in servers if s.status == status]
    return servers


@app.get("/servers/{server_id}", response_model=ServerOut, tags=["Servers"])
async def get_server(server_id: int):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    return _store[server_id]


@app.delete(
    "/servers/{server_id}",
    status_code=204,
    tags=["Servers"],
    dependencies=[Depends(require_api_key)],
)
async def delete_server(server_id: int):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    del _store[server_id]


@app.post(
    "/servers/{server_id}/check",
    response_model=ServerOut,
    tags=["Servers"],
    summary="Trigger a live health check on one server",
)
async def trigger_health_check(server_id: int):
    if server_id not in _store:
        raise HTTPException(status_code=404, detail="Server not found")
    return await checker.check(_store[server_id])


@app.post(
    "/servers/check-all",
    response_model=list[ServerOut],
    tags=["Servers"],
    summary="Trigger health checks on every server concurrently",
)
async def trigger_all_health_checks():
    if not _store:
        return []
    return await checker.check_all(list(_store.values()))
