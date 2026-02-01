/**
 * TerminalDashboard Component - Phase 4
 * Displays real-time terminal output from the AI agent
 */

class TerminalDashboard {
    constructor() {
        this.container = document.getElementById('terminal-content');
        this.dashboard = document.getElementById('terminal-dashboard');
        this.isVisible = false;
    }

    appendLine(text, type = 'stdout') {
        if (!this.container) return;

        // Mostrar dashboard ao receber dados se estiver escondido
        if (!this.isVisible) this.show();

        const div = document.createElement('div');
        div.className = `terminal-line terminal-${type}`;
        div.textContent = text;

        this.container.appendChild(div);
        this.container.scrollTop = this.container.scrollHeight;
    }

    logToolCall(name, args) {
        this.appendLine(`\n> EXECUTANDO: ${name}`, 'command');
        if (args && Object.keys(args).length > 0) {
            this.appendLine(`  Args: ${JSON.stringify(args)}`, 'system');
        }
    }

    logToolResult(name, result) {
        this.appendLine(`> RESULTADO [${name}]:`, 'system');
        this.appendLine(result, 'stdout');
    }

    clear() {
        if (this.container) this.container.innerHTML = '';
    }

    show() {
        this.dashboard.classList.add('visible');
        this.isVisible = true;
    }

    hide() {
        this.dashboard.classList.remove('visible');
        this.isVisible = false;
    }
}

// Inicializar globalmente
window.terminalDashboard = new TerminalDashboard();
