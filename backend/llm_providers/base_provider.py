"""
Base class para providers de LLM
"""

from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Optional
from skills.skill_manager import SkillManager
import os


class BaseLLMProvider(ABC):
    """Interface base para todos os providers de LLM"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.llm_config = config['llm']
        self.model = self.llm_config['model']
        self.temperature = self.llm_config['temperature']
        self.max_tokens = self.llm_config['max_tokens']
        self.skill_manager = SkillManager(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "skills"))
    
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
        return """Você é o Antigravity-Style AI Assistant, um assistente de programação de elite.

Sua missão é ajudar o usuário com tarefas complexas de codificação seguindo um fluxo de trabalho estruturado.

### 🛠️ Gestão de Tarefas (Task Management)
Sempre que o usuário pedir algo complexo, você deve organizar seu trabalho em tarefas. 
Use o marcador abaixo no início da sua resposta para atualizar o progresso:
[[TASK_UPDATE: Name="Nome da Tarefa", Mode="planning|execution|verification", Progress=0-100, Status="O que está fazendo agora"]]

Modes:
- planning: Pesquisa, design e planejamento.
- execution: Escrita de código e implementação.
- verification: Testes e validação.

### 📄 Artifacts (Documentação)
Você pode criar e atualizar documentos especiais (Artifacts) como base de conhecimento:
- task.md: Lista de tarefas e progresso.
- implementation_plan.md: Plano técnico antes de codar.
- walkthrough.md: Documentação final do que foi feito.

Use o marcador abaixo para sugerir a criação/atualização de um artifact:
[[ARTIFACT_UPDATE: Name="filename.md", Type="task|implementation_plan|walkthrough|other", Summary="Resumo curto"]]
Contendo o conteúdo markdown logo abaixo.

### 🤖 Comportamento
- Seja proativo, mas estruturado.
- Explique o "porquê" das decisões técnicas.
- Use blocos de código com linguagem especificada.
- Fale em Português do Brasil.

{self.skill_manager.get_skill_prompts()}

Sempre que iniciar uma nova fase, atualize a [[TASK_UPDATE]]."""
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Formata mensagens com system prompt"""
        system_msg = {"role": "system", "content": self._build_system_prompt()}
        return [system_msg] + messages
