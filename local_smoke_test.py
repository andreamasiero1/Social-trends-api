from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

get_paths = [
    ("/", {}),
    ("/health", {}),
    ("/openapi.json", {}),
    ("/v1/auth/generate-key", {"email": "test@example.com", "tier": "free"}),
    ("/v1/auth/v2/generate-key", {"email": "test@example.com", "tier": "free"}),
]

for path, params in get_paths:
    try:
        resp = client.get(path, params=params)
        ct = resp.headers.get("content-type", "")
        body = resp.json() if ct.startswith("application/json") else resp.text[:120]
        print(f"GET {path} -> {resp.status_code} | {body}")
    except Exception as e:
        print(f"GET {path} -> ERROR: {e}")

# POST con body JSON
post_tests = [
    ("/v1/auth/generate-key", {"email": "test@example.com", "tier": "free"}),
    ("/v1/auth/v2/generate-key", {"email": "test@example.com", "tier": "free"}),
    ("/v1/auth/generate-key", {}),  # dovrebbe dare 422 per email mancante
]

for path, payload in post_tests:
    try:
        resp = client.post(path, json=payload)
        ct = resp.headers.get("content-type", "")
        body = resp.json() if ct.startswith("application/json") else resp.text[:120]
        print(f"POST {path} body={payload} -> {resp.status_code} | {body}")
    except Exception as e:
        print(f"POST {path} -> ERROR: {e}")
