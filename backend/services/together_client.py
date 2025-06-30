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
        """Generate streaming text response from Together AI model optimized for legal analysis"""
        model = model or Config.LLM_MODEL
        
        # Optimize parameters based on model for legal analysis
        temperature = 0.05 if "70b" in model.lower() else Config.LLM_TEMPERATURE  # Even lower for 70B
        max_tokens = 4000 if "70b" in model.lower() else Config.LLM_MAX_TOKENS  # More tokens for detailed legal analysis
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert legal AI assistant with deep knowledge of law, legal procedures, and document analysis. Provide accurate, detailed, and well-reasoned legal analysis while always recommending consultation with qualified attorneys for specific legal advice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": Config.LLM_TOP_P,
            "stream": True,
            "repetition_penalty": 1.1,  # Reduce repetition in legal analysis
            "stop": ["Human:", "Assistant:", "User:"]  # Stop sequences for cleaner responses
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
                            wait_time = min(10 * (2 ** retry_count), 60)  # Exponential backoff, max 60s
                            logger.info(f"Rate limit hit, waiting {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            retry_count += 1
                            continue
                        
                        if response.status_code == 503:
                            # Model loading, wait and retry
                            logger.info(f"Model {model} is loading, waiting...")
                            await asyncio.sleep(15)
                            retry_count += 1
                            continue
                        
                        if response.status_code != 200:
                            try:
                                error_content = await response.aread()
                                error_text = error_content.decode('utf-8')
                                error_data = json.loads(error_text)
                                error_message = error_data.get('error', {}).get('message', error_text)
                            except Exception:
                                error_message = f"HTTP {response.status_code}"
                            
                            logger.error(f"Together AI API error: {response.status_code} - {error_message}")
                            yield f"[ERROR] Legal AI Error: {error_message}"
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
                                                
                                                # Yield complete words or sentences for better legal readability
                                                if content.endswith((" ", ".", "!", "?", "\n", ":", ";")):
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
        """Generate non-streaming text response from Together AI model optimized for legal analysis"""
        model = model or Config.LLM_MODEL
        
        # Optimize parameters based on model for legal analysis
        temperature = 0.05 if "70b" in model.lower() else Config.LLM_TEMPERATURE
        max_tokens = 4000 if "70b" in model.lower() else Config.LLM_MAX_TOKENS
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert legal AI assistant with deep knowledge of law, legal procedures, and document analysis. Provide accurate, detailed, and well-reasoned legal analysis while always recommending consultation with qualified attorneys for specific legal advice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": Config.LLM_TOP_P,
            "stream": False,
            "repetition_penalty": 1.1,
            "stop": ["Human:", "Assistant:", "User:"]
        }
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(self.base_url, headers=self.headers, json=payload)
                    
                    if response.status_code == 429:
                        wait_time = min(10 * (2 ** retry_count), 60)
                        logger.info(f"Rate limit hit, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        retry_count += 1
                        continue
                    
                    if response.status_code == 503:
                        logger.info(f"Model {model} is loading, waiting...")
                        await asyncio.sleep(15)
                        retry_count += 1
                        continue
                    
                    if response.status_code != 200:
                        try:
                            error_content = await response.aread()
                            error_text = error_content.decode('utf-8')
                            error_data = json.loads(error_text)
                            error_message = error_data.get('error', {}).get('message', error_text)
                        except Exception:
                            error_message = f"HTTP {response.status_code}"
                        
                        logger.error(f"Together AI API error: {response.status_code} - {error_message}")
                        raise Exception(f"Legal AI Error: {error_message}")
                    
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
        """Get list of models optimized for legal analysis, ranked by capability"""
        return [
            # Primary recommendation for legal analysis
            "meta-llama/Llama-2-70b-chat-hf",  # Best for complex legal reasoning
            
            # High-performance alternatives
            "mistralai/Mixtral-8x7B-Instruct-v0.1",  # Excellent for legal documents
            "meta-llama/Llama-2-13b-chat-hf",  # Balanced performance
            
            # Specialized models
            "codellama/CodeLlama-13b-Instruct-hf",  # Good for legal logic
            "mistralai/Mistral-7B-Instruct-v0.1",  # Fast instruction following
            
            # Additional options
            "meta-llama/Llama-2-7b-chat-hf",  # Fastest option
            "codellama/CodeLlama-7b-Instruct-hf",  # Lightweight logic model
            "togethercomputer/RedPajama-INCITE-7B-Chat",  # Alternative option
            "NousResearch/Nous-Hermes-2-Yi-34B",  # High-quality reasoning
            "teknium/OpenHermes-2.5-Mistral-7B"  # Instruction-tuned
        ]
    
    def get_model_info(self, model: str) -> Dict:
        """Get detailed information about a specific model for legal use"""
        model_info = {
            "meta-llama/Llama-2-70b-chat-hf": {
                "name": "Llama 2 70B (Recommended for Legal)",
                "description": "Most capable model for complex legal reasoning and comprehensive analysis",
                "best_for": "Complex contracts, legal research, detailed legal analysis",
                "performance": "Highest",
                "speed": "Slower",
                "legal_rating": 5
            },
            "mistralai/Mixtral-8x7B-Instruct-v0.1": {
                "name": "Mixtral 8x7B",
                "description": "Excellent balance of performance and speed for legal document analysis",
                "best_for": "Contract review, legal document analysis, legal Q&A",
                "performance": "High",
                "speed": "Fast",
                "legal_rating": 4
            },
            "meta-llama/Llama-2-13b-chat-hf": {
                "name": "Llama 2 13B",
                "description": "Good performance for most legal tasks with reasonable speed",
                "best_for": "General legal Q&A, document review, legal explanations",
                "performance": "Good",
                "speed": "Fast",
                "legal_rating": 4
            },
            "codellama/CodeLlama-13b-Instruct-hf": {
                "name": "CodeLlama 13B",
                "description": "Excellent for legal logic, procedures, and structured reasoning",
                "best_for": "Contract logic, legal procedures, compliance analysis",
                "performance": "Good",
                "speed": "Fast",
                "legal_rating": 3
            },
            "mistralai/Mistral-7B-Instruct-v0.1": {
                "name": "Mistral 7B",
                "description": "Fast and efficient for structured legal tasks",
                "best_for": "Quick legal analysis, specific legal instructions",
                "performance": "Good",
                "speed": "Very Fast",
                "legal_rating": 3
            }
        }
        
        return model_info.get(model, {
            "name": model.split('/')[-1],
            "description": "General purpose model",
            "best_for": "General tasks",
            "performance": "Unknown",
            "speed": "Unknown",
            "legal_rating": 2
        })