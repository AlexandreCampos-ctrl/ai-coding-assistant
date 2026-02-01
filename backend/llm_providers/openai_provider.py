"""
OpenAI Provider (GPT-3.5, GPT-4)
"""

from openai import AsyncOpenAI
from typing import List, Dict, AsyncGenerator
from backend.llm_providers.base_provider import BaseLLMProvider
import os


class OpenAIProvider(BaseLLMProvider):
    """Provider para OpenAI GPT models"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Configurar API key
        api_key = self.llm_config['api_keys'].get('openai') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada! Adicione no .env ou config.yaml")
        
        self.client = AsyncOpenAI(api_key=api_key)
    
    @property
    def name(self) -> str:
        return "openai"
    
    async def generate(self, messages: List[Dict[str, str]]) -> Dict:
        """Gera resposta (não-streaming)"""
        try:
            formatted_messages = self._format_messages(messages)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return {
                'content': response.choices[0].message.content,
                'tool_calls': []  # TODO: Implementar function calling
            }
        
        except Exception as e:
            return {
                'content': f"Erro ao gerar resposta: {str(e)}",
                'tool_calls': []
            }
    
    async def stream_generate(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Gera resposta (streaming)"""
        try:
            formatted_messages = self._format_messages(messages)
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            yield f"Erro ao gerar resposta: {str(e)}"
