import json
import os
import subprocess

import jwt

JWT_SECRET = "secret"


def run_lua(token=None):
    env = os.environ.copy()
    env["JWT_SECRET"] = JWT_SECRET
    env["STUB_JWT"] = "1"
    env["PRESIGN_PATH"] = "services/asset-proxy/presign.py"
    if token:
        env["TOKEN"] = token
    result = subprocess.run(
        ["luajit", "tests/run_upload.lua"], capture_output=True, text=True, env=env
    )
    return result.stdout.strip()


def test_upload_valid_token():
    token = jwt.encode({"sub": "123"}, JWT_SECRET, algorithm="HS256")
    output = run_lua(token)
    data = json.loads(output)
    assert "url" in data
    assert data["url"].startswith("http")


def test_upload_invalid_token():
    output = run_lua("invalid")
    assert output == "EXIT:401"
