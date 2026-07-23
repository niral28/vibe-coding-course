/* 
   Wordle Saloon — Frontend Controller 🤠🌵
   =========================================
   Handles grid rendering, virtual keyboard, physical key presses,
   3D tile reveal sequences, typewriter dialogue, and Fetch AJAX requests.
*/

// Game configuration & initial state
const MAX_ROWS = 6;
const MAX_COLS = 5;

let currentRow = 0;
let currentCol = 0;
let currentGuess = [];
let isGameActive = true;
let isLoading = false; // Locks inputs during animations or AI model queries

// Keyboard Layout Configuration
const KEYBOARD_LAYOUT = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "BACK"]
];

// Cache core DOM elements
const gridContainer = document.getElementById("wordle-grid");
const keyboardContainer = document.getElementById("virtual-keyboard");
const sheriffBubble = document.getElementById("sheriff-bubble");
const sheriffText = document.getElementById("sheriff-text");
const errorBanner = document.getElementById("error-banner");
const restartBtn = document.getElementById("btn-restart");
const modalRestartBtn = document.getElementById("btn-modal-restart");
const gameOverModal = document.getElementById("game-over-modal");
const wantedOutcome = document.getElementById("wanted-outcome");
const wantedMessage = document.getElementById("wanted-message");
const wantedAnswer = document.getElementById("wanted-answer");

// ============================================================================
// DYNAMIC COMPONENT CREATION
// ============================================================================

function createGrid() {
    gridContainer.innerHTML = "";
    for (let r = 0; r < MAX_ROWS; r++) {
        const rowDiv = document.createElement("div");
        rowDiv.classList.add("grid-row");
        rowDiv.id = `row-${r}`;

        for (let c = 0; c < MAX_COLS; c++) {
            const tileDiv = document.createElement("div");
            tileDiv.classList.add("tile");
            tileDiv.id = `tile-${r}-${c}`;

            // Create inner structure for 3D flip card effect
            const innerDiv = document.createElement("div");
            innerDiv.classList.add("tile-inner");

            const frontDiv = document.createElement("div");
            frontDiv.classList.add("tile-front");

            const backDiv = document.createElement("div");
            backDiv.classList.add("tile-back");

            innerDiv.appendChild(frontDiv);
            innerDiv.appendChild(backDiv);
            tileDiv.appendChild(innerDiv);
            rowDiv.appendChild(tileDiv);
        }
        gridContainer.appendChild(rowDiv);
    }
}

function createKeyboard() {
    keyboardContainer.innerHTML = "";
    KEYBOARD_LAYOUT.forEach(row => {
        const rowDiv = document.createElement("div");
        rowDiv.classList.add("keyboard-row");

        row.forEach(key => {
            const btn = document.createElement("button");
            btn.classList.add("key-btn");
            btn.textContent = key;
            btn.setAttribute("data-key", key);

            if (key === "ENTER" || key === "BACK") {
                btn.classList.add("large");
            }

            // Virtual keyboard tap listener
            btn.addEventListener("click", () => handleKeyPress(key));
            rowDiv.appendChild(btn);
        });

        keyboardContainer.appendChild(rowDiv);
    });
}

// ============================================================================
// ANIMATIONS & EFFECTS
// ============================================================================

/**
 * Typewriter reveal effect. Displays text character by character
 * for a rugged typewriter dialogue feeling.
 */
let typewriterTimeout = null;
function speakTypewriter(text) {
    // Clear any active typing intervals
    if (typewriterTimeout) {
        clearTimeout(typewriterTimeout);
    }
    
    sheriffText.textContent = "";
    let i = 0;
    
    function typeChar() {
        if (i < text.length) {
            sheriffText.textContent += text.charAt(i);
            i++;
            // Slightly randomized typing speed for realistic mechanical feel
            const speed = text.charAt(i) === '.' || text.charAt(i) === ',' ? 150 : 25 + Math.random() * 20;
            typewriterTimeout = setTimeout(typeChar, speed);
        }
    }
    typeChar();
}

function showError(message) {
    errorBanner.textContent = message;
    errorBanner.classList.add("visible");
    
    // Auto-hide error banner after 3 seconds
    setTimeout(() => {
        errorBanner.classList.remove("visible");
    }, 3000);
}

function shakeRow(rowIdx) {
    const row = document.getElementById(`row-${rowIdx}`);
    if (row) {
        row.classList.add("shake");
        // Remove animation class after completion to allow repeated shakes
        setTimeout(() => row.classList.remove("shake"), 500);
    }
}

// ============================================================================
// GAME CONTROL LOGIC
// ============================================================================

function handleKeyPress(key) {
    if (!isGameActive || isLoading) return;

    if (key === "ENTER" || key === "Enter") {
        submitGuess();
    } else if (key === "BACK" || key === "Backspace") {
        removeLetter();
    } else if (/^[a-zA-Z]$/.test(key) && key.length === 1) {
        insertLetter(key.toUpperCase());
    }
}

function insertLetter(letter) {
    if (currentCol < MAX_COLS) {
        currentGuess.push(letter);
        const tile = document.getElementById(`tile-${currentRow}-${currentCol}`);
        const innerFront = tile.querySelector(".tile-front");
        
        innerFront.textContent = letter;
        tile.classList.add("pop");
        
        // Remove pop class immediately to allow re-trigger on deletes
        setTimeout(() => tile.classList.remove("pop"), 150);
        
        currentCol++;
    }
}

