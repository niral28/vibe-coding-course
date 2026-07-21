/*
  AI Wordle Game Master Frontend JavaScript
  ==========================================
  Coordinates gameplay state, captures physical and virtual keystrokes,
  triggers animations (flipping, bouncing, shaking), handles REST API
  requests to the Flask backend, and renders conversational logs.
*/

document.addEventListener('DOMContentLoaded', () => {
  // --- Game State Constants & Variables ---
  const MAX_ROWS = 6;
  const WORD_LENGTH = 5;
  
  let currentRow = 0;
  let currentLetterIndex = 0;
  let currentGuess = '';
  let isInputLocked = false;
  let isGameOver = false;
  
  // Keep track of evaluated letter keys to update the keyboard colors
  // Values: 'correct' > 'present' > 'absent'
  const keyStateMap = {}; 

  // --- DOM Elements ---
  const grid = document.getElementById('wordle-grid');
  const keyboard = document.getElementById('keyboard');
  const chatBox = document.getElementById('chat-box');
  const typingIndicator = document.getElementById('typing-indicator');
  const toast = document.getElementById('toast-message');
  
  // Modal elements
  const modal = document.getElementById('game-over-modal');
  const modalContent = document.getElementById('modal-content');
  const modalTitle = document.getElementById('modal-title');
  const secretWordDisplay = document.getElementById('secret-word');
  const statGuesses = document.getElementById('stat-guesses');
  const statStatus = document.getElementById('stat-status');
  const btnRestart = document.getElementById('btn-restart');

  // --- Initializer ---
  async function initGame() {
    // Reset state variables
    currentRow = 0;
    currentLetterIndex = 0;
    currentGuess = '';
    isInputLocked = false;
    isGameOver = false;
    
    // Clear key evaluation map
    for (const key in keyStateMap) {
      delete keyStateMap[key];
    }
    
    // Clear letter board grid tiles
    const tiles = document.querySelectorAll('.tile');
    tiles.forEach(tile => {
      tile.textContent = '';
      tile.removeAttribute('data-state');
      tile.style.animation = '';
    });
    
    // Reset virtual keyboard keys
    const keys = document.querySelectorAll('.key');
    keys.forEach(key => {
      key.removeAttribute('data-state');
    });
    
    // Clear chat box except for a clean start
    chatBox.innerHTML = '';
    hideTypingIndicator();
    
    // Hide modal
    modal.style.display = 'none';
    modalContent.className = 'modal-content';
    
    // Show typing indicator, contact server for new game
    showTypingIndicator();
    
    try {
      const response = await fetch('/api/new-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const data = await response.json();
      hideTypingIndicator();
      
      if (data.status === 'success') {
        appendChatBubble('ai', data.ai_message);
      } else {
        appendChatBubble('ai', '⚠️ Error initializing game: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error starting game:', error);
      hideTypingIndicator();
      appendChatBubble('ai', '⚠️ Network error: Could not connect to the game server.');
    }
  }

  // --- Core Gameplay Actions ---

  function handleKeyPress(key) {
    if (isInputLocked || isGameOver) return;
    
    key = key.toUpperCase();
    
    if (key === 'ENTER') {
      submitGuess();
    } else if (key === 'BACKSPACE' || key === 'BACK' || key === '←') {
      handleBackspace();
    } else if (/^[A-Z]$/.test(key)) {
      handleLetterInput(key);
    }
  }

  function handleLetterInput(letter) {
    if (currentLetterIndex >= WORD_LENGTH) return;
    
    const tile = document.getElementById(`tile-${currentRow}-${currentLetterIndex}`);
    tile.textContent = letter;
    tile.setAttribute('data-state', 'tbd'); // 'to be determined' state
    
    currentGuess += letter;
    currentLetterIndex++;
  }

  function handleBackspace() {
    if (currentLetterIndex <= 0) return;
    
    currentLetterIndex--;
    currentGuess = currentGuess.slice(0, -1);
    
    const tile = document.getElementById(`tile-${currentRow}-${currentLetterIndex}`);
    tile.textContent = '';
    tile.removeAttribute('data-state');
  }

  async function submitGuess() {
    if (currentGuess.length < WORD_LENGTH) {
      showToast('Not enough letters');
      shakeRow(currentRow);
      return;
    }
    
    // Lock board during evaluating
    isInputLocked = true;
    showTypingIndicator();
    
    // Add user chat bubble first
    appendChatBubble('user', `My guess is: ${currentGuess}`);
    
    try {
      const response = await fetch('/api/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ guess: currentGuess })
      });
      
      const data = await response.json();
      
      if (response.status !== 200) {
        // Handle server error (e.g. invalid word or network failure)
        hideTypingIndicator();
        showToast(data.error || 'Server error');
        shakeRow(currentRow);
        isInputLocked = false;
        
        // Remove the user bubble since it was invalid
        const lastUserBubble = chatBox.querySelector('.message.user:last-child');
        if (lastUserBubble) lastUserBubble.remove();
        
        return;
      }
      
      // We have successful evaluation! Let's play the visual animations.
      await revealRowColors(currentRow, data.colors);
      
      // Update our keyboard state
      updateKeyboardColors(currentGuess, data.colors);
      
      // Append the AI dialogue
      hideTypingIndicator();
      appendChatBubble('ai', data.ai_message);
      
      // Check for Game Ending conditions
      if (data.game_over) {
        isGameOver = true;
        setTimeout(() => {
          showGameOverModal(data.reason, data.secret_word, data.guesses_used);
        }, 1500); // Give the player a moment to read the AI comment
      } else {
        // Unlock and go to next row
        currentRow++;
        currentLetterIndex = 0;
        currentGuess = '';
        isInputLocked = false;
      }
      
    } catch (error) {
      console.error('Error submitting guess:', error);
      hideTypingIndicator();
      showToast('Network error');
      isInputLocked = false;
    }
  }

  // --- Visuals & Animation Helpers ---

  function revealRowColors(row, colors) {
    return new Promise(resolve => {
      const tiles = Array.from({ length: WORD_LENGTH }, (_, i) => 
        document.getElementById(`tile-${row}-${i}`)
      );
      
      tiles.forEach((tile, i) => {
        // Sequential delayed 3D flip animation
        setTimeout(() => {
          tile.style.animation = 'flipIn 0.5s ease-in-out forwards';
          
          // Midway through the flip (when edge on at 90deg), change colors
          setTimeout(() => {
            tile.setAttribute('data-state', colors[i]);
          }, 250);
          
          // When the last tile is done flipping, resolve the Promise
          if (i === WORD_LENGTH - 1) {
            setTimeout(resolve, 500);
          }
        }, i * 150); // 150ms staggered waterfall delay
      });
    });
  }

  function updateKeyboardColors(guess, colors) {
    for (let i = 0; i < WORD_LENGTH; i++) {
      const char = guess[i];
      const color = colors[i];
      const keyBtn = keyboard.querySelector(`button[data-key="${char}"]`);
      
      if (!keyBtn) continue;
      
      const currentStatus = keyStateMap[char];
      
      // Wordle priority logic: Correct (Green) > Present (Yellow) > Absent (Gray)
      if (color === 'correct') {
        keyStateMap[char] = 'correct';
        keyBtn.setAttribute('data-state', 'correct');
      } else if (color === 'present') {
        if (currentStatus !== 'correct') {
          keyStateMap[char] = 'present';
          keyBtn.setAttribute('data-state', 'present');
        }
      } else if (color === 'absent') {
        if (currentStatus !== 'correct' && currentStatus !== 'present') {
          keyStateMap[char] = 'absent';
          keyBtn.setAttribute('data-state', 'absent');
        }
      }
    }
  }

  function shakeRow(row) {
    const rowEl = document.getElementById(`row-${row}`);
    rowEl.classList.add('shake');
    // Remove the class after animation completes so it can shake again later
    setTimeout(() => {
      rowEl.classList.remove('shake');
    }, 400);
  }

  function showToast(text) {
    toast.textContent = text;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2000);
  }

  // --- Chat Dialogue Helpers ---

  function appendChatBubble(sender, text) {
    const bubble = document.createElement('div');
    bubble.classList.add('message', sender);
    
    // Support basic line breaks from AI dialogue
    const formattedText = text.replace(/\n/g, '<br>');
    bubble.innerHTML = `<p>${formattedText}</p><span class="time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>`;
    
    chatBox.appendChild(bubble);
    
    // Auto-scroll chat window to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
  }

  // --- Modal Helpers ---

  function showGameOverModal(reason, secretWord, guesses) {
    modalTitle.textContent = reason === 'WON' ? '🎉 Spectacular Win!' : '😔 Nice Try!';
    modalContent.className = 'modal-content ' + (reason === 'WON' ? 'won' : 'lost');
    secretWordDisplay.innerHTML = `The secret word was<br><span>${secretWord}</span>`;
    
    statGuesses.textContent = guesses;
    statStatus.textContent = reason === 'WON' ? 'WON' : 'FAILED';
    
    modal.style.display = 'flex';
  }

  // --- Listeners Setup ---

  // Handle virtual on-screen keyboard clicks
  keyboard.addEventListener('click', e => {
    const target = e.target;
    if (target.classList.contains('key')) {
      const key = target.getAttribute('data-key');
      handleKeyPress(key);
    }
  });

  // Handle physical hardware keyboard events
  document.addEventListener('keydown', e => {
    // Ignore keystrokes when typing inside inputs or textareas (if any are added)
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    const key = e.key;
    if (key === 'Enter') {
      handleKeyPress('ENTER');
    } else if (key === 'Backspace') {
      handleKeyPress('BACKSPACE');
    } else if (/^[a-zA-Z]$/.test(key)) {
      handleKeyPress(key.toUpperCase());
    }
  });

  // Handle play again restart request
  btnRestart.addEventListener('click', initGame);

  // --- Bootstrap application ---
  initGame();
});
