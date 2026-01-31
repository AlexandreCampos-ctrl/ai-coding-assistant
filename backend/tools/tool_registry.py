"""
Sistema de registro e execução de ferramentas
"""

from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass
import asyncio


@dataclass
class Tool:
    """Definição de uma ferramenta"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]


class ToolRegistry:
    """Registro central de ferramentas disponíveis"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_built_in_tools()
    
    def register_tool(self, name: str, description: str, function: Callable, 
                     parameters: Dict[str, Any]):
        """Registra uma nova ferramenta"""
        self.tools[name] = Tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters
        )
    
    def _register_built_in_tools(self):
        """Registra ferramentas built-in"""
        from tools.file_operations import (
            read_file, write_file, list_files, create_directory
        )
        from tools.code_executor import execute_python
        
        # File operations
        self.register_tool(
            "read_file",
            "Lê o conteúdo de um arquivo",
            read_file,
            {
                "path": {
                    "type": "string",
                    "description": "Caminho do arquivo a ler"
                }
            }
        )
        
        self.register_tool(
            "write_file",
            "Escreve conteúdo em um arquivo",
            write_file,
            {
                "path": {
                    "type": "string",
                    "description": "Caminho do arquivo"
                },
                "content": {
                    "type": "string",
                    "description": "Conteúdo a escrever"
                }
            }
        )
        
        self.register_tool(
            "list_files",
            "Lista arquivos em um diretório",
            list_files,
            {
                "path": {
                    "type": "string",
                    "description": "Caminho do diretório"
                }
            }
        )
        
        self.register_tool(
            "create_directory",
            "Cria um novo diretório",
            create_directory,
            {
                "path": {
                    "type": "string",
                    "description": "Caminho do diretório a criar"
                }
            }
        )
        
        # Code execution
        self.register_tool(
            "execute_python",
            "Executa código Python em um sandbox",
            execute_python,
            {
                "code": {
                    "type": "string",
                    "description": "Código Python a executar"
                }
            }
        )
    
    def get_available_tools(self) -> Dict[str, Tool]:
        """Retorna todas as ferramentas disponíveis"""
        return self.tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Executa uma ferramenta"""
        if tool_name not in self.tools:
            raise ValueError(f"Ferramenta '{tool_name}' não encontrada")
        
        tool = self.tools[tool_name]
        
        # Executar função (pode ser async ou sync)
        if asyncio.iscoroutinefunction(tool.function):
            result = await tool.function(**parameters)
        else:
            result = tool.function(**parameters)
        
        return result
    
    def get_tools_for_llm(self) -> list:
        """Retorna ferramentas no formato para LLMs (function calling)"""
        tools_spec = []
        
        for tool in self.tools.values():
            tools_spec.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.parameters,
                        "required": list(tool.parameters.keys())
                    }
                }
            })
        
        return tools_spec
