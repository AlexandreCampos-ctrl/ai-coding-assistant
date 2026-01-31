"""
Ferramentas de operações de arquivo
"""

from pathlib import Path
from typing import List, Dict


def read_file(path: str) -> str:
    """Lê o conteúdo de um arquivo"""
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"Erro: Arquivo '{path}' não existe"
        
        content = file_path.read_text(encoding='utf-8')
        return content
    
    except Exception as e:
        return f"Erro ao ler arquivo: {str(e)}"


def write_file(path: str, content: str) -> str:
    """Escreve conteúdo em um arquivo"""
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return f"Arquivo '{path}' criado com sucesso"
    
    except Exception as e:
        return f"Erro ao escrever arquivo: {str(e)}"


def list_files(path: str = ".") -> str:
    """Lista arquivos em um diretório"""
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return f"Erro: Diretório '{path}' não existe"
        
        if not dir_path.is_dir():
            return f"Erro: '{path}' não é um diretório"
        
        files = []
        for item in sorted(dir_path.iterdir()):
            if item.is_file():
                files.append(f"📄 {item.name}")
            else:
                files.append(f"📁 {item.name}/")
        
        return "\n".join(files) if files else "Diretório vazio"
    
    except Exception as e:
        return f"Erro ao listar arquivos: {str(e)}"


def create_directory(path: str) -> str:
    """Cria um novo diretório"""
    try:
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return f"Diretório '{path}' criado com sucesso"
    
    except Exception as e:
        return f"Erro ao criar diretório: {str(e)}"


def delete_file(path: str) -> str:
    """Deleta um arquivo"""
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"Erro: Arquivo '{path}' não existe"
        
        file_path.unlink()
        return f"Arquivo '{path}' deletado com sucesso"
    
    except Exception as e:
        return f"Erro ao deletar arquivo: {str(e)}"
