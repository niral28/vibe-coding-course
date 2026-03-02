class WebAgent {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.currentStream = null;
        
        this.initializeElements();
        this.bindEvents();
        this.enableInput();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeElements() {
        this.elements = {
            queryInput: document.getElementById('query-input'),
            sendBtn: document.getElementById('send-btn'),
            voiceBtn: document.getElementById('voice-btn'),
            messages: document.getElementById('chat-messages'),
            loading: document.getElementById('loading'),
            voiceIndicator: document.getElementById('voice-indicator'),
            sessionList: document.getElementById('session-list'),
            newChatBtn: document.getElementById('new-chat-btn'),
            responseAudio: document.getElementById('response-audio')
        };
    }

    bindEvents() {
        // Text input events
        this.elements.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        this.elements.sendBtn.addEventListener('click', () => {
            this.handleSendMessage();
        });

        // Voice recording events
        this.elements.voiceBtn.addEventListener('mousedown', (e) => {
            e.preventDefault();
            this.startRecording();
        });

        this.elements.voiceBtn.addEventListener('mouseup', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        this.elements.voiceBtn.addEventListener('mouseleave', (e) => {
            if (this.isRecording) {
                this.stopRecording();
            }
        });

        // Touch events for mobile
        this.elements.voiceBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });

        this.elements.voiceBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        // New chat button
        this.elements.newChatBtn.addEventListener('click', () => {
            this.startNewChat();
        });
    }

    enableInput() {
        this.elements.queryInput.disabled = false;
        this.elements.sendBtn.disabled = false;
        this.elements.queryInput.placeholder = "Ask me anything...";
    }

    async handleSendMessage() {
        const query = this.elements.queryInput.value.trim();
        if (!query) return;

        // Clear input and disable while processing
        this.elements.queryInput.value = '';
        this.setLoading(true);

        // Add user message to UI
        this.addMessage('user', query);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (data.success) {
                // Display all conversation turns
                this.displayConversationTurns(data.messages);
                
                // Play audio response if available
                if (data.answer) {
                    await this.playTextToSpeech(data.answer);
                }
            } else {
                this.addMessage('assistant', `Sorry, I encountered an error: ${data.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('assistant', 'Sorry, I encountered a connection error. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    displayConversationTurns(messages) {
        // Clear existing messages except the initial greeting
        const firstMessage = this.elements.messages.querySelector('.message.assistant');
        this.elements.messages.innerHTML = '';
        if (firstMessage) {
            this.elements.messages.appendChild(firstMessage);
        }

        // Display all messages from the conversation
        for (const message of messages) {
            if (message.role === 'system') continue;
            
            if (message.role === 'user') {
                // Extract just the question part from system-prefixed messages
                let content = message.content;
                const questionMatch = content.match(/the user's question is: (.+)$/);
                if (questionMatch) {
                    content = questionMatch[1];
                }
                this.addMessage('user', content);
            } else if (message.role === 'assistant') {
                if (message.content && message.content.trim()) {
                    this.addMessage('assistant', message.content);
                }
                
                // Show tool calls if any
                if (message.tool_calls) {
                    for (const toolCall of message.tool_calls) {
                        const args = JSON.parse(toolCall.function.arguments);
                        if (toolCall.function.name === 'encyclopedia_search') {
                            this.addMessage('tool', `🔍 Searching Wikipedia for: "${args.query}"`);
                        }
                    }
                }
            } else if (message.role === 'tool') {
                if (message.name === 'encyclopedia_search') {
                    // Parse the search results
                    const content = message.content;
                    const resultsMatch = content.match(/Results: (.+)$/);
                    if (resultsMatch) {
                        try {
                            const results = JSON.parse(resultsMatch[1]);
                            if (results.success) {
                                this.addMessage('tool', `📚 Found information: ${results.answer.substring(0, 200)}${results.answer.length > 200 ? '...' : ''}`);
                            }
                        } catch (e) {
                            this.addMessage('tool', `📚 Search completed`);
                        }
                    }
                } else if (message.name === 'answer_question') {
                    const answer = message.content.replace('Encyclopedia answer: ', '');
                    this.addMessage('assistant', answer);
                }
            }
        }
        
        this.scrollToBottom();
    }

    async startRecording() {
        if (this.isRecording) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.currentStream = stream;
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.handleRecordingStop();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Update UI
            this.elements.voiceBtn.classList.add('recording');
            this.elements.voiceIndicator.innerHTML = '<i class="fas fa-microphone"></i><span>Recording... Release to stop</span>';
            this.elements.voiceIndicator.classList.add('recording');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Could not access microphone. Please check your permissions.');
        }
    }

    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;
        
        this.mediaRecorder.stop();
        this.isRecording = false;
        
        // Stop all tracks
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }
        
        // Update UI
        this.elements.voiceBtn.classList.remove('recording');
        this.elements.voiceIndicator.innerHTML = '<i class="fas fa-microphone-slash"></i><span>Processing voice...</span>';
        this.elements.voiceIndicator.classList.remove('recording');
    }

    async handleRecordingStop() {
        if (this.audioChunks.length === 0) {
            this.elements.voiceIndicator.innerHTML = '<i class="fas fa-microphone-slash"></i><span>No audio recorded</span>';
            return;
        }

        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        try {
            this.setLoading(true);
            
            const response = await fetch('/api/voice-to-text', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success && data.text.trim()) {
                // Set the transcribed text in the input
                this.elements.queryInput.value = data.text;
                this.elements.voiceIndicator.innerHTML = '<i class="fas fa-check"></i><span>Voice processed successfully</span>';
                
                // Automatically send the message
                setTimeout(() => {
                    this.handleSendMessage();
                }, 500);
            } else {
                this.elements.voiceIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Could not understand voice</span>';
            }
        } catch (error) {
            console.error('Error processing voice:', error);
            this.elements.voiceIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Voice processing failed</span>';
        } finally {
            this.setLoading(false);
            
            // Reset voice indicator after 3 seconds
            setTimeout(() => {
                this.elements.voiceIndicator.innerHTML = '<i class="fas fa-microphone-slash"></i><span>Hold the microphone button to record</span>';
            }, 3000);
        }
    }

    async playTextToSpeech(text) {
        try {
            const response = await fetch('/api/text-to-speech', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                this.elements.responseAudio.src = audioUrl;
                this.elements.responseAudio.play();
            }
        } catch (error) {
            console.error('Error playing text-to-speech:', error);
            // Silently fail for TTS errors
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        let avatar = '🤖';
        if (role === 'user') avatar = '👤';
        else if (role === 'tool') avatar = '🔧';
        
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="content">
                <div class="text">${this.formatMessage(content)}</div>
                <div class="timestamp">${timestamp}</div>
            </div>
        `;
        
        this.elements.messages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Basic formatting for URLs and line breaks
        return content
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    }

    scrollToBottom() {
        this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
    }

    setLoading(loading) {
        this.elements.loading.style.display = loading ? 'flex' : 'none';
        this.elements.sendBtn.disabled = loading;
        this.elements.queryInput.disabled = loading;
        
        if (loading) {
            this.elements.queryInput.placeholder = "Searching encyclopedia...";
        } else {
            this.elements.queryInput.placeholder = "Ask me anything...";
        }
    }

    startNewChat() {
        this.sessionId = this.generateSessionId();
        
        // Clear messages except initial greeting
        const firstMessage = this.elements.messages.querySelector('.message.assistant');
        this.elements.messages.innerHTML = '';
        if (firstMessage) {
            this.elements.messages.appendChild(firstMessage);
        }
        
        // Clear input
        this.elements.queryInput.value = '';
        this.setLoading(false);
    }
}

// Initialize the web agent when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new WebAgent();
});