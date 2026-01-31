"""
Base class para providers de LLM
"""

from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Optional


class BaseLLMProvider(ABC):
    """Interface base para todos os providers de LLM"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.llm_config = config['llm']
        self.model = self.llm_config['model']
        self.temperature = self.llm_config['temperature']
        self.max_tokens = self.llm_config['max_tokens']
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do provider"""
        pass
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]]) -> Dict:
        """
        Gera resposta do LLM (não-streaming)
        
        Args:
            messages: Lista de mensagens [{"role": "user", "content": "..."}]
        
        Returns:
            Dict com 'content' e opcionalmente 'tool_calls'
        """
        pass
    
    @abstractmethod
    async def stream_generate(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Gera resposta do LLM (streaming)
        
        Args:
            messages: Lista de mensagens
        
        Yields:
            Chunks de texto da resposta
        """
        pass
    
    def _build_system_prompt(self) -> str:
        """Constrói o prompt do sistema"""
        # TODO: Carregar de arquivo de configuração
        return """Você é um assistente de programação inteligente e útil.

Capacidades:
- Responder perguntas sobre programação
- Escrever e explicar código
- Usar ferramentas para manipular arquivos e executar código
- Depurar problemas

Sempre seja claro, conciso e forneça exemplos quando apropriado."""
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Formata mensagens com system prompt"""
        system_msg = {"role": "system", "content": self._build_system_prompt()}
        return [system_msg] + messages
