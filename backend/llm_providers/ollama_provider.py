"""
Ollama Provider (modelos locais)
"""

import aiohttp
from typing import List, Dict, AsyncGenerator
from backend.llm_providers.base_provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Provider para Ollama (modelos locais)"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "http://localhost:11434"  # URL padrão do Ollama
    
    @property
    def name(self) -> str:
        return "ollama"
    
    async def generate(self, messages: List[Dict[str, str]]) -> Dict:
        """Gera resposta (não-streaming)"""
        try:
            formatted_messages = self._format_messages(messages)
            
            # Converter para formato do Ollama
            prompt = self._convert_to_prompt(formatted_messages)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": self.temperature,
                        "stream": False
                    }
                ) as response:
                    result = await response.json()
                    return {
                        'content': result.get('response', ''),
                        'tool_calls': []
                    }
        
        except Exception as e:
            return {
                'content': f"Erro ao conectar com Ollama: {str(e)}. Certifique-se que Ollama está rodando (ollama serve)",
                'tool_calls': []
            }
    
    async def stream_generate(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Gera resposta (streaming)"""
        try:
            formatted_messages = self._format_messages(messages)
            prompt = self._convert_to_prompt(formatted_messages)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": self.temperature,
                        "stream": True
                    }
                ) as response:
                    async for line in response.content:
                        if line:
                            import json
                            try:
                                data = json.loads(line)
                                if 'response' in data:
                                    yield data['response']
                            except:
                                continue
        
        except Exception as e:
            yield f"Erro ao conectar com Ollama: {str(e)}"
    
    def _convert_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Converte mensagens para formato de prompt"""
        prompt_parts = []
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                prompt_parts.append(f"System: {content}\n")
            elif role == 'user':
                prompt_parts.append(f"User: {content}\n")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}\n")
        
        prompt_parts.append("Assistant: ")
        return "\n".join(prompt_parts)
