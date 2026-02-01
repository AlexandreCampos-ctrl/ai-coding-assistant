from typing import List, Dict, Any, Optional
import asyncio
from .terminal_executor import TerminalExecutor
from backend.llm_providers.base_provider import BaseLLMProvider


class AutonomousExecutor:
    """Gerencia loops autônomos de execução e correção"""

    def __init__(self, provider: BaseLLMProvider, terminal: TerminalExecutor):
        self.provider = provider
        self.terminal = terminal
        self.max_retries = 3

    async def run_with_retry(self, command: str, context: str = "") -> Dict[str, Any]:
        """Executa um comando e tenta corrigir se falhar"""
        current_attempt = 0
        last_error = ""

        while current_attempt < self.max_retries:
            output_lines = []
            async for line in self.terminal.execute(command):
                if line['type'] in ['stdout', 'stderr']:
                    output_lines.append(line['content'])
                elif line['type'] == 'exit' and line['code'] == 0:
                    return {"success": True, "output": "".join(output_lines)}
                elif line['type'] == 'exit' and line['code'] != 0:
                    last_error = "".join(output_lines)
                    break
            
            # Se falhou, pedir conselho à IA
            current_attempt += 1
            if current_attempt < self.max_retries:
                correction = await self._ask_for_correction(command, last_error, context)
                if correction.get('action') == 'retry' and correction.get('new_command'):
                    command = correction['new_command']
                elif correction.get('action') == 'fix_code':
                    # TODO: Implementar aplicação automática de fix sugerido pela IA
                    pass
            
        return {"success": False, "error": last_error, "attempts": current_attempt}

    async def _ask_for_correction(self, command: str, error: str, context: str) -> Dict:
        """Pergunta ao LLM como corrigir o erro"""
        prompt = f"""
O comando terminal '{command}' falhou com o seguinte erro:
---
{error}
---
Contexto adicional: {context}

Analise o erro e sugira uma ação:
1. 'retry' com um novo comando
2. 'fix_code' se precisar editar um arquivo primeiro
3. 'give_up' se for um erro fatal

Responda em formato JSON: {{"action": "...", "reason": "...", "new_command": "..."}}
"""
        response = await self.provider.generate([{"role": "user", "content": prompt}])
        try:
            import json
            # Tenta extrair JSON da resposta
            match = re.search(r'\{.*\}', response['content'], re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
        return {"action": "give_up"}
