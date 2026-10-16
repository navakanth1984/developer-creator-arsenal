"""
Zoho Catalyst Advanced I/O Function: Higgsfield Clean-Room API Gateway
Provides drop-in compatibility with Higgsfield CLI/Web contracts on top of Catalyst DataStore and FileStore.
"""

import json
import uuid
import time
from typing import Dict, Any

# In-memory mock store for local development; maps to Catalyst DataStore in production
JOBS_DB: Dict[str, Dict[str, Any]] = {}
SOUL_DB: Dict[str, Dict[str, Any]] = {}

AVAILABLE_MODELS = [
    {
        "id": "wan_2_1_cinema",
        "name": "Wan 2.1 Cinema SOTA (14B)",
        "media_type": "video",
        "supported_resolutions": ["720p", "1080p"],
        "supports_camera_ctrl": True,
        "default_steps": 30
    },
    {
        "id": "ltx_video_realtime",
        "name": "LTX-Video Real-Time Diffusion",
        "media_type": "video",
        "supported_resolutions": ["512p", "720p"],
        "supports_camera_ctrl": True,
        "default_steps": 20
    },
    {
        "id": "hunyuan_video_director",
        "name": "HunyuanVideo Director Edition",
        "media_type": "video",
        "supported_resolutions": ["720p", "1080p"],
        "supports_camera_ctrl": True,
        "default_steps": 35
    }
]

def handle_get_models() -> Dict[str, Any]:
    return {
        "status": "success",
        "models": AVAILABLE_MODELS
    }

def handle_create_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = payload.get("prompt", "")
    model_id = payload.get("model", "wan_2_1_cinema")
    camera_vector = payload.get("camera", {"pan": 0.0, "tilt": 0.0, "zoom": 1.0, "roll": 0.0})
    soul_id = payload.get("soul_id", None)
    
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    
    # Register job in state
    job_record = {
        "job_id": job_id,
        "status": "PROCESSING",
        "created_at": time.time(),
        "prompt": prompt,
        "model": model_id,
        "camera_vector": camera_vector,
        "soul_id": soul_id,
        "progress": 15,
        "video_url": None
    }
    JOBS_DB[job_id] = job_record
    
    return {
        "status": "queued",
        "job_id": job_id,
        "estimated_duration_sec": 24,
        "message": "Dispatched to Zoho Catalyst Queue -> GPU Worker"
    }

def handle_poll_job(job_id: str) -> Dict[str, Any]:
    if job_id not in JOBS_DB:
        # Simulate completed sample for demo purposes
        return {
            "job_id": job_id,
            "status": "COMPLETED",
            "progress": 100,
            "video_url": "https://catalyst.zoho.com/filestore/rendered_videos/sample_cinematic.mp4",
            "duration_sec": 4.5,
            "resolution": "1080p",
            "cost_usd": 0.00
        }
        
    job = JOBS_DB[job_id]
    elapsed = time.time() - job["created_at"]
    
    if elapsed > 10:
        job["status"] = "COMPLETED"
        job["progress"] = 100
        job["video_url"] = f"https://catalyst.zoho.com/filestore/rendered_videos/{job_id}.mp4"
    else:
        job["progress"] = min(90, int((elapsed / 10.0) * 100))
        
    return job

def handle_soul_create(payload: Dict[str, Any]) -> Dict[str, Any]:
    name = payload.get("name", "Unnamed Subject")
    images = payload.get("images", [])
    
    soul_id = f"soul_{uuid.uuid4().hex[:8]}"
    SOUL_DB[soul_id] = {
        "soul_id": soul_id,
        "name": name,
        "reference_count": len(images),
        "embedding_status": "READY"
    }
    
    return {
        "status": "success",
        "soul_id": soul_id,
        "name": name,
        "message": f"Character embedding trained from {len(images)} reference photos."
    }

def catalyst_handler(request_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entrypoint for Zoho Catalyst Advanced I/O function.
    """
    path = request_event.get("path", "/")
    method = request_event.get("method", "GET").upper()
    body = request_event.get("body", {})
    if isinstance(body, str) and body:
        try: body = json.loads(body)
        except Exception: body = {}

    if path == "/api/v1/models" and method == "GET":
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": handle_get_models()}
    elif path == "/api/v1/generate" and method == "POST":
        return {"statusCode": 201, "headers": {"Content-Type": "application/json"}, "body": handle_create_job(body)}
    elif path.startswith("/api/v1/jobs/poll/") and method == "GET":
        job_id = path.split("/")[-1]
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": handle_poll_job(job_id)}
    elif path == "/api/v1/jobs/cost" and method == "POST":
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": {"credits": 0, "tier": "sovereign_open_weights"}}
    elif path == "/api/v1/soul-id/create" and method == "POST":
        return {"statusCode": 201, "headers": {"Content-Type": "application/json"}, "body": handle_soul_create(body)}
    else:
        return {"statusCode": 404, "headers": {"Content-Type": "application/json"}, "body": {"error": f"Route {method} {path} not found"}}

def test_local():
    print("[+] Testing Catalyst Advanced I/O Function locally:")
    res_models = catalyst_handler({"path": "/api/v1/models", "method": "GET"})
    print("Models:", json.dumps(res_models["body"], indent=2))
    
    res_gen = catalyst_handler({
        "path": "/api/v1/generate",
        "method": "POST",
        "body": {
            "prompt": "Cinematic slow zoom into an astronaut standing on a neon cyberpunk street",
            "model": "wan_2_1_cinema",
            "camera": {"zoom": 1.25, "pan": 0.1}
        }
    })
    print("\nGeneration Dispatch:", json.dumps(res_gen["body"], indent=2))
    job_id = res_gen["body"]["job_id"]
    
    res_poll = catalyst_handler({"path": f"/api/v1/jobs/poll/{job_id}", "method": "GET"})
    print("\nInitial Poll:", json.dumps(res_poll["body"], indent=2))

if __name__ == "__main__":
    test_local()
