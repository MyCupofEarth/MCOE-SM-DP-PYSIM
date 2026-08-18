from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime, timezone
import secrets

app = FastAPI(
    title="MCOE eSIM Provisioning API",
    version="2.1.0"
)

# =========================================================
# IN-MEMORY STORAGE
# =========================================================

devices = {}
esim_requests = {}


# =========================================================
# MODELS
# =========================================================

class DeviceRegisterRequest(BaseModel):
    device_id: str
    device_name: str


class HeartbeatRequest(BaseModel):
    device_id: str


class ProvisionRequest(BaseModel):
    device_id: str
    eid: str | None = None


# =========================================================
# HELPERS
# =========================================================

def now():
    return datetime.now(timezone.utc).isoformat()


def get_device(device_id: str):
    device = devices.get(device_id)

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not registered"
        )

    return device


def verify_token(device, token):
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing device token"
        )

    if token != device["device_token"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid device token"
        )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "name": "MCOE eSIM Provisioning API",
        "status": "online",
        "version": "2.1.0"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "MCOE eSIM API",
        "timestamp": now()
    }


# =========================================================
# DEVICE REGISTRATION
# =========================================================

@app.post("/api/device/register")
def register_device(data: DeviceRegisterRequest):

    device_id = data.device_id

    token = secrets.token_urlsafe(32)

    devices[device_id] = {

        "device_id": device_id,

        "device_name": data.device_name,

        "device_token": token,

        "online": True,

        "last_seen": now(),

        "eid": None,

        "esim_status": "not_provisioned",

        "profile_id": None
    }

    return {

        "registered": True,

        "device_id": device_id,

        "device_token": token
    }


# =========================================================
# DEVICE HEARTBEAT
# =========================================================

@app.post("/api/device/heartbeat")
def heartbeat(
    data: HeartbeatRequest,
    authorization: str | None = Header(default=None)
):

    device = get_device(data.device_id)

    token = None

    if authorization:

        if authorization.lower().startswith("bearer "):

            token = authorization[7:]

    verify_token(device, token)

    device["online"] = True
    device["last_seen"] = now()

    return {
        "ok": True,
        "device_id": data.device_id,
        "last_seen": device["last_seen"]
    }


# =========================================================
# ESIM PROVISION REQUEST
# =========================================================

@app.post("/api/esim/provision")
def esim_provision(
    data: ProvisionRequest,
    authorization: str | None = Header(default=None)
):

    device = get_device(data.device_id)

    token = None

    if authorization:

        if authorization.lower().startswith("bearer "):

            token = authorization[7:]

    verify_token(device, token)

    # Store EID if Android supplied it
    if data.eid:

        device["eid"] = data.eid

    request_id = secrets.token_urlsafe(16)

    esim_requests[request_id] = {

        "request_id": request_id,

        "device_id": data.device_id,

        "eid": data.eid,

        "status": "pending",

        "created_at": now()
    }

    device["esim_status"] = "pending"

    return {

        "provider": "MCOE",

        "request_id": request_id,

        "device_id": data.device_id,

        "eid": data.eid,

        "status": "pending",

        "message":
            "eSIM provisioning request created. "
            "The SM-DP+ must now process this request."
    }


# =========================================================
# ESIM STATUS
# =========================================================

@app.get("/api/esim/status")
def esim_status(
    device_id: str,
    authorization: str | None = Header(default=None)
):

    device = get_device(device_id)

    token = None

    if authorization:

        if authorization.lower().startswith("bearer "):

            token = authorization[7:]

    verify_token(device, token)

    return {

        "provider": "MCOE",

        "device_id": device_id,

        "eid": device["eid"],

        "status": device["esim_status"],

        "profile_id": device["profile_id"],

        "esim_active":
            device["esim_status"] == "active"
    }


# =========================================================
# PROVISION REQUEST STATUS
# =========================================================

@app.get("/api/esim/request/{request_id}")
def provision_request_status(
    request_id: str
):

    request = esim_requests.get(request_id)

    if not request:

        raise HTTPException(
            status_code=404,
            detail="Provision request not found"
        )

    return request


# =========================================================
# DEVICE STATUS
# =========================================================

@app.get("/api/device/{device_id}")
def device_status(
    device_id: str,
    authorization: str | None = Header(default=None)
):

    device = get_device(device_id)

    token = None

    if authorization:

        if authorization.lower().startswith("bearer "):

            token = authorization[7:]

    verify_token(device, token)

    return device
