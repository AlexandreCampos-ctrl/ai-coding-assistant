/**
 * AI Coding Assistant - Frontend JavaScript
 */

// Estado global
let currentConversationId = null;
let ws = null;
let isStreaming = false;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 AI Assistant inicializado');
    setupMarked(); // Configurar renderizador
    loadConversations();
    loadConfig();
    connectWebSocket();
});

// Configuração do Marked.js
function setupMarked() {
    const renderer = new marked.Renderer();

    // Renderizador de código para Mermaid
    renderer.code = (code, language) => {
        if (language === 'mermaid') {
            return `<div class="mermaid">${code}</div>`;
        }
        return `<pre><code class="language-${language}">${code}</code></pre>`;
    };

    // Renderizador de blockquote para Alertas GitHub
    renderer.blockquote = (quote) => {
        let type = '';
        if (quote.includes('[!NOTE]')) type = 'note';
        else if (quote.includes('[!TIP]')) type = 'tip';
        else if (quote.includes('[!IMPORTANT]')) type = 'important';
        else if (quote.includes('[!WARNING]')) type = 'warning';
        else if (quote.includes('[!CAUTION]')) type = 'caution';

        if (type) {
            const cleanQuote = quote.replace(`[!${type.toUpperCase()}]`, '');
            return `<blockquote class="alert alert-${type}">${cleanQuote}</blockquote>`;
        }
        return `<blockquote>${quote}</blockquote>`;
    };

    marked.setOptions({ renderer });
}

// WebSocket
function connectWebSocket() {
    const wsUrl = 'ws://localhost:8000/ws/chat';
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        updateStatus('Conectado', true);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'chunk') {
            appendToLastMessage(data.content);
        } else if (data.type === 'tool_call') {
            if (window.terminalDashboard) {
                window.terminalDashboard.logToolCall(data.tool, data.args);
            }
        } else if (data.type === 'tool_result') {
            if (window.terminalDashboard) {
                window.terminalDashboard.logToolResult(data.tool, data.result);
            }
        } else if (data.type === 'done') {
            isStreaming = false;
            Prism.highlightAll();
            // Processar Mermaid após a resposta completa
            mermaid.run({
                nodes: document.querySelectorAll('.mermaid'),
            });
        }
    };

    ws.onclose = () => {
        console.log('❌ WebSocket desconectado');
        updateStatus('Desconectado', false);
        setTimeout(connectWebSocket, 3000);
    };
}

// Enviar mensagem
async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();

    if (!message || isStreaming) return;

    // Limpar input
    input.value = '';

    // Adicionar mensagem do usuário
    addMessage('user', message);

    // Criar resposta da IA
    const assistantMessageDiv = createMessageElement('assistant', '');
    document.getElementById('messages').appendChild(assistantMessageDiv);
    scrollToBottom();

    // Enviar via WebSocket
    isStreaming = true;
    ws.send(JSON.stringify({
        message: message,
        conversation_id: currentConversationId
    }));
}

// Adicionar mensagem
function addMessage(role, content) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = createMessageElement(role, content);
    messagesDiv.appendChild(messageDiv);
    scrollToBottom();
}

// Criar elemento de mensagem
function createMessageElement(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}-message`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (content) {
        const html = marked.parse(content);
        contentDiv.innerHTML = html;
        Prism.highlightAll();
    }

    div.appendChild(avatar);
    div.appendChild(contentDiv);

    return div;
}

// Append to last message (streaming)
function appendToLastMessage(chunk) {
    const messages = document.getElementById('messages');
    const lastMessage = messages.lastElementChild;

    if (lastMessage && lastMessage.classList.contains('assistant-message')) {
        const contentDiv = lastMessage.querySelector('.message-content');
        const currentText = contentDiv.getAttribute('data-raw-text') || '';
        const newText = currentText + chunk;
        contentDiv.setAttribute('data-raw-text', newText);

        const html = marked.parse(newText);
        contentDiv.innerHTML = html;
        scrollToBottom();
    }
}

// Nova conversa
function newChat() {
    currentConversationId = null;
    document.getElementById('messages').innerHTML = '';
    document.getElementById('chat-title').textContent = 'Nova Conversa';
    document.getElementById('user-input').focus();
}

// Carregar conversas
async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        const conversations = await response.json();

        const listDiv = document.getElementById('conversations-list');
        listDiv.innerHTML = '';

        conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            item.textContent = conv.title;
            item.onclick = () => loadConversation(conv.id);
            listDiv.appendChild(item);
        });
    } catch (e) {
        console.error('Erro ao carregar conversas:', e);
    }
}

// Carregar conversa específica
async function loadConversation(id) {
    try {
        const response = await fetch(`/api/conversations/${id}`);
        const data = await response.json();

        currentConversationId = id;
        document.getElementById('messages').innerHTML = '';

        data.messages.forEach(msg => {
            addMessage(msg.role, msg.content);
        });
    } catch (e) {
        console.error('Erro ao carregar conversa:', e);
    }
}

// Carregar configuração
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        document.getElementById('provider-select').value = config.llm.provider;
        document.getElementById('temperature').value = config.llm.temperature;
        document.getElementById('temp-value').textContent = config.llm.temperature;
    } catch (e) {
        console.error('Erro ao carregar config:', e);
    }
}

// Atualizar provider
async function updateProvider() {
    const provider = document.getElementById('provider-select').value;

    try {
        await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider })
        });

        console.log(`✅ Provider alterado para ${provider}`);
    } catch (e) {
        console.error('Erro ao atualizar provider:', e);
    }
}

// Atualizar temperature
async function updateTemperature() {
    const temperature = parseFloat(document.getElementById('temperature').value);
    document.getElementById('temp-value').textContent = temperature.toFixed(1);

    try {
        await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ temperature })
        });
    } catch (e) {
        console.error('Erro ao atualizar temperature:', e);
    }
}

// Update status
function updateStatus(text, connected) {
    document.getElementById('status-text').textContent = text;
    const indicator = document.getElementById('status-indicator');
    indicator.style.color = connected ? '#10b981' : '#ef4444';
}

// Handle key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Scroll to bottom
function scrollToBottom() {
    const messages = document.getElementById('messages');
    messages.scrollTop = messages.scrollHeight;
}
