"""
Configuração do sistema
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Carrega configuração do arquivo YAML"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    # Configuração padrão
    default_config = {
        'llm': {
            'provider': 'gemini',  # gemini, openai, ollama
            'model': 'gemini-pro',
            'temperature': 0.7,
            'max_tokens': 2000,
            'api_keys': {
                'gemini': '',  # Será preenchido do .env
                'openai': '',
                'anthropic': ''
            }
        },
        'tools': {
            'enabled': [
                'file_operations',
                'code_executor',
                'terminal'
            ]
        },
        'code_execution': {
            'timeout': 30,
            'allowed_libraries': [
                'numpy',
                'pandas',
                'matplotlib',
                'requests'
            ]
        },
        'memory': {
            'max_messages': 50,
            'context_window': 8000
        }
    }
    
    # Tentar carregar do arquivo
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            file_config = yaml.safe_load(f)
            # Merge com default
            default_config.update(file_config)
    
    # Carregar API keys do .env se existir
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key == 'GEMINI_API_KEY':
                        default_config['llm']['api_keys']['gemini'] = value
                    elif key == 'OPENAI_API_KEY':
                        default_config['llm']['api_keys']['openai'] = value
                    elif key == 'ANTHROPIC_API_KEY':
                        default_config['llm']['api_keys']['anthropic'] = value
    
    return default_config


def save_config(config: Dict[str, Any]):
    """Salva configuração no arquivo YAML"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False)
