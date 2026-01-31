from typing import Dict, Any
from .terminal_executor import TerminalExecutor
from .browser_automator import BrowserAutomator
import os


class ExecutionTools:
    """Wrapper para expor capacidades de execução ao ToolRegistry"""
    
    def __init__(self, conversation_id: str):
        self.terminal = TerminalExecutor()
        # Salva prints na pasta brain da conversa
        self.browser = BrowserAutomator(f".brain/{conversation_id}/media")

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
