class WordleGame {
    constructor() {
        this.gameState = {
            isActive: false,
            currentRow: 0,
            currentGuess: '',
            attempts: 0,
            maxAttempts: 6,
            gameId: null
        };
        
        this.elements = {
            gameStatus: document.getElementById('game-status'),
            gameBoard: document.getElementById('game-board'),
            guessInput: document.getElementById('guess-input'),
            submitButton: document.getElementById('submit-guess'),
            newGameButton: document.getElementById('new-game'),
            hintButton: document.getElementById('hint-button'),
            chatHistory: document.getElementById('chat-history'),
            attemptsRemaining: document.getElementById('attempts-remaining'),
            // Modal elements
            newGameModal: document.getElementById('new-game-modal'),
            gameEndModal: document.getElementById('game-end-modal'),
            confirmNewGame: document.getElementById('confirm-new-game'),
            cancelNewGame: document.getElementById('cancel-new-game'),
            closeNewGameModal: document.getElementById('close-new-game-modal'),
            playAgain: document.getElementById('play-again'),
            endSession: document.getElementById('end-session'),
            gameEndTitle: document.getElementById('game-end-title'),
            gameEndMessage: document.getElementById('game-end-message'),
            finalWord: document.getElementById('final-word'),
            finalAttempts: document.getElementById('final-attempts')
        };
        
        this.initializeEventListeners();
        this.createGameBoard();
        
        // Show new game modal on initial load
        this.showInitialModal();
    }
    
