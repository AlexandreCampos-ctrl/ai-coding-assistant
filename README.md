# 🤖 AI Coding Assistant

> Assistente de IA customizável para programação - Similar ao Antigravity, mas você código tem acesso total ao código!

---

## ✨ Features

- 🤖 **Multi-LLM Support**: OpenAI, Google Gemini, Claude, Ollama (local)
- 💬 **Chat Interativo**: Interface web moderna com streaming
- 🔧 **Sistema de Ferramentas**: Manipulação de arquivos, execução de código
- 🔌 **Extensível**: Sistema de plugins para adicionar capacidades
- 💾 **Memória Persistente**: Histórico de conversas salvo
- 🎨 **UI Moderna**: Dark mode, syntax highlighting, markdown
- 🔒 **Seguro**: Execução de código em sandbox

---

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r backend/requirements.txt
```

### 2. Configurar API Key

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite `.env` e adicione sua API key:
```env
GEMINI_API_KEY=sua_key_aqui
```

> **Opções gratuitas:**
> - **Google Gemini**: Gratuito até certo limite
> - **Ollama**: 100% gratuito e local (privado)

### 3. Iniciar

```bash
python run.py
```

Abra: **http://localhost:8000**

---

## 📦 Estrutura do Projeto

```
ai_assistant/
├── backend/
│   ├── main.py                     # FastAPI app
│   ├── llm_providers/              # Integrações LLM
│   ├── tools/                      # Ferramentas (files, code exec)
│   └── memory/                     # Sistema de memória
├── frontend/
│   ├── index.html                  # Interface web
│   ├── app.js                      # JavaScript
│   └── styles.css                  # CSS
├── config/
│   └── config.yaml                 # Configuração
└── run.py                          # Launcher
```

---

## 🔧 Configuração

### Trocar Provider

Edite `config/config.yaml`:

```yaml
llm:
  provider: gemini  # ou openai, ollama
  model: gemini-pro
  temperature: 0.7
```

Ou pela interface web no painel de configurações!

---

## 🛠️ Uso

### Chat Básico

```
Você: "Explique o que é Python"
IA: "Python é uma linguagem de programação..."
```

### Criar Arquivo

```
Você: "Crie um arquivo hello.py que imprime Hello World"
IA: *cria arquivo via ferramenta file_operations*
```

### Executar Código

```
Você: "Execute: print(2 + 2)"
IA: *executa código e retorna* "4"
```

---

## 🔌 Adicionar Plugins

Crie um arquivo em `plugins/`:

```python
from tools.tool_registry import Tool

class MeuPlugin(Tool):
    def execute(self, param):
        # Seu código aqui
        return resultado
```

Registre no `tool_registry.py` e pronto!

---

## 🤖 Providers Suportados

| Provider | Custo | Velocidade | Setup |
|----------|-------|------------|-------|
| **Gemini** | Grátis (limite) | Rápido | API key |
| **OpenAI** | Pago | Muito rápido | API key |
| **Ollama** | Grátis | Médio | Local install |

---

## 🔒 Segurança

- ✅ Código executado em **sandbox** (RestrictedPython)
- ✅ **Timeout** de 30 segundos
- ✅ **Whitelist** de bibliotecas permitidas
- ✅ Sem acesso ao filesystem fora do projeto

---

## 📝 TODO

- [ ] Function calling para ferramentas
- [ ] RAG (busca em documentos)
- [ ] Voice input
- [ ] Mobile app
- [ ] Docker container

---

## 🤝 Contribuindo

Este é um projeto open-source! Sinta-se à vontade para:
- Adicionar novos providers
- Criar ferramentas
- Melhorar a UI
- Reportar bugs

---

##  Licença

MIT License - Livre para uso e modificação

---

## 🆘 Suporte

**Problemas comuns:**

### "ModuleNotFoundError"
```bash
pip install -r backend/requirements.txt
```

### "API key inválida"
```bash
# Verifique o arquivo .env
cat .env
```

### "Ollama não conecta"
```bash
# Certifique-se que Ollama está rodando
ollama serve
```

---

**Desenvolvido com ❤️ para programadores que querem customizar sua própria IA!** 🚀
