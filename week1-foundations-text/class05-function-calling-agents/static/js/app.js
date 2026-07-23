/*
  AI Wordle Game Master Frontend JavaScript
  ==========================================
  Coordinates gameplay state, captures physical and virtual keystrokes,
  triggers animations (flipping, bouncing, shaking), handles REST API
  requests to the Flask backend, and renders conversational logs.
  
  NOW FEATURING:
  - Landing Menu Overlay: Choose Normal, Hard, or AI Mode at start
  - Strict Hard Mode Constraints: Enforces Correct (Green), Present (Yellow),
    and completely forbids Absent (Grey) letters in future guesses.
  - Autonomous AI Mode: Selectable directly from menu; types and solves
    autonomously using honest clue logic.
  - Interactive Canvas Confetti Explosions.
  - Staggered Typewriter Simulator for AI choices.
  - Menu Back Navigation dynamically resetting game states.
*/

document.addEventListener('DOMContentLoaded', () => {
  // --- Game State Constants & Variables ---
  const MAX_ROWS = 6;
  const WORD_LENGTH = 5;
  
  let activeMode = 'normal'; // 'normal' | 'hard' | 'ai'
  let currentRow = 0;
  let currentLetterIndex = 0;
  let currentGuess = '';
  let isInputLocked = false; // Prevents spamming double-submissions
  let isGameOver = false;
  let autoplayTimeoutId = null;
  
  // Hard Mode constraints
  let correctHints = Array(5).fill(null); // stores letter in correct index, e.g. [null, 'R', null, null, null]
  let presentHints = new Set();           // stores set of present characters, e.g. {'A', 'E'}
  let absentLetters = new Set();          // stores set of completely absent characters, e.g. {'T', 'S'}
  
  // Keep track of evaluated letter keys to update the keyboard colors
  const keyStateMap = {}; 

  // --- DOM Elements ---
  const grid = document.getElementById('wordle-grid');
  const keyboard = document.getElementById('keyboard');
  const chatBox = document.getElementById('chat-box');
  const typingIndicator = document.getElementById('typing-indicator');
  const toast = document.getElementById('toast-message');
  
  // Menu Overlay Elements
  const menuOverlay = document.getElementById('menu-overlay');
  const btnModeNormal = document.getElementById('btn-mode-normal');
  const btnModeHard = document.getElementById('btn-mode-hard');
  const btnModeAi = document.getElementById('btn-mode-ai');
  
  // Controls & Active Badges
  const btnChangeMode = document.getElementById('btn-change-mode');
  const currentModeDisplay = document.getElementById('current-mode-display');
  const aiControlCenter = document.getElementById('ai-control-center');
  const btnAiStep = document.getElementById('btn-ai-step');
  const autoplayToggle = document.getElementById('autoplay-toggle');
  
  // Modal elements
  const modal = document.getElementById('game-over-modal');
  const modalContent = document.getElementById('modal-content');
  const modalTitle = document.getElementById('modal-title');
  const secretWordDisplay = document.getElementById('secret-word');
  const statGuesses = document.getElementById('stat-guesses');
  const statStatus = document.getElementById('stat-status');
  const btnRestart = document.getElementById('btn-restart');

  // --- Confetti Canvas Animation System ---
  const confettiCanvas = document.getElementById('confetti-canvas');
  const ctx = confettiCanvas.getContext('2d');
  let confettiActive = false;
  let particles = [];
  const colorsList = ['#2ea043', '#d29922', '#58a6ff', '#ff4a4f', '#ff82b2', '#ffeb3b'];

  function resizeCanvas() {
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
  }

  class Particle {
    constructor() {
      this.x = Math.random() * confettiCanvas.width;
      this.y = Math.random() * confettiCanvas.height - confettiCanvas.height;
      this.r = Math.random() * 6 + 4;
      this.d = Math.random() * confettiCanvas.height;
      this.color = colorsList[Math.floor(Math.random() * colorsList.length)];
      this.tilt = Math.random() * 10 - 5;
      this.tiltAngleIncremental = Math.random() * 0.07 + 0.02;
      this.tiltAngle = 0;
    }

    draw() {
      ctx.beginPath();
      ctx.lineWidth = this.r / 2;
      ctx.strokeStyle = this.color;
      ctx.moveTo(this.x + this.tilt + this.r / 2, this.y);
      ctx.lineTo(this.x + this.tilt, this.y + this.tilt + this.r / 2);
      ctx.stroke();
    }

    update() {
      this.tiltAngle += this.tiltAngleIncremental;
      this.y += (Math.cos(this.d) + 3 + this.r / 2) / 2;
      this.x += Math.sin(this.tiltAngle);
      this.tilt = Math.sin(this.tiltAngle - this.r / 2) * 5;

      if (this.y > confettiCanvas.height) {
        if (confettiActive) {
          this.x = Math.random() * confettiCanvas.width;
          this.y = -20;
          this.tilt = Math.random() * 10 - 5;
        } else {
          return false;
        }
      }
      return true;
    }
  }

  function startConfetti() {
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    particles = [];
    confettiActive = true;
    for (let i = 0; i < 150; i++) {
      particles.push(new Particle());
    }
    animateConfetti();
  }

  function stopConfetti() {
    confettiActive = false;
  }

  function animateConfetti() {
    if (!confettiActive && particles.length === 0) {
      ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
      return;
    }
    ctx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
    particles = particles.filter(p => {
      p.draw();
      return p.update();
    });
    requestAnimationFrame(animateConfetti);
  }

  // --- Menu Launcher ---
  function selectGameMode(mode) {
    activeMode = mode;
    
    // Hide menu screen
    menuOverlay.style.display = 'none';
    
    // Set active badge representation
    if (mode === 'normal') {
      currentModeDisplay.textContent = '👤 Normal Mode';
      currentModeDisplay.className = 'mode-badge-status normal';
    } else if (mode === 'hard') {
      currentModeDisplay.textContent = '⚔️ Hard Mode';
      currentModeDisplay.className = 'mode-badge-status hard';
    } else if (mode === 'ai') {
      currentModeDisplay.textContent = '🤖 AI Mode';
      currentModeDisplay.className = 'mode-badge-status ai';
    }
    
    // Launch game!
    initGame();
  }

  // --- Initializer ---
  async function initGame() {
    // Reset state variables
    currentRow = 0;
    currentLetterIndex = 0;
    currentGuess = '';
    isInputLocked = false;
    isGameOver = false;
    
    // Clear active autoplay timers
    if (autoplayTimeoutId) {
      clearTimeout(autoplayTimeoutId);
      autoplayTimeoutId = null;
    }
    
    // Reset Hard Mode constraints
    correctHints = Array(5).fill(null);
    presentHints.clear();
    absentLetters.clear();
    
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
    
    // Stop confetti if it was running
    stopConfetti();
    
    // Clear chat box except for a clean start
    chatBox.innerHTML = '';
    hideTypingIndicator();
    
    // Hide modal
    modal.style.display = 'none';
    modalContent.className = 'modal-content';
    
    // Show AI Play control bar ONLY if AI Mode is selected
    if (activeMode === 'ai') {
      aiControlCenter.style.display = 'flex';
      btnAiStep.disabled = false;
    } else {
      aiControlCenter.style.display = 'none';
    }
    
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
        
        // If AI Mode is active and Auto-Play is toggled, schedule the first step!
        if (activeMode === 'ai' && autoplayToggle.checked) {
          scheduleNextAiMove();
        }
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
    // Block physical hardware triggers if board is locked, game is over, or AI is currently playing
    if (isInputLocked || isGameOver || activeMode === 'ai') return;
    
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
    
    // --- Hard Mode Constraints Verification ---
    if (activeMode === 'hard') {
      // 1st Rule: Green Clues must be placed in their exact spots
      for (let i = 0; i < WORD_LENGTH; i++) {
        if (correctHints[i] !== null && currentGuess[i] !== correctHints[i]) {
          const ordinal = ["1st", "2nd", "3rd", "4th", "5th"];
          showToast(`${ordinal[i]} letter must be ${correctHints[i]}`);
          shakeRow(currentRow);
          return;
        }
      }
      
      // 2nd Rule: Yellow Clues must exist somewhere in subsequent guesses
      for (const char of presentHints) {
        if (!currentGuess.includes(char)) {
          showToast(`Guess must contain ${char}`);
          shakeRow(currentRow);
          return;
        }
      }

      // 3rd Rule: Completely Grey/Absent letters MUST NOT be used in subsequent guesses
      for (let i = 0; i < WORD_LENGTH; i++) {
        const char = currentGuess[i];
        if (absentLetters.has(char)) {
          showToast(`"${char}" cannot be used (marked absent)`);
          shakeRow(currentRow);
          return;
        }
      }
    }
    
    // Lock board during evaluation
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
        hideTypingIndicator();
        showToast(data.error || 'Server error');
        shakeRow(currentRow);
        isInputLocked = false;
        
        const lastUserBubble = chatBox.querySelector('.message.user:last-child');
        if (lastUserBubble) lastUserBubble.remove();
        return;
      }
      
      await handleEvaluatedGuessResponse(data);
      
    } catch (error) {
      console.error('Error submitting guess:', error);
      hideTypingIndicator();
      showToast('Network error');
      isInputLocked = false;
    }
  }

  // --- Autonomous AI Mode Actions ---

  async function executeAiStep() {
    if (isGameOver || isInputLocked) return;
    
    // Lock controls
    isInputLocked = true;
    btnAiStep.disabled = true;
    showTypingIndicator();
    
    appendChatBubble('ai', "🤖 *I am consulting the database of previous hints and selecting my next move...*");
    
    try {
      const response = await fetch('/api/ai-guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const data = await response.json();
      hideTypingIndicator();
      
      if (response.status !== 200) {
        showToast(data.error || 'AI generation failed');
        btnAiStep.disabled = false;
        isInputLocked = false;
        return;
      }
      
      const word = data.guess;
      
      // Simulate "typing" the AI's selected word onto the grid before flipping!
      await typeAiWordIntoRow(currentRow, word);
      
      // Submit and evaluate
      appendChatBubble('user', `AI guessed: ${word}`);
      await handleEvaluatedGuessResponse(data);
      
      // Schedule next autoplay move if enabled and game is not over
      if (autoplayToggle.checked && !isGameOver) {
        scheduleNextAiMove();
      }
      
    } catch (error) {
      console.error('Error getting AI guess:', error);
      hideTypingIndicator();
      showToast('AI request failed');
      btnAiStep.disabled = false;
      isInputLocked = false;
    }
  }

  function typeAiWordIntoRow(row, word) {
    return new Promise(resolve => {
      let charIndex = 0;
      function typeChar() {
        if (charIndex < word.length) {
          const letter = word[charIndex];
          const tile = document.getElementById(`tile-${row}-${charIndex}`);
          tile.textContent = letter;
          tile.setAttribute('data-state', 'tbd');
          charIndex++;
          setTimeout(typeChar, 180); // Staggered key input pace
        } else {
          setTimeout(resolve, 300); // Wait briefly before starting flip
        }
      }
      typeChar();
    });
  }

  function scheduleNextAiMove() {
    if (autoplayTimeoutId) clearTimeout(autoplayTimeoutId);
    autoplayTimeoutId = setTimeout(() => {
      if (!isGameOver && activeMode === 'ai' && autoplayToggle.checked) {
        executeAiStep();
      }
    }, 2500); // 2.5s delay to let animations complete and bubbles be read
  }

  // Common response-handling block shared by both Player and AI guesses!
  async function handleEvaluatedGuessResponse(data) {
    const guessWord = data.guess;
    
    // We have successful evaluation! Play the visual animations.
    await revealRowColors(currentRow, data.colors);
    
    // Save constraints for Hard Mode on success (Green, Yellow, and Grey/Absent)
    for (let i = 0; i < WORD_LENGTH; i++) {
      const char = guessWord[i];
      if (data.colors[i] === 'correct') {
        correctHints[i] = char;
        absentLetters.delete(char);
      } else if (data.colors[i] === 'present') {
        presentHints.add(char);
        absentLetters.delete(char);
      } else if (data.colors[i] === 'absent') {
        // Only mark completely absent if it is not correct or present in another index (handles double letter edge cases)
        if (!correctHints.includes(char) && !presentHints.has(char)) {
          absentLetters.add(char);
        }
      }
    }
    
    // Update keyboard letters
    updateKeyboardColors(guessWord, data.colors);
    
    // Append conversational response
    hideTypingIndicator();
    appendChatBubble('ai', data.ai_message);
    
    // Check for game completion
    if (data.game_over) {
      isGameOver = true;
      if (autoplayTimeoutId) clearTimeout(autoplayTimeoutId);
      
      if (data.reason === 'WON') {
        startConfetti();
        appendChatBubble('ai', '🎉 CONGRATULATIONS! The Wordle puzzle has been solved! Spectacular! 🏆');
      }
      
      setTimeout(() => {
        showGameOverModal(data.reason, data.secret_word, data.guesses_used);
      }, 1500);
    } else {
      // Advance row
      currentRow++;
      currentLetterIndex = 0;
      currentGuess = '';
      
      // Release visual locks
      isInputLocked = false;
      if (activeMode === 'ai') {
        btnAiStep.disabled = false;
      }
    }
  }

  // --- Visuals & Animation Helpers ---

  function revealRowColors(row, colors) {
    return new Promise(resolve => {
      const tiles = Array.from({ length: WORD_LENGTH }, (_, i) => 
        document.getElementById(`tile-${row}-${i}`)
      );
      
      tiles.forEach((tile, i) => {
        setTimeout(() => {
          tile.style.animation = 'flipIn 0.5s ease-in-out forwards';
          
          setTimeout(() => {
            tile.setAttribute('data-state', colors[i]);
          }, 250);
          
          if (i === WORD_LENGTH - 1) {
            setTimeout(resolve, 500);
          }
        }, i * 150);
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
    setTimeout(() => {
      rowEl.classList.remove('shake');
    }, 400);
  }

  function showToast(text) {
    toast.textContent = text;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2500);
  }

  // --- Chat Dialogue Helpers ---

  function appendChatBubble(sender, text) {
    const bubble = document.createElement('div');
    bubble.classList.add('message', sender);
    
    const formattedText = text.replace(/\n/g, '<br>');
    bubble.innerHTML = `<p>${formattedText}</p><span class="time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>`;
    
    chatBox.appendChild(bubble);
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

  // Menu Mode selections
  btnModeNormal.addEventListener('click', () => selectGameMode('normal'));
  btnModeHard.addEventListener('click', () => selectGameMode('hard'));
  btnModeAi.addEventListener('click', () => selectGameMode('ai'));

  // Go back to Mode selection Menu screen
  btnChangeMode.addEventListener('click', () => {
    // Halt any active autoplay timeouts
    if (autoplayTimeoutId) {
      clearTimeout(autoplayTimeoutId);
      autoplayTimeoutId = null;
    }
    stopConfetti();
    
    // Unveil Menu card
    menuOverlay.style.display = 'flex';
  });

  // Auto-play checkbox listener
  autoplayToggle.addEventListener('change', () => {
    if (autoplayToggle.checked && activeMode === 'ai' && !isGameOver && !isInputLocked) {
      executeAiStep();
    } else if (!autoplayToggle.checked) {
      if (autoplayTimeoutId) {
        clearTimeout(autoplayTimeoutId);
        autoplayTimeoutId = null;
      }
    }
  });

  // AI Step button listener
  btnAiStep.addEventListener('click', executeAiStep);

  // Handle play again restart request
  btnRestart.addEventListener('click', initGame);

  // --- Initial Launch Setup ---
  // Renders the mode overlay immediately and lets user pick!
  menuOverlay.style.display = 'flex';
});