    initializeEventListeners() {
        // Game controls
        this.elements.newGameButton.addEventListener('click', () => this.showNewGameModal());
        this.elements.submitButton.addEventListener('click', () => this.submitGuess());
        this.elements.hintButton.addEventListener('click', () => this.getHint());
        
        // Input handling
        this.elements.guessInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.submitGuess();
            }
        });
        
        this.elements.guessInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/[^a-zA-Z]/g, '').toUpperCase();
            this.updateCurrentGuessDisplay(e.target.value);
        });
        
        // New Game Modal
        this.elements.confirmNewGame.addEventListener('click', () => {
            this.hideNewGameModal();
            this.startNewGame();
        });
        this.elements.cancelNewGame.addEventListener('click', () => this.hideNewGameModal());
        this.elements.closeNewGameModal.addEventListener('click', () => this.hideNewGameModal());
        
        // Game End Modal
        this.elements.playAgain.addEventListener('click', () => {
            this.hideGameEndModal();
            this.startNewGame();
        });
        this.elements.endSession.addEventListener('click', () => this.hideGameEndModal());
        
        // Close modals when clicking outside
        this.elements.newGameModal.addEventListener('click', (e) => {
            if (e.target === this.elements.newGameModal) {
                this.hideNewGameModal();
            }
        });
        
        this.elements.gameEndModal.addEventListener('click', (e) => {
            if (e.target === this.elements.gameEndModal) {
                this.hideGameEndModal();
            }
        });
        
        // ESC key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideNewGameModal();
                this.hideGameEndModal();
            }
        });
    }
    
    createGameBoard() {
        this.elements.gameBoard.innerHTML = '';
        for (let row = 0; row < this.gameState.maxAttempts; row++) {
            const rowElement = document.createElement('div');
            rowElement.className = 'guess-row';
            rowElement.id = `row-${row}`;
            
            for (let col = 0; col < 5; col++) {
                const cell = document.createElement('div');
                cell.className = 'letter-cell';
                cell.id = `cell-${row}-${col}`;
                rowElement.appendChild(cell);
            }
            
            this.elements.gameBoard.appendChild(rowElement);
        }
    }
    
    updateCurrentGuessDisplay(guess) {
        const currentRowElement = document.getElementById(`row-${this.gameState.currentRow}`);
        if (!currentRowElement) return;
        
        const cells = currentRowElement.querySelectorAll('.letter-cell');
        cells.forEach((cell, index) => {
            if (index < guess.length) {
                cell.textContent = guess[index];
                cell.classList.add('filled');
            } else {
                cell.textContent = '';
                cell.classList.remove('filled');
            }
        });
    }
    
    async startNewGame() {
        try {
            this.setLoading(true);
            this.addChatMessage('🎮 Starting new game...', 'system');
            
            const response = await fetch('/api/new_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.gameState.isActive = true;
                this.gameState.currentRow = 0;
                this.gameState.attempts = 0;
                this.gameState.gameId = data.game_id;
                
                this.createGameBoard();
                this.elements.guessInput.disabled = false;
                this.elements.submitButton.disabled = false;
                this.elements.hintButton.disabled = false;
                this.elements.guessInput.focus();
                
                this.updateGameStatus('Game started! Guess the 5-letter word.');
                this.addChatMessage(data.message, 'system');
                
                // Debug: show the word (remove in production)
                if (data.word) {
                    console.log('🎯 Debug - Word of the day:', data.word);
                }
                
                this.updateAttemptsDisplay();
            } else {
                this.updateGameStatus('Failed to start game: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error starting game:', error);
            this.updateGameStatus('Failed to start game. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    async submitGuess() {
        const guess = this.elements.guessInput.value.trim().toUpperCase();
        
        if (!this.gameState.isActive) {
            this.updateGameStatus('Please start a new game first!', 'error');
            return;
        }
        
        if (guess.length !== 5) {
            this.updateGameStatus('Please enter exactly 5 letters!', 'error');
            return;
        }
        
        try {
            this.setLoading(true);
            this.addChatMessage(`👤 Your guess: ${guess}`, 'user');
            
            const response = await fetch('/api/submit_guess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game_id: this.gameState.gameId,
                    guess: guess
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addChatMessage(data.message, 'system');
                
                // Only process valid guesses (with feedback)
                if (data.feedback) {
                    this.updateGuessRow(guess, data.feedback);
                    this.gameState.attempts = data.attempts || this.gameState.attempts + 1;
                    this.gameState.currentRow++;
                    this.updateAttemptsDisplay();
                    
                    if (data.game_over) {
                        this.endGame(data.won, data.answer);
                    } else {
                        this.elements.guessInput.value = '';
                        this.elements.guessInput.focus();
                        this.updateGameStatus(`Attempt ${this.gameState.attempts}/${this.gameState.maxAttempts} completed. Keep trying!`);
                    }
                } else {
                    // Invalid word - don't advance row, allow re-editing
                    this.updateGameStatus('Invalid word! Please try a different 5-letter word.', 'error');
                    this.elements.guessInput.focus();
                    this.elements.guessInput.select(); // Select the text for easy re-editing
                }
            } else {
                this.updateGameStatus('Error: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error submitting guess:', error);
            this.updateGameStatus('Failed to submit guess. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    updateGuessRow(guess, feedback) {
        const rowElement = document.getElementById(`row-${this.gameState.currentRow}`);
        if (!rowElement) return;
        
        const cells = rowElement.querySelectorAll('.letter-cell');
        
        for (let i = 0; i < 5; i++) {
            const cell = cells[i];
            cell.textContent = guess[i];
            cell.classList.remove('filled');
            
            // Map emoji feedback to CSS classes
            if (feedback[i] === '🟩') {
                cell.classList.add('correct');
            } else if (feedback[i] === '🟨') {
                cell.classList.add('present');
            } else if (feedback[i] === '⬜') {
                cell.classList.add('absent');
            }
        }
    }
    
    async getHint() {
        if (!this.gameState.isActive) {
            this.updateGameStatus('Please start a game first!', 'error');
            return;
        }
        
        try {
            this.setLoading(true);
            this.addChatMessage('💡 Requesting hint...', 'user');
            
            const response = await fetch('/api/get_hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game_id: this.gameState.gameId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addChatMessage(data.hint, 'system');
            } else {
                this.updateGameStatus('Failed to get hint: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error getting hint:', error);
            this.updateGameStatus('Failed to get hint. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    endGame(won, answer) {
        this.gameState.isActive = false;
        this.elements.guessInput.disabled = true;
        this.elements.submitButton.disabled = true;
        this.elements.hintButton.disabled = true;
        
        // Show game end modal with results
        this.showGameEndModal(won, answer);
        
        if (won) {
            this.updateGameStatus(`🎉 Congratulations! You guessed the word: ${answer}`, 'success');
        } else {
            this.updateGameStatus(`😔 Game Over! The word was: ${answer}`, 'error');
        }
    }
    
    // Modal Functions
    showNewGameModal() {
        this.elements.newGameModal.classList.add('show');
    }
    
    hideNewGameModal() {
        this.elements.newGameModal.classList.remove('show');
    }
    
    showGameEndModal(won, answer) {
        // Update modal content based on game result
        if (won) {
            this.elements.gameEndTitle.textContent = '🎉 Congratulations!';
            this.elements.gameEndMessage.textContent = 'Amazing! You solved the puzzle!';
        } else {
            this.elements.gameEndTitle.textContent = '😔 Game Over';
            this.elements.gameEndMessage.textContent = 'Better luck next time!';
        }
        
        // Update stats
        this.elements.finalWord.textContent = answer;
        this.elements.finalAttempts.textContent = `${this.gameState.attempts}/${this.gameState.maxAttempts}`;
        
        // Show modal
        this.elements.gameEndModal.classList.add('show');
    }
    
    hideGameEndModal() {
        this.elements.gameEndModal.classList.remove('show');
    }
    
    showInitialModal() {
        // Wait a brief moment for page to fully load, then show modal
        setTimeout(() => {
            this.showNewGameModal();
        }, 500);
    }
    
    updateGameStatus(message, type = '') {
        this.elements.gameStatus.textContent = message;
        this.elements.gameStatus.className = `game-status ${type}`;
    }
    
    addChatMessage(message, type) {
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${type}`;
        
        if (type === 'user') {
            messageElement.innerHTML = `👤 <strong>You:</strong> ${message}`;
        } else {
            messageElement.innerHTML = `🤖 <strong>AI:</strong> ${message}`;
        }
        
        this.elements.chatHistory.appendChild(messageElement);
        this.elements.chatHistory.scrollTop = this.elements.chatHistory.scrollHeight;
    }
    
    updateAttemptsDisplay() {
        this.elements.attemptsRemaining.textContent = `Attempts: ${this.gameState.attempts}/${this.gameState.maxAttempts}`;
    }
    
    setLoading(loading) {
        if (loading) {
            document.body.classList.add('loading');
        } else {
            document.body.classList.remove('loading');
        }
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new WordleGame();
});