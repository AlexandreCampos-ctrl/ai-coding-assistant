from .terminal_executor import TerminalExecutor
from .browser_automator import BrowserAutomator
from .autonomous_executor import AutonomousExecutor
from backend.memory.rag.project_indexer import ProjectIndexer
from backend.agents.agent_manager import AgentManager
import os
import importlib.util
import sys


class ExecutionTools:
    """Wrapper para expor capacidades de execução ao ToolRegistry"""
    
    def __init__(self, conversation_id: str, provider: Optional[BaseLLMProvider] = None, agent_manager: Optional[AgentManager] = None, tool_registry: Any = None):
        self.terminal = TerminalExecutor()
        self.browser = BrowserAutomator(f".brain/{conversation_id}/media")
        self.indexer = ProjectIndexer(os.getcwd())
        self.agent_manager = agent_manager
        self.tool_registry = tool_registry
        if provider:
            self.autonomous = AutonomousExecutor(provider, self.terminal)
        else:
            self.autonomous = None
        self.provider_factory = lambda: provider # Simplificado para o MVP

    async def terminal_run(self, command: str) -> str:
        """Executa um comando e retorna o output acumulado"""
        output = []
        async for line in self.terminal.execute(command):
            if line['type'] in ['stdout', 'stderr']:
                output.append(line['content'])
            elif line['type'] == 'error':
                return f"ERROR: {line['content']}"
        
        return "".join(output)

    async def web_screenshot(self, url: str) -> str:
        """Tira print e retorna o caminho do arquivo"""
        try:
            path = await self.browser.screenshot(url)
            return f"Screenshot salvo em: {path}"
        except Exception as e:
            return f"Erro ao tirar screenshot: {str(e)}"

    async def web_read(self, url: str) -> str:
        """Lê o conteúdo de texto de uma página"""
        try:
            text = await self.browser.scrape_text(url)
            return text[:5000] # Limite para não estourar contexto
        except Exception as e:
            return f"Erro ao ler página: {str(e)}"

    async def project_search(self, keyword: str) -> str:
        """Busca arquivos e símbolos no projeto (Lite RAG)"""
        self.indexer.load_index() # Garante que está carregado
        results = self.indexer.search_keyword(keyword)
        if not results:
            return f"Nenhum arquivo encontrado para '{keyword}'."
        return "Arquivos encontrados:\n- " + "\n- ".join(results[:10])

    async def autonomous_terminal_run(self, command: str) -> str:
        """Executa um comando com tentativa de auto-correção"""
        if not self.autonomous:
            return "Erro: AutonomousExecutor não configurado (Provider ausente)."
        
        result = await self.autonomous.run_with_retry(command)
        if result['success']:
            return f"Sucesso (após tentativas): {result['output']}"
        else:
            return f"FALHA após {result['attempts']} tentativas. Erro final: {result['error']}"

    async def agent_spawn(self, role: str) -> str:
        """Cria um sub-agente especialista"""
        if not self.agent_manager:
            return "Erro: AgentManager não configurado."
        
        agent_id = self.agent_manager.spawn_agent(role, self.provider_factory)
        return f"Agente '{role}' criado com ID: {agent_id}. Use agent_delegate para enviar tarefas."

    async def agent_delegate(self, agent_id: str, task: str) -> str:
        """Envia uma tarefa para um sub-agente especialista"""
        if not self.agent_manager:
            return "Erro: AgentManager não configurado."
        
        return await self.agent_manager.delegate_to_agent(agent_id, task)

    async def agent_list(self) -> str:
        """Lista todos os sub-agentes ativos"""
        if not self.agent_manager:
            return "Erro: AgentManager não configurado."
        
        agents = self.agent_manager.list_agents()
        if not agents: return "Nenhum sub-agente ativo."
        return "Sub-agentes ativos:\n" + "\n".join([f"- {a['id']} ({a['role']})" for a in agents])

    async def create_new_tool(self, name: str, description: str, code: str, parameters: Dict[str, Any]) -> str:
        """Cria e registra uma nova ferramenta dinamicamente (Auto-Evolução)"""
        if not self.tool_registry:
            return "Erro: ToolRegistry não injetado em ExecutionTools."
        
        try:
            # Caminho para a nova tool
            dynamic_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "dynamic")
            os.makedirs(dynamic_dir, exist_ok=True)
            file_path = os.path.join(dynamic_dir, f"{name}.py")
            
            # Escrever o código
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Importar dinamicamente
            spec = importlib.util.spec_from_file_location(name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            
            # A função principal deve ter o mesmo nome da tool ou ser 'run'
            func = getattr(module, name, getattr(module, 'run', None))
            if not func:
                return f"Erro: Função '{name}' ou 'run' não encontrada no código fornecido."
            
            # Registrar no ToolRegistry global da conversa
            self.tool_registry.register_tool(name, description, func, parameters)
            
            return f"Sucesso! Ferramenta '{name}' criada, importada e registrada com sucesso."
            
        except Exception as e:
            return f"Erro na criação da ferramenta: {str(e)}"
