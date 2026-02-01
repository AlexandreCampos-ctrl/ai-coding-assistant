// Componente de Task Progress
class TaskProgress {
    constructor() {
        this.currentTask = null;
        this.container = null;
    }

    init() {
        // Criar container se não existir
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'task-progress-container';
            this.container.className = 'task-progress-hidden glass-panel';
            document.body.appendChild(this.container);
        }

        // Conectar ao WebSocket para receber updates
        this.setupWebSocket();

        // Poll API a cada 2 segundos
        this.startPolling();
    }

    setupWebSocket() {
        // Placeholder para integração com WebSocket existente
        // Será integrado no app.js principal
    }

    async startPolling() {
        setInterval(async () => {
            try {
                const response = await fetch('/api/task/current');
                const data = await response.json();

                if (data && data.name) {
                    this.updateTask(data);
                } else {
                    this.hideTask();
                }
            } catch (error) {
                console.error('Error polling task:', error);
            }
        }, 2000);
    }

    updateTask(task) {
        this.currentTask = task;
        this.render();
        this.show();
    }

    hideTask() {
        if (this.container) {
            this.container.classList.add('task-progress-hidden');
        }
    }

    show() {
        if (this.container) {
            this.container.classList.remove('task-progress-hidden');
        }
    }

    getModeIcon(mode) {
        const icons = {
            'planning': '📝',
            'execution': '⚙️',
            'verification': '✅'
        };
        return icons[mode] || '🔄';
    }

    getModeColor(mode) {
        const colors = {
            'planning': '#3b82f6',    // Blue
            'execution': '#f59e0b',   // Orange
            'verification': '#10b981' // Green
        };
        return colors[mode] || '#6b7280';
    }

    render() {
        if (!this.currentTask || !this.container) return;

        const modeIcon = this.getModeIcon(this.currentTask.mode);
        const modeColor = this.getModeColor(this.currentTask.mode);
        const progress = this.currentTask.progress || 0;

        this.container.innerHTML = `
            <div class="task-progress-card">
                <div class="task-header">
                    <div class="mode-badge" style="background-color: ${modeColor}">
                        <span class="mode-icon">${modeIcon}</span>
                        <span class="mode-text">${this.currentTask.mode.toUpperCase()}</span>
                    </div>
                    <button class="task-close" onclick="taskProgress.hideTask()">✕</button>
                </div>
                
                <div class="task-body">
                    <h3 class="task-name">${this.escapeHtml(this.currentTask.name)}</h3>
                    
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%; background-color: ${modeColor}"></div>
                        </div>
                        <span class="progress-text">${progress}%</span>
                    </div>
                    
                    <p class="task-status">${this.escapeHtml(this.currentTask.status)}</p>
                    
                    ${this.renderSubtasks()}
                </div>
            </div>
        `;
    }

    renderSubtasks() {
        if (!this.currentTask.subtasks || this.currentTask.subtasks.length === 0) {
            return '';
        }

        const subtasksList = this.currentTask.subtasks
            .map(st => `<li>${this.escapeHtml(st)}</li>`)
            .join('');

        return `
            <div class="subtasks">
                <h4>Subtasks:</h4>
                <ul>${subtasksList}</ul>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Instância global
const taskProgress = new TaskProgress();

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => taskProgress.init());
} else {
    taskProgress.init();
}
