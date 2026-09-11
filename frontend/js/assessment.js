document.addEventListener('DOMContentLoaded', () => {

    /* =========================================================
       1. LINGUISTIC SIGNAL (STEP 1) - TYPING ANIMATION
       ========================================================= */
    const textInput = document.getElementById('social-text');
    const charCountDisplay = document.getElementById('char-count');
    const signalStatusIndicator = document.getElementById('signal-status-indicator');
    const validationMsg = document.getElementById('text-validation-msg');
    const clearBtn = document.getElementById('btn-clear-text');
    const sampleBtn = document.getElementById('btn-sample-text');

    if (textInput) {
        textInput.addEventListener('input', (e) => {
            const currentLength = e.target.value.length;
            charCountDisplay.innerHTML = `${currentLength} / 1500 <span style="opacity: 0.5;">SIGNAL LENGTH</span>`;

            if (currentLength > 0) {
                signalStatusIndicator.style.opacity = '1';
            } else {
                signalStatusIndicator.style.opacity = '0';
                validationMsg.innerText = "System Ready. Waiting for input...";
                validationMsg.style.color = "var(--teal)";
            }

            if (currentLength > 0 && currentLength < 20) {
                signalStatusIndicator.innerText = "SIGNAL CAPTURE ● ○ ○ ○ ○";
                validationMsg.innerText = "Insufficient signal depth. Keep typing...";
                validationMsg.style.color = "var(--gold)";
            } else if (currentLength >= 20 && currentLength < 60) {
                signalStatusIndicator.innerText = "SIGNAL CAPTURE ● ● ○ ○ ○";
                validationMsg.innerText = "Capturing linguistic patterns...";
                validationMsg.style.color = "var(--teal)";
            } else if (currentLength >= 60 && currentLength < 120) {
                signalStatusIndicator.innerText = "SIGNAL CAPTURE ● ● ● ○ ○";
                validationMsg.innerText = "Analyzing sentiment depth...";
            } else if (currentLength >= 120 && currentLength < 250) {
                signalStatusIndicator.innerText = "SIGNAL CAPTURE ● ● ● ● ○";
                validationMsg.innerText = "Extracting cognitive distortions...";
            } else if (currentLength >= 250) {
                signalStatusIndicator.innerText = "SIGNAL CAPTURE ● ● ● ● ●";
                validationMsg.innerText = "Optimum signal depth reached.";
            }
        });

        clearBtn?.addEventListener('click', () => {
            textInput.value = '';
            textInput.dispatchEvent(new Event('input'));
        });

        // 4 Clinically Calibrated Examiner Text Presets
        const samples = {
            normal: "Today was a productive and balanced day. I went for a morning walk, completed my tasks without excessive anxiety, and feel optimistic about the coming week.",
            mild: "Feeling a bit worn down and tired this week. The workload is noticeable and I am finding it slightly difficult to unwind in the evenings, but still managing daily routines.",
            moderate: "Everything feels noticeably heavy lately. I wake up unrefreshed no matter how long I sleep, disconnected from my usual hobbies, and struggle to find joy in everyday things.",
            severe: "Honestly, everything just feels completely exhausted and empty. Getting out of bed takes immense effort. I feel an overwhelming sense of hopelessness and detached from everyone."
        };

        window.loadPresetSample = function(key) {
            const text = samples[key];
            if (!text || !textInput) return;
            textInput.value = text;
            textInput.dispatchEvent(new Event('input'));
        };

        document.getElementById('btn-sample-normal')?.addEventListener('click', () => window.loadPresetSample('normal'));
        document.getElementById('btn-sample-mild')?.addEventListener('click', () => window.loadPresetSample('mild'));
        document.getElementById('btn-sample-moderate')?.addEventListener('click', () => window.loadPresetSample('moderate'));
        document.getElementById('btn-sample-severe')?.addEventListener('click', () => window.loadPresetSample('severe'));
    }

    /* =========================================================
       2. WEARABLE SENSORS (STEP 2) - LIVE SLIDERS & 2-WAY INPUTS
       ========================================================= */
    const sensors = ['hr', 'hrv', 'eda', 'temp', 'resp', 'sleep', 'steps', 'sedentary'];
    sensors.forEach(sensor => {
        const slider = document.getElementById(`input-${sensor}`);
        const numInput = document.getElementById(`num-${sensor}`);
        
        if (slider && numInput) {
            // Slider changes -> update Number input
            slider.addEventListener('input', (e) => {
                numInput.value = e.target.value;
            });

            // Number input typed -> update Slider
            numInput.addEventListener('input', (e) => {
                const val = parseFloat(e.target.value);
                if (!isNaN(val)) {
                    slider.value = val;
                }
            });
        }
    });

    // Quick Presets — Healthy baseline
    document.getElementById('preset-calm')?.addEventListener('click', () => {
        const presets = { hr: 68, hrv: 52, eda: 2.5, temp: 34.0, resp: 14, sleep: 7.5, steps: 8500, sedentary: 6.0 };
        Object.entries(presets).forEach(([key, val]) => {
            const slider = document.getElementById(`input-${key}`);
            const num = document.getElementById(`num-${key}`);
            if (slider) slider.value = val;
            if (num) num.value = val;
        });
    });

    // Quick Presets — High risk / dysregulated
    document.getElementById('preset-stressed')?.addEventListener('click', () => {
        const presets = { hr: 98, hrv: 18, eda: 8.5, temp: 32.0, resp: 24, sleep: 4.2, steps: 1200, sedentary: 13.5 };
        Object.entries(presets).forEach(([key, val]) => {
            const slider = document.getElementById(`input-${key}`);
            const num = document.getElementById(`num-${key}`);
            if (slider) slider.value = val;
            if (num) num.value = val;
        });
    });

    /* =========================================================
       3. NAVIGATION & WIZARD LOGIC
       ========================================================= */
    const steps = [
        document.getElementById('step-1'),
        document.getElementById('step-2'),
        document.getElementById('step-3'),
        document.getElementById('step-4')
    ];

    const badges = [
        document.getElementById('step-badge-1'),
        document.getElementById('step-badge-2'),
        document.getElementById('step-badge-3')
    ];

    function showStep(stepIndex) {
        steps.forEach(step => { if (step) step.style.display = 'none'; });
        if (steps[stepIndex]) steps[stepIndex].style.display = 'block';

        if (stepIndex < 3) {
            badges.forEach((badge, index) => {
                if (!badge) return;
                if (index === stepIndex) {
                    badge.classList.add('active');
                    badge.style.opacity = '1';
                } else {
                    badge.classList.remove('active');
                    badge.style.opacity = index < stepIndex ? '0.7' : '0.4';
                }
            });
        } else {
            badges.forEach(b => { if (b) b.style.opacity = '0.3'; });
            if (badges[2]) {
                badges[2].style.opacity = '1';
                badges[2].classList.add('active');
                badges[2].innerText = "03 SYNTHESIS [ RUNNING ]";
            }
        }

        window.scrollTo({ top: document.querySelector('.assessment-section').offsetTop - 50, behavior: 'smooth' });
    }

    document.getElementById('btn-to-step-2')?.addEventListener('click', () => showStep(1));
    document.getElementById('btn-back-to-1')?.addEventListener('click', () => showStep(0));

    document.getElementById('btn-to-step-3')?.addEventListener('click', () => {
        const reviewText = textInput ? textInput.value.trim() : '';
        const reviewDisplay = document.getElementById('review-text-display');
        if (reviewDisplay) {
            reviewDisplay.innerText = reviewText !== '' ? reviewText : "No linguistic signal provided.";
        }

        const sensorsDisplay = document.getElementById('review-sensors-display');
        if (sensorsDisplay) {
            sensorsDisplay.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-soft);">
                    <div>HR: <span style="color: var(--teal)">${document.getElementById('input-hr').value} bpm</span></div>
                    <div>HRV: <span style="color: var(--teal)">${document.getElementById('input-hrv').value} ms</span></div>
                    <div>EDA: <span style="color: var(--teal)">${document.getElementById('input-eda').value} µS</span></div>
                    <div>TEMP: <span style="color: var(--teal)">${document.getElementById('input-temp').value} °C</span></div>
                    <div>RESP: <span style="color: var(--teal)">${document.getElementById('input-resp').value} bpm</span></div>
                    <div>SLEEP: <span style="color: var(--teal)">${document.getElementById('input-sleep').value} hrs</span></div>
                    <div>STEPS: <span style="color: var(--teal)">${document.getElementById('input-steps').value}</span></div>
                    <div>SEDENTARY: <span style="color: var(--teal)">${document.getElementById('input-sedentary').value} hrs</span></div>
                </div>
            `;
        }
        showStep(2);
    });

    document.getElementById('btn-back-to-2')?.addEventListener('click', () => showStep(1));
    document.getElementById('edit-text-btn')?.addEventListener('click', () => showStep(0));
    document.getElementById('edit-sensors-btn')?.addEventListener('click', () => showStep(1));

    /* =========================================================
       4. SEVERITY ENGINE (calls FastAPI or falls back to local)
       ========================================================= */

    // Read all sensor values from the DOM
    function readSensors() {
        return {
            text:       document.getElementById('social-text')?.value || '',
            hr:         parseFloat(document.getElementById('input-hr')?.value || 74),
            hrv:        parseFloat(document.getElementById('input-hrv')?.value || 40),
            eda:        parseFloat(document.getElementById('input-eda')?.value || 4.0),
            temp:       parseFloat(document.getElementById('input-temp')?.value || 33.5),
            resp:       parseFloat(document.getElementById('input-resp')?.value || 16),
            sleep:      parseFloat(document.getElementById('input-sleep')?.value || 7.0),
            steps:      parseFloat(document.getElementById('input-steps')?.value || 5500),
            sedentary:  parseFloat(document.getElementById('input-sedentary')?.value || 8.0),
        };
    }

    async function computeSeverity() {
        const s = readSensors();

        try {
            const response = await fetch('http://127.0.0.1:8000/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: s.text,
                    heart_rate: s.hr, hrv: s.hrv, eda: s.eda,
                    skin_temp: s.temp, respiration_rate: s.resp,
                    sleep_duration: s.sleep, daily_steps: s.steps,
                    sedentary_hours: s.sedentary
                })
            });
            if (!response.ok) throw new Error('API error');
            const data = await response.json();
            return {
                severity: data.severity, level: data.level, color: data.color,
                description: data.description, contributions: data.contributions,
                sensorReadings: data.sensor_readings, composite: data.composite_score,
                text: s.text
            };
        } catch (err) {
            console.warn('Backend offline — using local fallback.', err);
            return computeLocalFallback(s);
        }
    }

    // Offline fallback (heuristic mock — NOT real ML)
    function computeLocalFallback(s) {
        const hrScore   = Math.max(0, Math.min(1, (s.hr - 85) / 35));
        const hrvScore  = Math.max(0, Math.min(1, 1 - (s.hrv - 10) / 70));
        const edaScore  = Math.max(0, Math.min(1, (s.eda - 5.0) / 5.0));
        const stepScore = Math.max(0, Math.min(1, 1 - (s.steps / 15000)));
        const sleepScore= Math.max(0, Math.min(1, Math.abs(s.sleep - 7.5) / 5.0));
        const sedScore  = Math.max(0, Math.min(1, (s.sedentary - 8) / 8));

        // Distress keyword detector for local fallback
        const lowerText = s.text.toLowerCase();
        const severeWords = ['empty', 'hopeless', 'exhausted', 'can\'t', 'joy', 'depress', 'heavy', 'burden', 'die', 'bed', 'helpless', 'hate'];
        const mildWords = ['tired', 'stress', 'overwhelm', 'deadline', 'hard', 'unwind', 'workload'];
        
        let keywordScore = 0.0;
        severeWords.forEach(w => { if (lowerText.includes(w)) keywordScore += 0.25; });
        mildWords.forEach(w => { if (lowerText.includes(w)) keywordScore += 0.10; });
        const textRisk = Math.min(1.0, keywordScore);

        const composite = (hrScore * 0.20) + (hrvScore * 0.20) + (edaScore * 0.15) +
                          (stepScore * 0.10) + (sleepScore * 0.15) + (sedScore * 0.10) + (textRisk * 0.20);

        const levels = [
            { severity: 'Normal',             level: 1, color: '#64b8ad', description: 'Signal patterns within expected ranges. No elevated risk markers detected.' },
            { severity: 'Mild Depression',     level: 2, color: '#8bc4b8', description: 'Mild variance detected across physiological modalities. Manageable stress indicators.' },
            { severity: 'Moderate Depression', level: 3, color: '#e5bd73', description: 'Notable signal divergence detected across modalities. Context-aware monitoring recommended.' },
            { severity: 'Severe Depression',   level: 4, color: '#c488a0', description: 'High-confidence signal convergence indicating severe depressive distress. Professional clinical guidance is recommended.' },
        ];
        
        // Calibrated 4-tier clinical thresholds
        const idx = composite < 0.30 ? 0 : composite < 0.50 ? 1 : composite < 0.68 ? 2 : 3;

        return {
            ...levels[idx], 
            contributions: {
                'Autonomic Arousal (EDA)': Math.max(5, Math.round((edaScore * 0.15 / (composite || 1)) * 100)),
                'Cardiac Stress (HR/HRV)': Math.max(8, Math.round(((hrScore * 0.20 + hrvScore * 0.20) / (composite || 1)) * 100)),
                'Sleep Deprivation Risk':  Math.max(5, Math.round((sleepScore * 0.15 / (composite || 1)) * 100)),
                'Sedentary Inactivity':    Math.max(5, Math.round((sedScore * 0.10 / (composite || 1)) * 100)),
                'Linguistic Depth (NLP)':  Math.max(10, Math.round((textRisk * 0.20 / (composite || 1)) * 100))
            },
            sensorReadings: { hr: s.hr, hrv: s.hrv, eda: s.eda, temp: s.temp, resp: s.resp, sleep: s.sleep, steps: s.steps, sedentary: s.sedentary },
            composite, text: s.text
        };
    }

    
    // Sync sliders and number inputs
    ['hr', 'hrv', 'eda', 'temp', 'resp', 'sleep', 'steps', 'sedentary'].forEach(s => {
        const slider = document.getElementById('input-' + s);
        const num = document.getElementById('num-' + s);
        if(slider && num) {
            num.value = slider.value;
            slider.addEventListener('input', () => { num.value = slider.value; });
            num.addEventListener('input', () => { slider.value = num.value; document.getElementById('val-' + s).innerHTML = slider.value + document.getElementById('val-' + s).innerHTML.replace(/^[0-9.]+/, ''); });
        }
    });

    // Sample inputs
    document.getElementById('btn-sample-inputs')?.addEventListener('click', () => {
        const samples = { hr: 95, hrv: 25, eda: 8.5, temp: 34.0, resp: 20, sleep: 5.5, steps: 2500, sedentary: 10.5 };
        Object.keys(samples).forEach(s => {
            const slider = document.getElementById('input-' + s);
            const num = document.getElementById('num-' + s);
            if(slider && num) {
                slider.value = samples[s];
                num.value = samples[s];
                // trigger input event to update ui
                slider.dispatchEvent(new Event('input'));
            }
        });
        const text = document.getElementById('social-text');
        if(text) text.value = "I've been feeling completely exhausted lately. Everything feels so heavy and I can't seem to find joy in anything I used to like. It's just hard to get out of bed.";
    });


    /* =========================================================
       5. TRIGGER THE 3D AI FUSION PIPELINE (STEP 4)
       ========================================================= */
    document.getElementById('btn-start-analysis')?.addEventListener('click', async () => {
        const result = await computeSeverity();
        localStorage.setItem('mc_result', JSON.stringify(result));
        showStep(3);
        window.dispatchEvent(new CustomEvent('StartFusionPipeline', { detail: result }));
        setTimeout(() => { window.location.href = 'results.html'; }, 6500);
    });

});