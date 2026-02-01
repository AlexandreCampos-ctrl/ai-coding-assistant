import os
import re
from pathlib import Path
from typing import List, Dict, Any
import asyncio

class ProactiveAnalyzer:
    """Monitora o projeto em background e gera sugestões proativas"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.suggestions = []

    async def analyze_project(self) -> List[Dict[str, str]]:
        """Realiza uma varredura em busca de melhorias óbvias"""
        self.suggestions = []
        
        for root, dirs, files in os.walk(self.project_root):
            if any(p in root for p in [".git", "__pycache__", "node_modules", ".brain", "venv"]):
                continue

            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    await self._check_file(Path(root) / file)
        
        return self.suggestions

    async def _check_file(self, file_path: Path):
        """Aplica regras de análise em um arquivo individual"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            relative_path = os.path.relpath(file_path, self.project_root)

            # Regra 1: Arquivos muito grandes
            if len(content.splitlines()) > 500:
                self.suggestions.append({
                    "type": "refactor",
                    "file": relative_path,
                    "message": f"O arquivo `{relative_path}` está ficando muito grande (>500 linhas). Considere modularizar.",
                    "priority": "medium"
                })

            # Regra 2: TODOs pendentes
            todos = re.findall(r'#\s*TODO:?\s*(.*)', content, re.IGNORECASE)
            todos += re.findall(r'//\s*TODO:?\s*(.*)', content, re.IGNORECASE)
            for todo in todos:
                self.suggestions.append({
                    "type": "todo",
                    "file": relative_path,
                    "message": f"TODO encontrado em `{relative_path}`: {todo.strip()}",
                    "priority": "low"
                })

            # Regra 3: Funções sem documentação (Python)
            if file_path.suffix == '.py':
                undocumented = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\(.*\):\s*(?!\s*"""|\s*\'\'\')', content)
                for func in undocumented:
                    if not func.startswith('_'): # Ignorar privadas
                        self.suggestions.append({
                            "type": "documentation",
                            "file": relative_path,
                            "message": f"A função `{func}` em `{relative_path}` não possui docstring.",
                            "priority": "low"
                        })

        except Exception as e:
            pass

    async def run_periodic_check(self, websocket_manager_callback):
        """Loop que roda a análise periodicamente e envia para a UI"""
        while True:
            suggestions = await self.analyze_project()
            if suggestions:
                # Enviar apenas a sugestão de maior prioridade para não floodar
                top_suggestion = suggestions[0]
                await websocket_manager_callback({
                    "type": "proactive_suggestion",
                    "content": top_suggestion
                })
            
            # Intervalo longo (ex: a cada 5 minutos ou após grandes mudanças)
            await asyncio.sleep(300) 
