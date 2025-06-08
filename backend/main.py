from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import os
from dotenv import load_dotenv
import json
import logging
from pydantic import BaseModel
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
if not TOGETHER_API_KEY:
    raise RuntimeError("TOGETHER_API_KEY not set in environment variables")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "Authorization"],
)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/chat/stream")
async def stream_chat(prompt_request: PromptRequest, request: Request):
    prompt = prompt_request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    async def event_generator():
        buffer = ""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    "https://api.together.xyz/inference",
                    headers={"Authorization": f"Bearer {TOGETHER_API_KEY}"},
                    json={
                        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                        "prompt": prompt,
                        "stream": True,
                        "max_tokens": 3000,  # Increased to avoid truncation
                        "temperature": 0.05,  # Lowered for maximum factual accuracy
                        "top_p": 0.9
                    }
                ) as response:
                    if response.status_code != 200:
                        logger.error(f"Together API error: {response.status_code}")
                        raise HTTPException(status_code=response.status_code, detail="Failed to connect to Together AI")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            content = line[5:].strip()
                            if content and content != "[DONE]":
                                try:
                                    data = json.loads(content)
                                    choices = data.get("choices", [])
                                    if choices:
                                        text = choices[0].get("text", "")
                                        if text:
                                            buffer += text
                                            # Split buffer by meaningful separators (e.g., newlines or bullets)
                                            lines = buffer.split("\n")
                                            buffer = lines[-1]  # Keep incomplete line in buffer
                                            for line in lines[:-1]:
                                                if line.strip():
                                                    yield f"data: {line.strip()}\n\n"
                                    else:
                                        logger.debug(f"Skipping metadata chunk: {content}")
                                except Exception as e:
                                    logger.warning(f"Could not parse chunk: {content} ({e})")
                                    yield f"data: [ERROR] Failed to parse response chunk\n\n"
                        if await request.is_disconnected():
                            logger.info("Client disconnected, stopping stream")
                            break
                    # Yield any remaining buffer content
                    if buffer.strip():
                        yield f"data: {buffer.strip()}\n\n"
        except httpx.RequestError as e:
            logger.error(f"Network error: {e}")
            yield f"data: [ERROR] Network error occurred\n\n"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            yield f"data: [ERROR] Internal server error\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")