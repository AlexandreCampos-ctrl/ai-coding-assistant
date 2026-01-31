// Componente de Artifacts Panel
class ArtifactsPanel {
    constructor() {
        this.artifacts = [];
        this.conversationId = 'default';
        this.isVisible = false;
    }

    async init() {
        // Criar botão toggle
        this.createToggleButton();

        // Criar painel
        this.createPanel();

        // Carregar artifacts
        await this.loadArtifacts();

        // Poll a cada 5 segundos
        setInterval(() => this.loadArtifacts(), 5000);
    }

    createToggleButton() {
        const button = document.createElement('button');
        button.id = 'artifacts-toggle';
        button.className = 'artifacts-toggle-btn';
        button.innerHTML = '📄 Artifacts';
        button.onclick = () => this.toggle();

        document.body.appendChild(button);
    }

    createPanel() {
        const panel = document.createElement('div');
        panel.id = 'artifacts-panel';
        panel.className = 'artifacts-panel artifacts-panel-hidden';
        panel.innerHTML = `
            <div class="artifacts-header">
                <h2>📄 Artifacts</h2>
                <button class="panel-close" onclick="artifactsPanel.toggle()">✕</button>
            </div>
            <div class="artifacts-content" id="artifacts-list">
                <p class="loading">Carregando...</p>
            </div>
        `;

        document.body.appendChild(panel);
    }

    toggle() {
        this.isVisible = !this.isVisible;
        const panel = document.getElementById('artifacts-panel');

        if (this.isVisible) {
            panel.classList.remove('artifacts-panel-hidden');
            this.loadArtifacts(); // Reload when opening
        } else {
            panel.classList.add('artifacts-panel-hidden');
        }
    }

    async loadArtifacts() {
        try {
            const response = await fetch(`/api/artifacts?conversation_id=${this.conversationId}`);
            const data = await response.json();

            this.artifacts = data.artifacts || [];
            this.render();
        } catch (error) {
            console.error('Error loading artifacts:', error);
        }
    }

    render() {
        const container = document.getElementById('artifacts-list');

        if (!container) return;

        if (this.artifacts.length === 0) {
            container.innerHTML = '<p class="no-artifacts">Nenhum artifact ainda</p>';
            return;
        }

        const html = this.artifacts.map(artifact => this.renderArtifact(artifact)).join('');
        container.innerHTML = html;
    }

    renderArtifact(artifact) {
        const icon = this.getIconForType(artifact.type);
        const date = artifact.updated_at ? new Date(artifact.updated_at).toLocaleString('pt-BR') : '';

        return `
            <div class="artifact-item" onclick="artifactsPanel.viewArtifact('${artifact.name}')">
                <div class="artifact-icon">${icon}</div>
                <div class="artifact-info">
                    <h4>${this.escapeHtml(artifact.name)}</h4>
                    ${artifact.summary ? `<p>${this.escapeHtml(artifact.summary)}</p>` : ''}
                    <span class="artifact-meta">${date}</span>
                </div>
            </div>
        `;
    }

    getIconForType(type) {
        const icons = {
            'task': '📋',
            'implementation_plan': '📝',
            'walkthrough': '📚',
            'other': '📄'
        };
        return icons[type] || '📄';
    }

    async viewArtifact(name) {
        try {
            const response = await fetch(`/api/artifacts/${name}?conversation_id=${this.conversationId}`);
            const data = await response.json();

            // Criar modal para visualização
            this.showArtifactModal(data);
        } catch (error) {
            console.error('Error viewing artifact:', error);
        }
    }

    showArtifactModal(artifact) {
        // Remove modal existente se houver
        const existingModal = document.getElementById('artifact-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'artifact-modal';
        modal.className = 'artifact-modal';
        modal.innerHTML = `
            <div class="artifact-modal-content">
                <div class="artifact-modal-header">
                    <h2>${this.escapeHtml(artifact.name)}</h2>
                    <button onclick="document.getElementById('artifact-modal').remove()">✕</button>
                </div>
                <div class="artifact-modal-body">
                    <pre><code>${this.escapeHtml(artifact.content)}</code></pre>
                </div>
            </div>
        `;

        // Fechar ao clicar fora
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        };

        document.body.appendChild(modal);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Instância global
const artifactsPanel = new ArtifactsPanel();

// Inicializar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => artifactsPanel.init());
} else {
    artifactsPanel.init();
}
