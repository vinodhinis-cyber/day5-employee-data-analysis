import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Header, HTTPException

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

SECRET_API_KEY = os.getenv("API_KEY")


def verify_api_key(api_key: str = Header(default=None, alias="X-API-Key")):
    if api_key is None:
        raise HTTPException(status_code=401, detail="API key missing")

    if api_key != SECRET_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return api_key
