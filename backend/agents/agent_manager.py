from typing import List, Dict, Any, Optional
from backend.llm_providers.base_provider import BaseLLMProvider
import uuid

class SpecializedAgent:
    """Um agente especialista com um papel definido e seu próprio provedor LLM"""
    
    def __init__(self, agent_id: str, role: str, system_prompt: str, provider: BaseLLMProvider):
        self.agent_id = agent_id
        self.role = role
        self.system_prompt = system_prompt
        self.provider = provider
        self.messages = [{"role": "system", "content": system_prompt}]

    async def think(self, user_message: str, tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Processa uma mensagem do usuário ou do agente principal"""
        self.messages.append({"role": "user", "content": user_message})
        
        response = await self.provider.generate(self.messages, tools=tools)
        
        if response.get('content'):
            self.messages.append({"role": "assistant", "content": response['content']})
            
        return response

class AgentManager:
    """Gerencia o ciclo de vida e a orquestração de sub-agentes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_agents: Dict[str, SpecializedAgent] = {}
        self.roles_definitions = {
            "security": "Você é um Analista de Segurança Cibernética especializado em auditoria de código e prevenção de vulnerabilidades (OWASP).",
            "tester": "Você é um Especialista em QA e Testes Autômatos, focado em cobertura de código e testes de estresse.",
            "frontend": "Você é um Engenheiro de Frontend especialista em UI/UX e frameworks modernos como React e Vue.",
            "database": "Você é um DBA e Arquiteto de Dados focado em otimização de queries e modelagem relacional.",
        }

    def spawn_agent(self, role: str, provider_factory) -> str:
        """Cria um novo agente especialista sob demanda"""
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        system_prompt = self.roles_definitions.get(role, f"Você é um especialista em {role}.")
        
        # Cria uma instância limpa do provider para o agente
        provider = provider_factory()
        
        self.active_agents[agent_id] = SpecializedAgent(agent_id, role, system_prompt, provider)
        return agent_id

    async def delegate_to_agent(self, agent_id: str, Task: str) -> str:
        """Envia uma tarefa para um agente específico e retorna a resposta"""
        if agent_id not in self.active_agents:
            return f"ERRO: Agente {agent_id} não encontrado."
            
        agent = self.active_agents[agent_id]
        response = await agent.think(Task)
        return response.get('content', "O agente não retornou conteúdo.")

    def list_agents(self) -> List[Dict[str, str]]:
        """Lista todos os agentes ativos e seus papéis"""
        return [{"id": id, "role": agent.role} for id, agent in self.active_agents.items()]
