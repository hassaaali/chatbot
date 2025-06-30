import httpx
import json
import logging
import asyncio
from typing import Dict, List, Optional, AsyncGenerator
from config import Config

logger = logging.getLogger(__name__)

class HuggingFaceClient:
    def __init__(self):
        self.api_key = Config.HUGGINGFACE_API_KEY
        self.base_url = Config.HUGGINGFACE_API_URL
        self.timeout = Config.HF_REQUEST_TIMEOUT
        self.max_retries = Config.HF_MAX_RETRIES
        
        # Headers for Hugging Face API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_text_stream(self, prompt: str, model: str = None) -> AsyncGenerator[str, None]:
        """Generate streaming text response from Hugging Face model"""
        model = model or Config.LLM_MODEL
        url = f"{self.base_url}/{model}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": Config.LLM_MAX_TOKENS,
                "temperature": Config.LLM_TEMPERATURE,
                "top_p": Config.LLM_TOP_P,
                "do_sample": True,
                "return_full_text": False,
                "stream": True
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        "POST",
                        url,
                        headers=self.headers,
                        json=payload
                    ) as response:
                        
                        if response.status_code == 503:
                            # Model is loading, wait and retry
                            logger.info(f"Model {model} is loading, waiting...")
                            await asyncio.sleep(10)
                            retry_count += 1
                            continue
                        
                        if response.status_code != 200:
                            error_text = await response.atext()
                            logger.error(f"Hugging Face API error: {response.status_code} - {error_text}")
                            yield f"[ERROR] API Error: {response.status_code}"
                            return
                        
                        # Handle streaming response
                        buffer = ""
                        async for line in response.aiter_lines():
                            if line.startswith("data:"):
                                data_str = line[5:].strip()
                                if data_str and data_str != "[DONE]":
                                    try:
                                        data = json.loads(data_str)
                                        if "token" in data:
                                            token = data["token"]["text"]
                                            buffer += token
                                            
                                            # Yield complete words or sentences
                                            if token.endswith((" ", ".", "!", "?", "\n")):
                                                if buffer.strip():
                                                    yield buffer
                                                    buffer = ""
                                        elif "generated_text" in data:
                                            # Non-streaming response
                                            yield data["generated_text"]
                                            return
                                    except json.JSONDecodeError:
                                        # Sometimes the response is just text
                                        if data_str.strip():
                                            yield data_str
                        
                        # Yield any remaining buffer
                        if buffer.strip():
                            yield buffer
                        
                        return  # Success, exit retry loop
                        
            except httpx.RequestError as e:
                logger.error(f"Network error (attempt {retry_count + 1}): {e}")
                retry_count += 1
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    yield f"[ERROR] Network error after {self.max_retries} attempts"
                    return
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                yield f"[ERROR] Unexpected error: {str(e)}"
                return
        
        yield f"[ERROR] Failed after {self.max_retries} attempts"
    
    async def generate_text(self, prompt: str, model: str = None) -> str:
        """Generate non-streaming text response from Hugging Face model"""
        model = model or Config.LLM_MODEL
        url = f"{self.base_url}/{model}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": Config.LLM_MAX_TOKENS,
                "temperature": Config.LLM_TEMPERATURE,
                "top_p": Config.LLM_TOP_P,
                "do_sample": True,
                "return_full_text": False
            },
            "options": {
                "wait_for_model": True,
                "use_cache": False
            }
        }
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, headers=self.headers, json=payload)
                    
                    if response.status_code == 503:
                        # Model is loading, wait and retry
                        logger.info(f"Model {model} is loading, waiting...")
                        await asyncio.sleep(10)
                        retry_count += 1
                        continue
                    
                    if response.status_code != 200:
                        error_text = await response.atext()
                        logger.error(f"Hugging Face API error: {response.status_code} - {error_text}")
                        raise Exception(f"API Error: {response.status_code}")
                    
                    result = response.json()
                    
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                    elif isinstance(result, dict):
                        return result.get("generated_text", "")
                    else:
                        return str(result)
                        
            except httpx.RequestError as e:
                logger.error(f"Network error (attempt {retry_count + 1}): {e}")
                retry_count += 1
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)
                else:
                    raise Exception(f"Network error after {self.max_retries} attempts")
            except Exception as e:
                logger.error(f"Error generating text: {e}")
                raise
        
        raise Exception(f"Failed after {self.max_retries} attempts")
    
    def get_available_models(self) -> List[str]:
        """Get list of recommended models for legal analysis"""
        return [
            # Legal-specific models
            "microsoft/DialoGPT-large",
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill",
            
            # General purpose models good for legal text
            "google/flan-t5-large",
            "google/flan-t5-xl",
            "microsoft/GODEL-v1_1-large-seq2seq",
            
            # Instruction-following models
            "microsoft/GODEL-v1_1-base-seq2seq",
            "facebook/blenderbot-1B-distill",
            
            # Code and reasoning models (good for legal logic)
            "Salesforce/codegen-350M-multi",
            "bigscience/bloom-560m"
        ]