import httpx
import json
import logging
import asyncio
from typing import Dict, List, Optional, AsyncGenerator
from config import Config

logger = logging.getLogger(__name__)

class TogetherClient:
    def __init__(self):
        self.api_key = Config.TOGETHER_API_KEY
        self.base_url = Config.TOGETHER_API_URL
        self.timeout = Config.TOGETHER_REQUEST_TIMEOUT
        self.max_retries = Config.TOGETHER_MAX_RETRIES
        
        # Headers for Together AI API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_text_stream(self, prompt: str, model: str = None) -> AsyncGenerator[str, None]:
        """Generate streaming text response from Together AI model"""
        model = model or Config.LLM_MODEL
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": Config.LLM_MAX_TOKENS,
            "temperature": Config.LLM_TEMPERATURE,
            "top_p": Config.LLM_TOP_P,
            "stream": True
        }
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        "POST",
                        self.base_url,
                        headers=self.headers,
                        json=payload
                    ) as response:
                        
                        if response.status_code == 429:
                            # Rate limit, wait and retry
                            logger.info("Rate limit hit, waiting...")
                            await asyncio.sleep(5)
                            retry_count += 1
                            continue
                        
                        if response.status_code != 200:
                            try:
                                error_content = await response.aread()
                                error_text = error_content.decode('utf-8')
                            except Exception:
                                error_text = f"HTTP {response.status_code}"
                            
                            logger.error(f"Together AI API error: {response.status_code} - {error_text}")
                            yield f"[ERROR] API Error: {response.status_code} - {error_text}"
                            return
                        
                        # Handle streaming response
                        buffer = ""
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:].strip()
                                if data_str and data_str != "[DONE]":
                                    try:
                                        data = json.loads(data_str)
                                        if "choices" in data and len(data["choices"]) > 0:
                                            delta = data["choices"][0].get("delta", {})
                                            if "content" in delta:
                                                content = delta["content"]
                                                buffer += content
                                                
                                                # Yield complete words or sentences
                                                if content.endswith((" ", ".", "!", "?", "\n")):
                                                    if buffer.strip():
                                                        yield buffer
                                                        buffer = ""
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
                    yield f"[ERROR] Network error after {self.max_retries} attempts: {str(e)}"
                    return
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                yield f"[ERROR] Unexpected error: {str(e)}"
                return
        
        yield f"[ERROR] Failed after {self.max_retries} attempts"
    
    async def generate_text(self, prompt: str, model: str = None) -> str:
        """Generate non-streaming text response from Together AI model"""
        model = model or Config.LLM_MODEL
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": Config.LLM_MAX_TOKENS,
            "temperature": Config.LLM_TEMPERATURE,
            "top_p": Config.LLM_TOP_P,
            "stream": False
        }
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(self.base_url, headers=self.headers, json=payload)
                    
                    if response.status_code == 429:
                        # Rate limit, wait and retry
                        logger.info("Rate limit hit, waiting...")
                        await asyncio.sleep(5)
                        retry_count += 1
                        continue
                    
                    if response.status_code != 200:
                        try:
                            error_content = await response.aread()
                            error_text = error_content.decode('utf-8')
                        except Exception:
                            error_text = f"HTTP {response.status_code}"
                        
                        logger.error(f"Together AI API error: {response.status_code} - {error_text}")
                        raise Exception(f"API Error: {response.status_code} - {error_text}")
                    
                    result = response.json()
                    
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        return str(result)
                        
            except httpx.RequestError as e:
                logger.error(f"Network error (attempt {retry_count + 1}): {e}")
                retry_count += 1
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)
                else:
                    raise Exception(f"Network error after {self.max_retries} attempts: {str(e)}")
            except Exception as e:
                logger.error(f"Error generating text: {e}")
                raise
        
        raise Exception(f"Failed after {self.max_retries} attempts")
    
    def get_available_models(self) -> List[str]:
        """Get list of recommended models for legal analysis"""
        return [
            # Legal-specific models
            "meta-llama/Llama-2-7b-chat-hf",
            "meta-llama/Llama-2-13b-chat-hf",
            "meta-llama/Llama-2-70b-chat-hf",
            
            # Code and reasoning models (good for legal logic)
            "codellama/CodeLlama-7b-Instruct-hf",
            "codellama/CodeLlama-13b-Instruct-hf",
            
            # General purpose models good for legal text
            "mistralai/Mistral-7B-Instruct-v0.1",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            
            # Instruction-following models
            "togethercomputer/RedPajama-INCITE-7B-Chat",
            "NousResearch/Nous-Hermes-2-Yi-34B",
            "teknium/OpenHermes-2.5-Mistral-7B"
        ]