#!/usr/bin/env python3
"""
Launcher para o AI Coding Assistant
"""

import sys
import os
from pathlib import Path
import subprocess

# Adicionar backend ao path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def check_requirements():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    requirements_file = backend_path / "requirements.txt"
    
    try:
        import fastapi
        import uvicorn
        print("✅ Dependências OK")
        return True
    except ImportError:
        print("❌ Dependências faltando!")
        print(f"\n📦 Instale as dependências com:")
        print(f"   pip install -r {requirements_file}")
        return False


def check_api_keys():
    """Verifica se as API keys estão configuradas"""
    print("\n🔑 Verificando API keys...")
    
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado")
        print("   Copie .env.example para .env e adicione suas keys")
        print("\n💡 Você pode usar Gemini (gratuito) ou Ollama (local)")
        return False
    
    # Verificar se tem pelo menos uma key
    with open(env_file) as f:
        content = f.read()
        if "your_" in content:
            print("⚠️  API keys não parecem estar configuradas")
            print("   Edite o arquivo .env e adicione suas keys")
            return False
    
    print("✅ API keys configuradas")
    return True


def start_server():
    """Inicia o servidor"""
    print("\n🚀 Iniciando AI Coding Assistant...")
    print("=" * 60)
    
    # Importar e iniciar
    try:
        from backend.main import main
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor encerrado")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Função principal"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         🤖 AI CODING ASSISTANT - v1.0.0                  ║
║         Assistente de IA Customizável                    ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # if not check_requirements():
    #     return
    
    # check_api_keys()
    
    print("\n" + "=" * 60)
    start_server()


if __name__ == "__main__":
    main()
