"""
ASSISTENTE DE IA CUSTOMIZÁVEL - Backend
Sistema modular de IA para programação com suporte a múltiplos LLMs
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, AsyncGenerator
import uvicorn
import json
import asyncio
from pathlib import Path

# Importações locais
from llm_providers.base_provider import BaseLLMProvider
from llm_providers.gemini_provider import GeminiProvider
from llm_providers.openai_provider import OpenAIProvider
from llm_providers.ollama_provider import OllamaProvider
from tools.tool_registry import ToolRegistry
from memory.conversation_manager import ConversationManager
from config_loader import load_config

# Inicializar FastAPI
app = FastAPI(title="AI Coding Assistant", version="1.0.0")

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração global
config = load_config()

# Gerenciadores
conversation_manager = ConversationManager()
tool_registry = ToolRegistry()

# LLM Provider atual
current_provider: Optional[BaseLLMProvider] = None


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Obtém o provider LLM configurado"""
    global current_provider
    
    provider_name = provider_name or config['llm']['provider']
    
    if current_provider and current_provider.name == provider_name:
        return current_provider
    
    # Criar novo provider
    providers = {
        'gemini': GeminiProvider,
        'openai': OpenAIProvider,
        'ollama': OllamaProvider,
    }
    
    if provider_name not in providers:
        raise ValueError(f"Provider '{provider_name}' não suportado")
    
    current_provider = providers[provider_name](config)
    return current_provider


# Models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    stream: bool = True


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls: List[Dict] = []


class ConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None


# Routes
@app.get("/")
async def root():
    """Serve frontend HTML"""
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding='utf-8'), status_code=200)
    return {"message": "AI Coding Assistant API", "status": "running"}


@app.get("/api/config")
async def get_config():
    """Retorna configuração atual"""
    return {
        "llm": config['llm'],
        "tools": {
            "enabled": list(tool_registry.get_available_tools().keys())
        },
        "status": "running"
    }


@app.post("/api/config")
async def update_config(update: ConfigUpdate):
    """Atualiza configuração"""
    global current_provider
    
    if update.provider:
        config['llm']['provider'] = update.provider
        current_provider = None  # Force reload
    
    if update.model:
        config['llm']['model'] = update.model
    
    if update.temperature is not None:
        config['llm']['temperature'] = update.temperature
    
    return {"status": "updated", "config": config['llm']}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Endpoint de chat (não-streaming)"""
    try:
        # Obter provider
        provider = get_llm_provider()
        
        # Obter histórico
        conversation_id = request.conversation_id or conversation_manager.create_conversation()
        history = conversation_manager.get_messages(conversation_id)
        
        # Adicionar mensagem do usuário
        conversation_manager.add_message(conversation_id, "user", request.message)
        
        # Construir mensagens para LLM
        messages = history + [{"role": "user", "content": request.message}]
        
        # Chamar LLM
        response = await provider.generate(messages)
        
        # Processar tool calls (se houver)
        tool_calls = []
        if response.get('tool_calls'):
            for tool_call in response['tool_calls']:
                result = await tool_registry.execute_tool(
                    tool_call['name'],
                    tool_call['arguments']
                )
                tool_calls.append({
                    'name': tool_call['name'],
                    'result': result
                })
        
        # Adicionar resposta ao histórico
        assistant_message = response.get('content', '')
        conversation_manager.add_message(conversation_id, "assistant", assistant_message)
        
        return ChatResponse(
            response=assistant_message,
            conversation_id=conversation_id,
            tool_calls=tool_calls
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket para streaming"""
    await websocket.accept()
    
    try:
        while True:
            # Receber mensagem
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            message = request_data.get('message')
            conversation_id = request_data.get('conversation_id') or conversation_manager.create_conversation()
            
            # Obter provider
            provider = get_llm_provider()
            
            # Obter histórico
            history = conversation_manager.get_messages(conversation_id)
            
            # Adicionar mensagem do usuário
            conversation_manager.add_message(conversation_id, "user", message)
            
            # Construir mensagens
            messages = history + [{"role": "user", "content": message}]
            
            # Stream response
            full_response = ""
            async for chunk in provider.stream_generate(messages):
                full_response += chunk
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk,
                    "conversation_id": conversation_id
                })
            
            # Adicionar resposta completa ao histórico
            conversation_manager.add_message(conversation_id, "assistant", full_response)
            
            # Enviar mensagem de conclusão
            await websocket.send_json({
                "type": "done",
                "conversation_id": conversation_id
            })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


@app.get("/api/conversations")
async def list_conversations():
    """Lista todas as conversas"""
    return conversation_manager.list_conversations()


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Obtém uma conversa específica"""
    messages = conversation_manager.get_messages(conversation_id)
    return {"conversation_id": conversation_id, "messages": messages}


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Deleta uma conversa"""
    conversation_manager.delete_conversation(conversation_id)
    return {"status": "deleted"}


@app.get("/api/tools")
async def list_tools():
    """Lista ferramentas disponíveis"""
    tools = tool_registry.get_available_tools()
    return {
        "tools": [
            {
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for name, tool in tools.items()
        ]
    }


@app.post("/api/tools/{tool_name}")
async def execute_tool_endpoint(tool_name: str, params: Dict):
    """Executa uma ferramenta diretamente"""
    try:
        result = await tool_registry.execute_tool(tool_name, params)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "provider": config['llm']['provider'],
        "model": config['llm']['model']
    }


# Servir arquivos estáticos do frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


def main():
    """Iniciar servidor"""
    print("🚀 Iniciando Assistente de IA Customizável")
    print(f"📡 Provider: {config['llm']['provider']}")
    print(f"🤖 Model: {config['llm']['model']}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
