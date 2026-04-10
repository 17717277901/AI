/**
 * WorkAI Agent - Web Client
 */

class WorkAIClient {
    constructor() {
        this.ws = null;
        this.connected = false;
        this.messageCount = 0;
        this.toolCallCount = 0;

        // DOM Elements
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.charCount = document.getElementById('charCount');
        this.clearBtn = document.getElementById('clearBtn');
        this.exportBtn = document.getElementById('exportBtn');
        this.messageCountEl = document.getElementById('messageCount');
        this.toolCallCountEl = document.getElementById('toolCallCount');
        this.sessionIdEl = document.getElementById('sessionId');

        this.init();
    }

    init() {
        // Generate session ID
        this.sessionId = this.generateSessionId();
        this.sessionIdEl.textContent = this.sessionId;

        this.connect();
        this.bindEvents();
        this.setupQuickActions();
    }

    generateSessionId() {
        return Math.random().toString(36).substring(2, 8);
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

        try {
            this.ws = new WebSocket(wsUrl);
            this.setupWebSocketHandlers();
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.showError('Failed to connect to server');
        }
    }

    setupWebSocketHandlers() {
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.connected = true;
            this.sendBtn.disabled = false;
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.connected = false;
            this.sendBtn.disabled = true;
            this.showError('Connection lost. Reconnecting...');
            setTimeout(() => this.connect(), 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing message:', error);
            }
        };
    }

    handleMessage(data) {
        const { type, content } = data;

        // Remove loading indicator
        this.removeLoading();

        switch (type) {
            case 'assistant':
                this.addMessage('assistant', content);
                // Count tool calls in response
                const toolMatches = content.match(/\[(\w+)\]/g);
                if (toolMatches) {
                    this.toolCallCount += toolMatches.length;
                    this.updateStats();
                }
                break;
            case 'system':
                this.addMessage('system', content);
                break;
            case 'error':
                this.addMessage('error', content);
                break;
            default:
                console.log('Unknown message type:', type);
        }

        this.scrollToBottom();
    }

    addMessage(role, content) {
        // Remove welcome message if exists
        const welcome = this.messagesContainer.querySelector('.welcome-message');
        if (welcome) {
            welcome.remove();
        }

        const messageEl = document.createElement('div');
        messageEl.className = `message ${role}-message`;

        const bubbleEl = document.createElement('div');
        bubbleEl.className = 'message-bubble';

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.innerHTML = this.formatContent(content);

        bubbleEl.appendChild(contentEl);
        messageEl.appendChild(bubbleEl);
        this.messagesContainer.appendChild(messageEl);

        this.messageCount++;
        this.updateStats();
        this.scrollToBottom();
    }

    formatContent(content) {
        if (!content) return '';

        // Escape HTML first
        let formatted = content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Handle tool results - wrap them in styled div
        // Pattern: [tool_name] Result: ... or [tool_name] Error: ...
        const toolResultRegex = /\[(\w+)\]\s*(Result:|Error:)\s*([\s\S]*?)(?=\[|$)/gi;

        formatted = formatted.replace(toolResultRegex, (match, toolName, status, result) => {
            const statusClass = status === 'Error:' ? 'error' : '';
            // Convert newlines inside result to <br> for display
            const cleanResult = result.trim().replace(/\n/g, '<br>');
            return `<div class="tool-result ${statusClass}">${cleanResult}</div>`;
        });

        // If no tool results were formatted, format newlines normally
        if (!formatted.includes('tool-result')) {
            // Format inline code
            formatted = formatted.replace(
                /`([^`]+)`/g,
                '<code>$1</code>'
            );
            // Format newlines
            formatted = formatted.replace(/\n/g, '<br>');
        }

        return formatted;
    }

    showLoading() {
        // Remove existing loading
        this.removeLoading();

        const messageEl = document.createElement('div');
        messageEl.className = 'message assistant-message loading-message';
        messageEl.id = 'loadingIndicator';

        const bubbleEl = document.createElement('div');
        bubbleEl.className = 'message-bubble';

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.innerHTML = `
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span style="color: var(--text-tertiary)">Thinking...</span>
        `;

        bubbleEl.appendChild(contentEl);
        messageEl.appendChild(bubbleEl);
        this.messagesContainer.appendChild(messageEl);
        this.scrollToBottom();
    }

    removeLoading() {
        const loading = document.getElementById('loadingIndicator');
        if (loading) {
            loading.remove();
        }
    }

    showError(message) {
        this.removeLoading();
        this.addMessage('error', message);
    }

    showSystem(message) {
        this.addMessage('system', message);
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    updateStats() {
        this.messageCountEl.textContent = this.messageCount;
        this.toolCallCountEl.textContent = this.toolCallCount;
    }

    send(message) {
        if (!this.connected) {
            this.showError('Not connected to server');
            return;
        }

        if (!message.trim()) return;

        // Send to server
        this.ws.send(JSON.stringify({ type: 'message', content: message }));

        // Add user message
        this.addUserMessage(message);

        // Clear input
        this.messageInput.value = '';
        this.updateCharCount();
        this.messageInput.style.height = 'auto';
        this.messageInput.focus();
    }

    addUserMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message user-message';

        const bubbleEl = document.createElement('div');
        bubbleEl.className = 'message-bubble';

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.textContent = message;

        bubbleEl.appendChild(contentEl);
        messageEl.appendChild(bubbleEl);
        this.messagesContainer.appendChild(messageEl);

        this.showLoading();
        this.scrollToBottom();
    }

    clearConversation() {
        this.messagesContainer.innerHTML = '';
        this.messageCount = 0;
        this.toolCallCount = 0;
        this.updateStats();

        // Show welcome message
        this.showWelcome();
    }

    showWelcome() {
        const welcomeEl = document.createElement('div');
        welcomeEl.className = 'welcome-message';
        welcomeEl.innerHTML = `
            <div class="welcome-icon">
                <svg viewBox="0 0 48 48" fill="none">
                    <rect width="48" height="48" rx="12" fill="url(#welcomeGradient)"/>
                    <path d="M16 24h16M24 16v16" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                    <defs>
                        <linearGradient id="welcomeGradient" x1="0" y1="0" x2="48" y2="48">
                            <stop stop-color="#6366F1"/>
                            <stop offset="1" stop-color="#8B5CF6"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <h2>Welcome to WorkAI</h2>
            <p>Your intelligent agent with real-time tool access. Try asking about weather or math!</p>
            <div class="quick-actions">
                <button class="quick-action" data-prompt="What's the weather like in Tokyo?">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <circle cx="12" cy="12" r="5"/>
                        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
                    </svg>
                    Tokyo Weather
                </button>
                <button class="quick-action" data-prompt="Calculate sqrt(144) times 7">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <rect x="4" y="2" width="16" height="20" rx="2"/>
                        <line x1="8" y1="6" x2="16" y2="6"/>
                        <line x1="8" y1="10" x2="16" y2="10"/>
                        <line x1="8" y1="14" x2="12" y2="14"/>
                        <line x1="8" y1="18" x2="12" y2="18"/>
                    </svg>
                    Math Expression
                </button>
            </div>
        `;
        this.messagesContainer.appendChild(welcomeEl);
        this.setupQuickActions();
    }

    exportConversation() {
        const messages = this.messagesContainer.querySelectorAll('.message');
        let exportData = 'WorkAI Conversation Export\n';
        exportData += `Session: ${this.sessionId}\n`;
        exportData += `Exported: ${new Date().toISOString()}\n`;
        exportData += '=' .repeat(50) + '\n\n';

        messages.forEach(msg => {
            const role = msg.classList.contains('user-message') ? 'User' :
                         msg.classList.contains('assistant-message') ? 'WorkAI' : 'System';
            const content = msg.querySelector('.message-content')?.textContent || '';
            exportData += `[${role}]\n${content}\n\n`;
        });

        const blob = new Blob([exportData], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `workai-conversation-${this.sessionId}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = count;
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    bindEvents() {
        // Send button
        this.sendBtn.addEventListener('click', () => {
            this.send(this.messageInput.value);
        });

        // Enter key (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.send(this.messageInput.value);
            }
        });

        // Input change
        this.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.autoResizeTextarea();
        });

        // Clear button
        this.clearBtn.addEventListener('click', () => {
            if (confirm('Clear all conversation history?')) {
                this.clearConversation();
                if (this.connected) {
                    this.ws.send(JSON.stringify({ type: 'reset' }));
                }
            }
        });

        // Export button
        this.exportBtn.addEventListener('click', () => {
            this.exportConversation();
        });
    }

    setupQuickActions() {
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', () => {
                const prompt = btn.dataset.prompt;
                this.send(prompt);
            });
        });
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.workAI = new WorkAIClient();
});
