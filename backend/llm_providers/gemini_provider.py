"""
Google Gemini Provider
"""

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import google.generativeai as genai
from typing import List, Dict, AsyncGenerator
from backend.llm_providers.base_provider import BaseLLMProvider
import os


class GeminiProvider(BaseLLMProvider):
    """Provider para Google Gemini"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Configurar API key
        api_key = self.llm_config['api_keys'].get('gemini') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada! Adicione no .env ou config.yaml")
        
        genai.configure(api_key=api_key)
        
        # Inicializar modelo sem tools por padrão
        self._setup_model()

    def _setup_model(self, tools: list = None):
        """Configura a instância do modelo com ferramentas se disponíveis"""
        self.model_instance = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                'temperature': self.temperature,
                'max_output_tokens': self.max_tokens,
            },
            tools=tools
        )
    
    @property
    def name(self) -> str:
        return "gemini"
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """Converte formato de mensagens para Gemini"""
        gemini_messages = []
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            # Gemini usa 'user' e 'model' como roles
            if role == 'system':
                # System prompts vão como primeira mensagem do usuário
                gemini_messages.append({
                    'role': 'user',
                    'parts': [f"[SYSTEM] {content}"]
                })
            elif role == 'assistant':
                gemini_messages.append({
                    'role': 'model',
                    'parts': [content]
                })
            else:  # user
                gemini_messages.append({
                    'role': 'user',
                    'parts': [content]
                })
        
        return gemini_messages
    
    async def generate(self, messages: List[Dict[str, str]], tools: list = None) -> Dict:
        """Gera resposta (não-streaming)"""
        try:
            # Re-configurar modelo se houver tools
            if tools:
                self._setup_model(tools)

            # Formatar mensagens
            formatted_messages = self._format_messages(messages)
            gemini_messages = self._convert_messages(formatted_messages)
            
            # Criar chat
            chat = self.model_instance.start_chat(history=gemini_messages[:-1])
            
            # Enviar última mensagem
            response = chat.send_message(gemini_messages[-1]['parts'][0])
            
            tool_calls = []
            # Extrair function calls se houver
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if fn := part.function_call:
                        tool_calls.append({
                            'name': fn.name,
                            'arguments': dict(fn.args)
                        })

            return {
                'content': response.text if not tool_calls else "",
                'tool_calls': tool_calls
            }
        
        except Exception as e:
            return {
                'content': f"Erro ao gerar resposta: {str(e)}",
                'tool_calls': []
            }
    
    async def stream_generate(self, messages: List[Dict[str, str]], tools: list = None) -> AsyncGenerator[str, None]:
        """Gera resposta (streaming)"""
        try:
            # Re-configurar modelo se houver tools
            if tools:
                self._setup_model(tools)

            # Formatar mensagens
            formatted_messages = self._format_messages(messages)
            gemini_messages = self._convert_messages(formatted_messages)
            
            # Criar chat
            chat = self.model_instance.start_chat(history=gemini_messages[:-1])
            
            # Stream response
            response = chat.send_message(
                gemini_messages[-1]['parts'][0],
                stream=True
            )
            
            for chunk in response:
                try:
                    if hasattr(chunk, 'text') and chunk.text:
                        yield chunk.text
                except (ValueError, AttributeError):
                    # Ignora chunks sem texto (ex: finish_reason)
                    continue
        
        except Exception as e:
            yield f"Erro ao gerar resposta: {str(e)}"
