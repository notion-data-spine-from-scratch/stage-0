import json
import os
import shutil
import subprocess

import jwt
import pytest

JWT_SECRET = "secret"


LUAJIT = shutil.which("luajit") or shutil.which("lua") or shutil.which("lua5.4")


def run_lua(token=None):
    env = os.environ.copy()
    env["JWT_SECRET"] = JWT_SECRET
    env["STUB_JWT"] = "1"
    env["STUB_CJSON"] = "1"
    env["PRESIGN_PATH"] = "services/asset-proxy/presign.py"
    if token:
        env["TOKEN"] = token
    if LUAJIT is None:
        pytest.skip("Lua interpreter not available")
    result = subprocess.run(
        [LUAJIT, "tests/run_upload.lua"], capture_output=True, text=True, env=env
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
