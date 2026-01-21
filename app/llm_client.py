from __future__ import annotations

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

_client: OpenAI | None = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=30.0,
            max_retries=1,
        )
    return _client
