// HS Chatbot JavaScript Application

class HSChatbot {
    constructor() {
        this.socket = null;
        this.isTyping = false;
        this.typingTimeout = null;
        this.messageContainer = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.connectionStatus = document.getElementById('connection-status');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.onlineIndicator = document.getElementById('online-indicator');
        
        this.initializeSocketIO();
        this.setupEventListeners();
        // this.loadPopularProducts(); // Fonction supprimée
    }

    initializeSocketIO() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.updateConnectionStatus('connected');
            console.log('Connected to server');
        });

        this.socket.on('disconnect', () => {
            this.updateConnectionStatus('disconnected');
            console.log('Disconnected from server');
        });

        this.socket.on('message', (data) => {
            if (data.type === 'human_contact' || data.type === 'human_contact_offer') {
                this.displayHumanContactMessage(data);
            } else {
                this.displayMessage(data.content, 'assistant', data.timestamp);
            }
            this.hideTypingIndicator();
        });

        this.socket.on('suggestions', (data) => {
            this.displaySuggestions(data.products);
        });

        this.socket.on('error', (data) => {
            this.showError(data.message);
        });

        this.socket.on('typing_status', (data) => {
            if (data.typing) {
                this.showTypingIndicator();
            } else {
                this.hideTypingIndicator();
            }
        });
    }
    
    displayHumanContactMessage(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        
        const time = data.timestamp ? new Date(data.timestamp) : new Date();
        const timeString = time.toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        let htmlContent = '';
        
        if (data.type === 'human_contact') {
            // Message pour la redirection directe vers WhatsApp
            htmlContent = `
                <div class="message-bubble">
                    <div class="human-contact-message">
                        <h6><i class="fas fa-headset me-2"></i>Contact avec un conseiller</h6>
                        <p>${data.content}</p>
                        <div class="human-contact-actions">
                            <a href="${data.whatsapp_link}" target="_blank" class="whatsapp-contact-btn">
                                <i class="fab fa-whatsapp"></i>
                                Discuter sur WhatsApp
                            </a>
                            <a href="tel:${data.phone_number}" class="btn btn-outline-secondary">
                                <i class="fas fa-phone-alt me-2"></i>
                                Appeler
                            </a>
                        </div>
                    </div>
                </div>
                <div class="message-time">${timeString}</div>
            `;
        } else if (data.type === 'human_contact_offer') {
            // Message pour l'offre de contact humain
            htmlContent = `
                <div class="message-bubble">
                    <div class="human-contact-message">
                        <h6><i class="fas fa-question-circle me-2"></i>Besoin d'aide supplémentaire ?</h6>
                        <p>${data.content}</p>
                        <div class="human-contact-actions">
                            <a href="${data.whatsapp_link}" target="_blank" class="whatsapp-contact-btn">
                                <i class="fab fa-whatsapp"></i>
                                Oui, contacter un conseiller
                            </a>
                            <button class="btn btn-outline-secondary" onclick="sendQuickMessage('Non merci, continuons la discussion')">
                                <i class="fas fa-robot me-2"></i>
                                Non, continuons
                            </button>
                        </div>
                    </div>
                </div>
                <div class="message-time">${timeString}</div>
            `;
        }
        
        messageDiv.innerHTML = htmlContent;
        this.messageContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    setupEventListeners() {
        // Message input event listeners
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            } else {
                this.handleTyping();
            }
        });

        // La référence au bouton de statistiques a été supprimée

        // Mobile sidebar toggle
        this.setupMobileMenu();
    }

    setupMobileMenu() {
        // Add mobile menu toggle if needed
        if (window.innerWidth <= 768) {
            const navbar = document.querySelector('.navbar');
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'btn btn-outline-light d-md-none';
            toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            toggleBtn.onclick = () => {
                document.querySelector('.sidebar').classList.toggle('show');
            };
            navbar.querySelector('.container').appendChild(toggleBtn);
        }
    }

    updateConnectionStatus(status) {
        const statusElement = this.connectionStatus;
        statusElement.className = `alert connection-status ${status}`;
        
        switch (status) {
            case 'connected':
                statusElement.innerHTML = '<i class="fas fa-check-circle me-2"></i>Connecté';
                statusElement.classList.add('alert-success');
                break;
            case 'disconnected':
                statusElement.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>Déconnecté';
                statusElement.classList.add('alert-danger');
                break;
            case 'connecting':
                statusElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Connexion...';
                statusElement.classList.add('alert-warning');
                break;
        }
    }

    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Display user message
        this.displayMessage(message, 'user');
        
        // Send to server
        this.socket.emit('message', {
            content: message,
            timestamp: new Date().toISOString()
        });

        // Clear input and show typing indicator
        this.messageInput.value = '';
        this.showTypingIndicator();
    }

    displayMessage(content, sender, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const time = timestamp ? new Date(timestamp) : new Date();
        const timeString = time.toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="message-bubble">
                ${this.formatMessageContent(content, sender)}
            </div>
            <div class="message-time">${timeString}</div>
        `;

        this.messageContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessageContent(content, sender) {
        if (sender === 'assistant') {
            // Format assistant messages with better styling
            return this.parseAssistantMessage(content);
        }
        return content;
    }

    parseAssistantMessage(content) {
        // Enhanced message parsing for better display
        let formattedContent = content;
        
        // Convert markdown-style bold
        formattedContent = formattedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert line breaks
        formattedContent = formattedContent.replace(/\n/g, '<br>');
        
        // Highlight prices in MAD
        formattedContent = formattedContent.replace(/(\d+(?:\.\d+)?\s*MAD)/g, '<span class="price">$1</span>');
        
        // Highlight prices in dirhams
        formattedContent = formattedContent.replace(/(\d+(?:\.\d+)?\s*dirhams)/gi, '<span class="price">$1</span>');
        
        // Highlight product names
        formattedContent = formattedContent.replace(/Produit: ([^|]+)/g, '<strong>Produit: $1</strong>');
        
        return formattedContent;
    }

    displaySuggestions(products) {
        if (!products || products.length === 0) return;

        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'message assistant';
        
        let suggestionsHTML = `
            <div class="message-bubble">
                <h6><i class="fas fa-lightbulb me-2"></i>Suggestions de produits</h6>
                <div class="row">
        `;

        products.forEach(product => {
            const metadata = product.metadata || {};
            suggestionsHTML += `
                <div class="col-md-6 mb-3">
                    <div class="product-card">
                        <h6>${metadata.name || 'Produit'}</h6>
                        <p class="small text-muted">${metadata.category || ''}</p>
                        <div class="price">${metadata.price || 0} MAD</div>
                        <span class="price-tier ${metadata.price_tier || 'économique'}">${metadata.price_tier || 'économique'}</span>
                    </div>
                </div>
            `;
        });

        suggestionsHTML += `
                </div>
            </div>
            <div class="message-time">${new Date().toLocaleTimeString('fr-FR', {
                hour: '2-digit',
                minute: '2-digit'
            })}</div>
        `;

        suggestionsDiv.innerHTML = suggestionsHTML;
        this.messageContainer.appendChild(suggestionsDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        // Remove existing typing indicator
        const existingIndicator = this.messageContainer.querySelector('.typing-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        // Add new typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        this.messageContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = this.messageContainer.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    handleTyping() {
        if (!this.isTyping) {
            this.isTyping = true;
            this.socket.emit('typing', { typing: true });
        }

        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
            this.isTyping = false;
            this.socket.emit('typing', { typing: false });
        }, 1000);
    }

    scrollToBottom() {
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        this.messageContainer.appendChild(errorDiv);
        this.scrollToBottom();

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    // La fonction loadPopularProducts a été supprimée

    // La méthode showStatsModal a été supprimée

    getSuggestions(preferences) {
        this.socket.emit('get_suggestions', { preferences });
    }
}

// Global functions for HTML onclick events
function sendQuickMessage(message) {
    chatbot.messageInput.value = message;
    chatbot.sendMessage();
}

function handleEnterKey(event) {
    if (event.key === 'Enter') {
        chatbot.sendMessage();
    }
}

function sendMessage() {
    chatbot.sendMessage();
}

// Initialize the chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new HSChatbot();
});

// Service Worker for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
