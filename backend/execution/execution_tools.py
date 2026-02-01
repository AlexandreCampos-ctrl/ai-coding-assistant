from .terminal_executor import TerminalExecutor
from .browser_automator import BrowserAutomator
from .autonomous_executor import AutonomousExecutor
from ..memory.rag.project_indexer import ProjectIndexer
import os


class ExecutionTools:
    """Wrapper para expor capacidades de execução ao ToolRegistry"""
    
    def __init__(self, conversation_id: str, provider: Optional[BaseLLMProvider] = None):
        self.terminal = TerminalExecutor()
        self.browser = BrowserAutomator(f".brain/{conversation_id}/media")
        self.indexer = ProjectIndexer(os.getcwd())
        if provider:
            self.autonomous = AutonomousExecutor(provider, self.terminal)
        else:
            self.autonomous = None

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