function removeLetter() {
    if (currentCol > 0) {
        currentCol--;
        currentGuess.pop();
        const tile = document.getElementById(`tile-${currentRow}-${currentCol}`);
        const innerFront = tile.querySelector(".tile-front");
        innerFront.textContent = "";
    }
}

async function submitGuess() {
    if (currentCol < MAX_COLS) {
        showError("Whoa partner! That guess ain't 5 letters long yet!");
        shakeRow(currentRow);
        return;
    }

    const guessStr = currentGuess.join("");
    isLoading = true;
    speakTypewriter("Checking with Sheriff Tex... Let's see if your draw hits the mark...");

    try {
        const response = await fetch("/guess", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ guess: guessStr })
        });

        const data = await response.json();

        if (!response.ok) {
            // Re-enable input if error happens (like invalid words)
            showError(data.error || "That word's not allowed on the range!");
            shakeRow(currentRow);
            speakTypewriter("That word's a bit suspect, partner! Pick a real 5-letter word.");
            isLoading = false;
            return;
        }

        // 3D Staggered flip sequences for premium visual feedback
        revealRow(data);

    } catch (err) {
        showError("Goldarnit! The telegraph line cut out.");
        speakTypewriter("Shoot, we lost contact with the range! Try typing that guess again.");
        isLoading = false;
    }
}

function revealRow(data) {
    const feedback = data.feedback;
    const rowIdx = currentRow;

    // Staggered letter reveal loop
    for (let i = 0; i < MAX_COLS; i++) {
        setTimeout(() => {
            const tile = document.getElementById(`tile-${rowIdx}-${i}`);
            const innerBack = tile.querySelector(".tile-back");
            const innerFront = tile.querySelector(".tile-front");
            
            // Set the uppercase letter on the back tile
            innerBack.textContent = feedback[i].letter;
            innerBack.classList.add(feedback[i].status);
            
            // Flip card!
            tile.classList.add("flipped");

            // If we completed revealing the very last tile in the row
            if (i === MAX_COLS - 1) {
                setTimeout(() => {
                    // Update dialogue with Tex's humorous remarks
                    speakTypewriter(data.sheriff_reply);
                    
                    // Colorize virtual keyboard
                    updateKeyboardColors(data.keyboard_status);
                    
                    // Shift play focus to next row
                    currentRow = data.guesses_used;
                    currentCol = 0;
                    currentGuess = [];

                    // Evaluate if the game was won or lost
                    if (data.game_over) {
                        isGameActive = false;
                        showGameOver(data);
                    }
                    
                    isLoading = false; // Release input lock
                }, 400);
            }
        }, i * 250); // 250ms stagger step
    }
}

function updateKeyboardColors(keyboardStatus) {
    for (const [letter, status] of Object.entries(keyboardStatus)) {
        const keyBtn = document.querySelector(`.key-btn[data-key="${letter}"]`);
        if (keyBtn) {
            // Remove previous statuses
            keyBtn.classList.remove("correct", "present", "absent");
            // Add new highest priority status
            keyBtn.classList.add(status);
        }
    }
}

function showGameOver(data) {
    setTimeout(() => {
        wantedAnswer.textContent = data.secret_word;
        
        if (data.game_reason === "WON") {
            wantedOutcome.textContent = "🏆 SAFE CRACKED!";
            wantedOutcome.style.color = "#3e6e47";
            wantedMessage.textContent = `Quick draw! Sheriff Tex tips his dusty hat to you. You cracked the saloon safe in ${data.guesses_used} shots!`;
        } else {
            wantedOutcome.textContent = "💀 OUT OF AMMO!";
            wantedOutcome.style.color = "#a81c07";
            wantedMessage.textContent = "Drat! You ran dry out of bullets. Sheriff Tex took your loot and locked you in the local jailhouses. Practice your draw!";
        }
        
        gameOverModal.classList.add("visible");
    }, 1500); // Small dramatic delay before showing modal
}

async function startNewGame() {
    // Reset states
    currentRow = 0;
    currentCol = 0;
    currentGuess = [];
    isGameActive = true;
    isLoading = true;
    
    gameOverModal.classList.remove("visible");
    createGrid();
    createKeyboard();
    
    speakTypewriter("Preparing the deck, partner... Picking a fresh 5-letter word...");

    try {
        const response = await fetch("/new_game", { method: "POST" });
        const data = await response.json();
        
        speakTypewriter(data.greeting);
        isLoading = false;
    } catch (err) {
        showError("Telegraph line failed to boot a new saloon session!");
        speakTypewriter("Oh, shoot! The sheriff's office is temporarily closed. Hit restart to try again.");
        isLoading = false;
    }
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

// Physical Keyboard inputs
document.addEventListener("keydown", (e) => {
    handleKeyPress(e.key);
});

// Control panel button clicks
restartBtn.addEventListener("click", startNewGame);
modalRestartBtn.addEventListener("click", startNewGame);

// Boot game on window load
window.addEventListener("DOMContentLoaded", () => {
    startNewGame();
});
