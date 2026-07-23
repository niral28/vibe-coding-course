/* ==========================================================================
   AI MATH TUTOR - FRONTEND JAVASCRIPT APP
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

    // --- State Variables ---
    let currentSessionId = null;
    let currentSessionMode = 'questions';
    let sessionStartTimestamp = null;
    let questionStartTimestamp = null;
    let timeLimitSeconds = null;
    let totalTimerInterval = null;
    let questionTimerInterval = null;
    let isTimeWarningShown = false;

    // --- DOM Elements ---
    const startScreen = document.getElementById('start-screen');
    const quizScreen = document.getElementById('quiz-screen');
    const summaryScreen = document.getElementById('summary-screen');

    const btnStart = document.getElementById('btn-start');
    const btnSubmit = document.getElementById('btn-submit');
    const btnQuit = document.getElementById('btn-quit');
    const btnRestart = document.getElementById('btn-restart');

    const answerForm = document.getElementById('answer-form');
    const answerInput = document.getElementById('answer-input');

    const problemText = document.getElementById('problem-text');
    const quizTopicBadge = document.getElementById('quiz-topic-badge');
    const quizProgressText = document.getElementById('quiz-progress-text');
    const quizLevelText = document.getElementById('quiz-level-text');
    const quizStreakText = document.getElementById('quiz-streak-text');
    const quizTimerText = document.getElementById('quiz-timer-text');
    const quizQtimeText = document.getElementById('quiz-qtime-text');
    const tutorMessage = document.getElementById('tutor-message');
    const timeWarningBanner = document.getElementById('time-warning-banner');

    // --- Level Option Selector ---
    const levelRadios = document.querySelectorAll('input[name="difficulty"]');
    levelRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            document.querySelectorAll('.level-option').forEach(opt => {
                const r = opt.querySelector('input[type="radio"]');
                opt.classList.toggle('selected', r && r.checked);
            });
        });
    });

    // --- Topic Checkbox Selector ---
    const topicCheckboxes = document.querySelectorAll('input[name="topics"]');
    topicCheckboxes.forEach(chk => {
        chk.addEventListener('change', () => {
            // Prevent selecting zero topics
            const checkedCount = document.querySelectorAll('input[name="topics"]:checked').length;
            if (checkedCount === 0) {
                chk.checked = true;
            }

            // Sync visual 'checked' class across topic cards
            topicCheckboxes.forEach(input => {
                const card = input.closest('.topic-checkbox');
                if (card) {
                    card.classList.toggle('checked', input.checked);
                }
            });
        });
    });

    // --- Session Limit Mode Selector (Either / Or) ---
    const modeRadios = document.querySelectorAll('input[name="session_mode"]');
    const selectQuestions = document.getElementById('max-questions');
    const selectTime = document.getElementById('time-limit');

    function updateModeUI() {
        const selectedMode = document.querySelector('input[name="session_mode"]:checked').value;
        document.querySelectorAll('.mode-card').forEach(card => {
            const r = card.querySelector('input[name="session_mode"]');
            card.classList.toggle('selected', r && r.checked);
        });

        if (selectedMode === 'questions') {
            selectQuestions.disabled = false;
            selectTime.disabled = true;
        } else {
            selectQuestions.disabled = true;
            selectTime.disabled = false;
        }
    }

    modeRadios.forEach(radio => {
        radio.addEventListener('change', updateModeUI);
    });

    document.querySelectorAll('.mode-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.tagName === 'SELECT' || e.target.tagName === 'OPTION') return;
            const r = card.querySelector('input[name="session_mode"]');
            if (r && !r.checked) {
                r.checked = true;
                updateModeUI();
            }
        });
    });

    // =========================================================================
    // SCREEN 1 -> SCREEN 2: START SESSION
    // =========================================================================
    btnStart.addEventListener('click', async () => {
        const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
        const topicNodes = document.querySelectorAll('input[name="topics"]:checked');
        const topics = Array.from(topicNodes).map(n => n.value);
        const mode = document.querySelector('input[name="session_mode"]:checked').value;
        const maxQuestions = selectQuestions.value;
        const timeLimitMinutes = selectTime.value;

        btnStart.disabled = true;
        btnStart.innerHTML = 'Starting Session... ⏳';

        try {
            const res = await fetch('/api/start_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    difficulty: parseInt(difficulty),
                    topics: topics,
                    mode: mode,
                    max_questions: parseInt(maxQuestions),
                    time_limit_minutes: parseFloat(timeLimitMinutes)
                })
            });

            const data = await res.json();
            if (data.status === 'success') {
                currentSessionId = data.session_id;
                currentSessionMode = data.mode;
                timeLimitSeconds = data.time_limit_seconds;
                sessionStartTimestamp = Date.now();
                isTimeWarningShown = false;
                timeWarningBanner.classList.add('hidden');

                // Render First Problem
                renderProblem(data.current_problem);
                updateProgress(data.problems_done + 1, data.max_questions, data.level, data.streak, data.mode);

                tutorMessage.innerHTML = `👋 Welcome! I'm your Gemini AI math tutor. Let's solve <strong>${data.current_problem.topic}</strong> together!`;

                // Switch Screen
                switchScreen(startScreen, quizScreen);

                // Start Timers
                startTimers();
                answerInput.value = '';
                answerInput.focus();
            } else {
                alert('Could not start session: ' + data.message);
            }
        } catch (err) {
            console.error(err);
            alert('Error connecting to backend server.');
        } finally {
            btnStart.disabled = false;
            btnStart.innerHTML = 'Start Math Session 🚀';
        }
    });


    // =========================================================================
    // SCREEN 2: TIMERS
    // =========================================================================
    function startTimers() {
        clearInterval(totalTimerInterval);
        clearInterval(questionTimerInterval);

        questionStartTimestamp = Date.now();

        // 1. Total Session Timer
        totalTimerInterval = setInterval(() => {
            const elapsedSec = Math.floor((Date.now() - sessionStartTimestamp) / 1000);

            if (timeLimitSeconds && timeLimitSeconds > 0) {
                const remainingSec = timeLimitSeconds - elapsedSec;
                if (remainingSec <= 0) {
                    quizTimerText.textContent = '00:00';
                    if (!isTimeWarningShown) {
                        isTimeWarningShown = true;
                        timeWarningBanner.classList.remove('hidden');
                    }
                } else {
                    quizTimerText.textContent = formatMMSS(remainingSec);
                }
            } else {
                quizTimerText.textContent = formatMMSS(elapsedSec);
            }
        }, 1000);

        // 2. Question Stopwatch
        questionTimerInterval = setInterval(() => {
            const qSec = Math.floor((Date.now() - questionStartTimestamp) / 1000);
            quizQtimeText.textContent = `${qSec}s`;
        }, 500);
    }

    function resetQuestionStopwatch() {
        questionStartTimestamp = Date.now();
        quizQtimeText.textContent = '0s';
    }

    function formatMMSS(seconds) {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }


    // =========================================================================
    // SUBMIT ANSWER
    // =========================================================================
    answerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userAns = answerInput.value.trim();
        if (!userAns) return;

        btnSubmit.disabled = true;
        btnSubmit.innerHTML = 'Checking... ⌛';

        try {
            const res = await fetch('/api/submit_answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    answer: userAns
                })
            });

            const data = await res.json();

            if (data.status === 'success') {
                // Update AI tutor chat bubble
                tutorMessage.innerHTML = data.ai_reply || 'Nice attempt!';

                if (data.is_correct) {
                    // Confetti animation on correct answer!
                    triggerConfetti();
                    answerInput.value = '';

                    if (data.is_finished) {
                        setTimeout(() => endAndShowSummary(), 1200);
                    } else if (data.next_problem) {
                        renderProblem(data.next_problem);
                        updateProgress(data.problems_done + 1, data.max_questions, data.level, data.streak, currentSessionMode);
                        resetQuestionStopwatch();
                        answerInput.focus();
                    }
                } else if (data.revealed_answer !== null && data.revealed_answer !== undefined) {
                    // Answer revealed after 3 attempts
                    answerInput.value = '';
                    if (data.is_finished) {
                        setTimeout(() => endAndShowSummary(), 1500);
                    } else if (data.next_problem) {
                        renderProblem(data.next_problem);
                        updateProgress(data.problems_done + 1, data.max_questions, data.level, data.streak, currentSessionMode);
                        resetQuestionStopwatch();
                        answerInput.focus();
                    }
                } else {
                    // Incorrect attempt - re-ask same problem with hint
                    answerInput.select();
                }
            } else {
                alert('Error: ' + data.message);
            }

        } catch (err) {
            console.error(err);
            alert('Failed to submit answer.');
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = 'Submit ➔';
        }
    });


    // =========================================================================
    // QUIT SESSION EARLY
    // =========================================================================
    btnQuit.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to stop this practice session?')) return;
        
        try {
            await fetch('/api/end_session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: currentSessionId })
            });
            endAndShowSummary();
        } catch (err) {
            console.error(err);
        }
    });


    // =========================================================================
    // END & SHOW SUMMARY SCREEN
    // =========================================================================
    async function endAndShowSummary() {
        clearInterval(totalTimerInterval);
        clearInterval(questionTimerInterval);

        try {
            const res = await fetch(`/api/session_summary?session_id=${currentSessionId}`);
            const data = await res.json();

            if (data.status === 'success') {
                // Populate metrics
                document.getElementById('metric-accuracy').textContent = `${data.accuracy_pct}%`;
                document.getElementById('metric-counts').textContent = `${data.correct_count} Right / ${data.incorrect_count} Wrong`;
                document.getElementById('metric-total-time').textContent = formatMMSS(Math.floor(data.total_time_seconds));
                document.getElementById('metric-avg-time').textContent = `${data.avg_time_per_question}s`;

                document.getElementById('summary-tutor-text').textContent = data.summary_text;

                // Populate Breakdown Table
                const tbody = document.getElementById('history-table-body');
                tbody.innerHTML = '';

                data.history.forEach((item) => {
                    const tr = document.createElement('tr');
                    const isOk = item.is_correct;
                    tr.innerHTML = `
                        <td><strong>${item.question_num}</strong></td>
                        <td><span class="badge">${item.topic}</span></td>
                        <td><code>${item.problem_text}</code></td>
                        <td>${item.student_answer}</td>
                        <td><code>${item.correct_answer}</code></td>
                        <td><span class="res-pill ${isOk ? 'res-correct' : 'res-wrong'}">${isOk ? '✓ Correct' : '✗ Missed'}</span></td>
                        <td>${item.time_spent_seconds}s</td>
                    `;
                    tbody.appendChild(tr);
                });

                // Celebrate high scores
                if (data.accuracy_pct >= 75 && data.problems_done > 0) {
                    triggerConfetti();
                }

                switchScreen(quizScreen, summaryScreen);
            }
        } catch (err) {
            console.error(err);
            alert('Failed to load session summary.');
        }
    }


    // =========================================================================
    // RESTART
    // =========================================================================
    btnRestart.addEventListener('click', () => {
        switchScreen(summaryScreen, startScreen);
    });


    // --- Helper Functions ---
    function renderProblem(prob) {
        problemText.textContent = prob.text;
        quizTopicBadge.textContent = prob.topic;
    }

    function updateProgress(curr, maxQ, lvl, streak, mode) {
        if (mode === 'time') {
            quizProgressText.textContent = `Problem #${curr} (Speed Run ⏱️)`;
        } else {
            quizProgressText.textContent = `${curr} of ${maxQ}`;
        }
        quizLevelText.textContent = `⭐ ${lvl}`;
        quizStreakText.textContent = `🔥 ${streak}`;
    }

    function switchScreen(from, to) {
        from.classList.remove('active');
        from.classList.add('hidden');
        to.classList.remove('hidden');
        to.classList.add('active');
    }

    function triggerConfetti() {
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 50,
                spread: 60,
                origin: { y: 0.7 }
            });
        }
    }
});
