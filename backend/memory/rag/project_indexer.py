import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any


class ProjectIndexer:
    """Indexador leve de projeto para busca de símbolos e contexto"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.index_file = self.project_root / ".brain" / "project_index.json"
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        self.index = {
            "files": {},
            "symbols": {} # {name: [file_paths]}
        }

    def index_project(self):
        """Escaneia todo o projeto e cria o índice"""
        for root, dirs, files in os.walk(self.project_root):
            # Ignorar diretórios irrelevantes
            if any(p in root for p in [".git", "__pycache__", "node_modules", ".brain", "venv", ".next"]):
                continue

            for file in files:
                if file.endswith(('.py', '.js', '.html', '.css', '.rs', '.go', '.ts')):
                    file_path = Path(root) / file
                    relative_path = os.path.relpath(file_path, self.project_root)
                    self._index_file(file_path, relative_path)
        
        self.save_index()

    def _index_file(self, file_path: Path, relative_path: str):
        """Analisa um arquivo e extrai símbolos"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            
            # Regex simples para símbolos (funções e classes)
            # Python
            symbols = re.findall(r'(?:def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
            # JS
            symbols += re.findall(r'(?:function|class|const|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:=]', content)

            self.index["files"][relative_path] = {
                "size": file_path.stat().st_size,
                "symbols": list(set(symbols)),
                "summary": content[:500] # Opcional: resumo curto
            }

            for sym in symbols:
                if sym not in self.index["symbols"]:
                    self.index["symbols"][sym] = []
                if relative_path not in self.index["symbols"][sym]:
                    self.index["symbols"][sym].append(relative_path)

        except Exception as e:
            print(f"Erro ao indexar {relative_path}: {e}")

    def search_symbols(self, query: str) -> List[str]:
        """Busca arquivos que contêm o símbolo"""
        return self.index["symbols"].get(query, [])

    def search_keyword(self, keyword: str) -> List[str]:
        """Busca arquivos que contêm uma palavra-chave no nome ou símbolos"""
        results = []
        for path, data in self.index["files"].items():
            if keyword.lower() in path.lower() or any(keyword.lower() in sym.lower() for sym in data["symbols"]):
                results.append(path)
        return results

    def save_index(self):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2)

    def load_index(self):
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
