/* ==========================================================================
   moodcompiler — 3D Multimodal Fusion Pipeline
   "INPUT → SIGNAL PROCESSING → MULTIMODAL FUSION → INSIGHT"

   Architecture:
   - Pure Vanilla Canvas 2D with manual 3D projection (no Three.js)
   - State Machine: IDLE → PROCESSING → OUTPUT
   - Mouse parallax for depth
   - Particle system with bezier-curve flow paths
   ========================================================================== */

(function () {
    'use strict';

    /* ------------------------------------------------------------------
       CONFIG
    ------------------------------------------------------------------ */
    const CFG = {
        TEAL:       '#64b8ad',
        GOLD:       '#e5bd73',
        CREAM:      '#f8f4eb',
        MUTED:      '#82919e',
        VIOLET:     '#8b7eb8',
        PINK:       '#c488a0',

        PARTICLE_SPEED_IDLE: 0.4,
        PARTICLE_SPEED_PROC: 1.6,
        PROCESSING_DURATION: 4200,
        PARALLAX_STRENGTH:   22,
    };

    /* ------------------------------------------------------------------
       STATE
    ------------------------------------------------------------------ */
    let state = 'IDLE';

    /* ------------------------------------------------------------------
       CANVAS
    ------------------------------------------------------------------ */
    let canvas, ctx, W, H, RAF;
    let mouse    = { x: 0, y: 0 };
    let parallax = { x: 0, y: 0 };
    let tick     = 0;

    /* ------------------------------------------------------------------
       LAYOUT (normalized 0-1 coords)
    ------------------------------------------------------------------ */
    const layout = {
        nodeL1: { x: 0.14, y: 0.26 },
        nodeL2: { x: 0.14, y: 0.50 },
        nodeL3: { x: 0.14, y: 0.74 },
        core:   { x: 0.47, y: 0.50 },
        an1:    { x: 0.61, y: 0.36 },
        an2:    { x: 0.67, y: 0.50 },
        an3:    { x: 0.61, y: 0.64 },
        output: { x: 0.82, y: 0.50 },
    };

    /* ------------------------------------------------------------------
       PARTICLES
    ------------------------------------------------------------------ */
    let particles = [];

    class Particle {
        constructor(src, tgt, color, speed) {
            this.src   = src;
            this.tgt   = tgt;
            this.color = color || CFG.TEAL;
            this.speed = speed || CFG.PARTICLE_SPEED_IDLE;
            this.t     = 0;
            this.size  = Math.random() * 2.4 + 1;
            this.alpha = 0;
            this.cpx   = (src.x + tgt.x) / 2 + (Math.random() - 0.5) * 0.10;
            this.cpy   = (src.y + tgt.y) / 2 + (Math.random() - 0.5) * 0.14;
            this.dead  = false;
        }

        update() {
            this.t += this.speed * 0.008;
            if      (this.t < 0.15) this.alpha = this.t / 0.15;
            else if (this.t > 0.78) this.alpha = (1 - this.t) / 0.22;
            else                    this.alpha = 1;
            if (this.t >= 1) this.dead = true;
        }

        getPos() {
            const t = this.t, mt = 1 - t;
            return {
                x: mt * mt * this.src.x + 2 * mt * t * this.cpx + t * t * this.tgt.x,
                y: mt * mt * this.src.y + 2 * mt * t * this.cpy + t * t * this.tgt.y,
            };
        }

        draw() {
            if (this.dead || this.alpha <= 0) return;
            const p  = this.getPos();
            const sx = p.x * W + parallax.x;
            const sy = p.y * H + parallax.y;
            ctx.save();
            ctx.globalAlpha = this.alpha * 0.88;
            ctx.shadowBlur  = 9;
            ctx.shadowColor = this.color;
            ctx.fillStyle   = this.color;
            ctx.beginPath();
            ctx.arc(sx, sy, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    /* ------------------------------------------------------------------
       INPUT NODES
    ------------------------------------------------------------------ */
    const inputNodes = [
        { ...layout.nodeL1, label: 'LINGUISTIC',    sub: 'Text & Language',     color: CFG.TEAL   },
        { ...layout.nodeL2, label: 'PHYSIOLOGICAL', sub: 'Wearable Biosignals', color: CFG.GOLD   },
        { ...layout.nodeL3, label: 'BEHAVIORAL',    sub: 'Activity Patterns',   color: CFG.VIOLET },
    ];

    function sx(nx) { return nx * W + parallax.x; }
    function sy(ny) { return ny * H + parallax.y; }

    function drawInputNode(node, idx) {
        const cx    = sx(node.x);
        const cy    = sy(node.y);
        const pulse = Math.sin(tick * 0.032 + idx * 2.1) * 0.3 + 0.7;
        const r     = state === 'PROCESSING' ? 13 : 10;

        // Glow halo
        const grad = ctx.createRadialGradient(cx, cy, r * 0.5, cx, cy, r * 2.6);
        grad.addColorStop(0, hexA(node.color, 0.30 * pulse));
        grad.addColorStop(1, hexA(node.color, 0));
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(cx, cy, r * 2.6, 0, Math.PI * 2);
        ctx.fill();

        // Core
        ctx.save();
        ctx.shadowBlur  = 18 * pulse;
        ctx.shadowColor = node.color;
        ctx.fillStyle   = hexA(node.color, 0.85);
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // Bright centre
        ctx.fillStyle   = '#fff';
        ctx.globalAlpha = 0.85;
        ctx.beginPath();
        ctx.arc(cx, cy, r * 0.32, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;

        // Label
        ctx.save();
        ctx.textAlign   = 'center';
        ctx.font        = '600 9.5px JetBrains Mono, monospace';
        ctx.fillStyle   = node.color;
        ctx.globalAlpha = 0.9;
        ctx.fillText(node.label, cx, cy - r - 13);
        ctx.font        = '400 8.5px Inter, sans-serif';
        ctx.fillStyle   = CFG.MUTED;
        ctx.globalAlpha = 0.55;
        ctx.fillText(node.sub, cx, cy - r - 4);
        ctx.restore();

        // Orbiting dots
        for (let i = 0; i < 3; i++) {
            const angle = (tick * 0.018 + i * 2.094) * (idx % 2 === 0 ? 1 : -1);
            const oR    = r * 1.9;
            const ox    = cx + Math.cos(angle) * oR;
            const oy    = cy + Math.sin(angle) * oR * 0.52;
            ctx.save();
            ctx.shadowBlur  = 5;
            ctx.shadowColor = node.color;
            ctx.fillStyle   = hexA(node.color, 0.65);
            ctx.beginPath();
            ctx.arc(ox, oy, 2.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    /* ------------------------------------------------------------------
       FUSION CORE
    ------------------------------------------------------------------ */
    function drawFusionCore() {
        const cx    = sx(layout.core.x);
        const cy    = sy(layout.core.y);
        const pulse = Math.sin(tick * 0.022) * 0.18 + 0.82;
        const coreR = state === 'PROCESSING' ? 52 : 42;

        // Deep atmospheric bloom
        const bgG = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreR * 3.5);
        bgG.addColorStop(0,   hexA(CFG.TEAL,   0.13 * pulse));
        bgG.addColorStop(0.5, hexA(CFG.VIOLET, 0.06));
        bgG.addColorStop(1,   'rgba(0,0,0,0)');
        ctx.fillStyle = bgG;
        ctx.beginPath();
        ctx.arc(cx, cy, coreR * 3.5, 0, Math.PI * 2);
        ctx.fill();

        // Orbital rings
        [
            [coreR * 1.85, 0.008, CFG.TEAL,    1],
            [coreR * 2.35, 0.005, CFG.VIOLET, -1],
            [coreR * 2.85, 0.003, CFG.GOLD,    1],
        ].forEach(([r, spd, col, dir]) => {
            const angle = tick * spd * dir;
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angle);
            ctx.strokeStyle = hexA(col, 0.22);
            ctx.lineWidth   = 1;
            ctx.setLineDash([4, 20]);
            ctx.beginPath();
            ctx.ellipse(0, 0, r, r * 0.40, 0, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
            // Dot on ring
            ctx.shadowBlur  = 8;
            ctx.shadowColor = col;
            ctx.fillStyle   = col;
            ctx.beginPath();
            ctx.arc(r, 0, 3.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        });

        // Glass sphere
        const sG = ctx.createRadialGradient(cx - coreR * 0.3, cy - coreR * 0.3, 0, cx, cy, coreR);
        sG.addColorStop(0,   hexA('#b0f0ec', 0.24));
        sG.addColorStop(0.5, hexA(CFG.TEAL,  0.12));
        sG.addColorStop(1,   'rgba(0,0,0,0)');
        ctx.save();
        ctx.shadowBlur  = 32 * pulse;
        ctx.shadowColor = CFG.TEAL;
        ctx.fillStyle   = sG;
        ctx.strokeStyle = hexA(CFG.TEAL, 0.38 * pulse);
        ctx.lineWidth   = 1.5;
        ctx.beginPath();
        ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.restore();

        // Internal neural nodes
        for (let i = 0; i < 7; i++) {
            const angle = tick * 0.012 + i * 0.8976;
            const dist  = coreR * (0.40 + Math.sin(tick * 0.022 + i) * 0.15);
            const nx    = cx + Math.cos(angle) * dist;
            const ny    = cy + Math.sin(angle) * dist * 0.68;

            // Spoke to centre
            ctx.save();
            ctx.strokeStyle = hexA(CFG.TEAL, 0.25);
            ctx.lineWidth   = 0.7;
            ctx.beginPath();
            ctx.moveTo(nx, ny);
            ctx.lineTo(cx, cy);
            ctx.stroke();
            ctx.restore();

            // Node dot
            const np = Math.sin(tick * 0.05 + i * 1.3) * 0.5 + 0.5;
            ctx.save();
            ctx.shadowBlur  = 9 * np;
            ctx.shadowColor = CFG.TEAL;
            ctx.fillStyle   = hexA(CFG.TEAL, 0.65 + 0.35 * np);
            ctx.beginPath();
            ctx.arc(nx, ny, 2.6, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // Centre glow
        ctx.save();
        ctx.shadowBlur  = 22;
        ctx.shadowColor = '#fff';
        ctx.fillStyle   = '#fff';
        ctx.globalAlpha = 0.55 * pulse;
        ctx.beginPath();
        ctx.arc(cx, cy, 4.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // Label
        ctx.save();
        ctx.textAlign   = 'center';
        ctx.font        = '600 9.5px JetBrains Mono, monospace';
        ctx.fillStyle   = CFG.TEAL;
        ctx.globalAlpha = 0.75;
        ctx.fillText('MULTIMODAL FUSION', cx, cy + coreR + 22);
        ctx.restore();
    }

    /* ------------------------------------------------------------------
       ANALYSIS PATH
    ------------------------------------------------------------------ */
    const analysisSteps = [
        { ...layout.an1, label: 'PATTERN'   },
        { ...layout.an2, label: 'CONTEXT'   },
        { ...layout.an3, label: 'INFERENCE' },
    ];

    function drawAnalysisPath() {
        const nodes = analysisSteps.map(n => ({ ...n, cx: sx(n.x), cy: sy(n.y) }));
        const isOn  = (state === 'PROCESSING' || state === 'OUTPUT');

        // Connector lines
        for (let i = 0; i < nodes.length - 1; i++) {
            const a = nodes[i], b = nodes[i + 1];
            ctx.save();
            ctx.strokeStyle = hexA(CFG.GOLD, 0.22);
            ctx.lineWidth   = 1;
            ctx.setLineDash([3, 12]);
            ctx.beginPath();
            ctx.moveTo(a.cx, a.cy);
            ctx.lineTo(b.cx, b.cy);
            ctx.stroke();
            ctx.setLineDash([]);

            if (isOn) {
                const t  = (Math.sin(tick * 0.04 + i) + 1) / 2;
                const px = a.cx + (b.cx - a.cx) * t;
                const py = a.cy + (b.cy - a.cy) * t;
                ctx.shadowBlur  = 6;
                ctx.shadowColor = CFG.GOLD;
                ctx.fillStyle   = CFG.GOLD;
                ctx.beginPath();
                ctx.arc(px, py, 2.8, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();
        }

        nodes.forEach((node, i) => {
            const pulse = Math.sin(tick * 0.04 + i * 1.4) * 0.4 + 0.6;
            const r     = 12;
            ctx.save();
            ctx.shadowBlur  = isOn ? 16 * pulse : 4;
            ctx.shadowColor = CFG.GOLD;
            ctx.strokeStyle = hexA(CFG.GOLD, isOn ? 0.8 * pulse : 0.22);
            ctx.lineWidth   = 1.5;
            ctx.fillStyle   = hexA(CFG.GOLD, isOn ? 0.14 * pulse : 0.05);
            ctx.beginPath();
            ctx.arc(node.cx, node.cy, r, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
            ctx.fillStyle   = CFG.GOLD;
            ctx.globalAlpha = isOn ? 0.88 : 0.28;
            ctx.shadowBlur  = isOn ? 10 : 2;
            ctx.beginPath();
            ctx.arc(node.cx, node.cy, 3.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();

            ctx.save();
            ctx.textAlign   = 'center';
            ctx.font        = '500 8.5px JetBrains Mono, monospace';
            ctx.fillStyle   = hexA(CFG.GOLD, isOn ? 0.88 : 0.35);
            ctx.fillText(node.label, node.cx, node.cy + r + 13);
            ctx.restore();
        });
    }

    /* ------------------------------------------------------------------
       SIGNAL PROCESSING LABEL
    ------------------------------------------------------------------ */
    function drawMidLabel() {
        const cx = sx(0.30);
        const cy = sy(0.10);
        ctx.save();
        ctx.textAlign   = 'center';
        ctx.font        = '600 9px JetBrains Mono, monospace';
        ctx.fillStyle   = hexA(CFG.MUTED, 0.45);
        ctx.fillText('SIGNAL PROCESSING', cx, cy);
        ctx.strokeStyle = hexA(CFG.MUTED, 0.13);
        ctx.lineWidth   = 1;
        ctx.setLineDash([2, 10]);
        ctx.beginPath();
        ctx.moveTo(sx(0.17), cy + 6);
        ctx.lineTo(sx(0.44), cy + 6);
        ctx.stroke();
        ctx.restore();
    }

    /* ------------------------------------------------------------------
       OUTPUT CARD REVEAL
    ------------------------------------------------------------------ */
    function revealOutputCard(result) {
        const card  = document.getElementById('insight-card-container');
        const title = document.getElementById('final-severity-title');
        const desc  = document.getElementById('final-severity-desc');
        if (!card) return;

        const severityColor = (result && result.color) ? result.color : CFG.TEAL;

        title.innerText   = result ? result.severity    : 'Mild–Moderate';
        title.style.color = severityColor;
        desc.innerText    = result ? result.description : 'Multimodal signal fusion complete. This is an academic research estimate only.';

        const innerCard = card.querySelector('.wizard-card');
        if (innerCard) {
            innerCard.style.borderColor = severityColor + '66';
            innerCard.style.boxShadow   = `0 0 60px ${severityColor}28`;
        }

        setTimeout(() => {
            card.style.opacity   = '1';
            card.style.transform = 'translateX(0)';
        }, 600);
    }

    /* ------------------------------------------------------------------
       PARTICLE SPAWNER
    ------------------------------------------------------------------ */
    let pTimer = 0;
    function spawnParticles() {
        const isProc = (state === 'PROCESSING' || state === 'OUTPUT');
        const speed  = isProc ? CFG.PARTICLE_SPEED_PROC : CFG.PARTICLE_SPEED_IDLE;
        const every  = isProc ? 12 : 28;

        if (pTimer++ % every !== 0) return;

        const colors = [CFG.TEAL, CFG.GOLD, CFG.VIOLET];
        [layout.nodeL1, layout.nodeL2, layout.nodeL3].forEach((src, i) => {
            particles.push(new Particle(src, layout.core, colors[i], speed));
        });

        if (isProc) {
            particles.push(new Particle(layout.core, layout.an1,   CFG.GOLD, speed * 0.7));
            particles.push(new Particle(layout.core, layout.an3,   CFG.GOLD, speed * 0.7));
            particles.push(new Particle(layout.an2,  layout.output, CFG.TEAL, speed * 0.55));
        }

        particles = particles.filter(p => !p.dead);
        if (particles.length > 320) particles.splice(0, particles.length - 320);
    }

    /* ------------------------------------------------------------------
       UTILITY
    ------------------------------------------------------------------ */
    function hexA(hex, alpha) {
        if (hex.startsWith('rgba') || hex.startsWith('rgb')) {
            return hex.replace(/[\d.]+\)$/, `${alpha.toFixed(2)})`);
        }
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r},${g},${b},${alpha})`;
    }

    /* ------------------------------------------------------------------
       ANIMATION LOOP
    ------------------------------------------------------------------ */
    function animate() {
        RAF = requestAnimationFrame(animate);
        tick++;

        // Smooth parallax
        parallax.x += ((mouse.x / W - 0.5) * CFG.PARALLAX_STRENGTH - parallax.x) * 0.06;
        parallax.y += ((mouse.y / H - 0.5) * CFG.PARALLAX_STRENGTH - parallax.y) * 0.06;

        ctx.clearRect(0, 0, W, H);

        // Signal path connectors (behind everything)
        inputNodes.forEach((node) => {
            ctx.save();
            ctx.strokeStyle = hexA(node.color, state === 'PROCESSING' ? 0.20 : 0.08);
            ctx.lineWidth   = 1;
            ctx.beginPath();
            ctx.moveTo(sx(node.x), sy(node.y));
            ctx.bezierCurveTo(
                sx(0.28), sy(node.y),
                sx(0.38), sy(layout.core.y),
                sx(layout.core.x), sy(layout.core.y)
            );
            ctx.stroke();
            ctx.restore();
        });

        // Core → analysis connectors
        ctx.save();
        ctx.strokeStyle = hexA(CFG.GOLD, 0.10);
        ctx.lineWidth   = 1;
        ctx.beginPath();
        ctx.moveTo(sx(layout.core.x), sy(layout.core.y));
        ctx.lineTo(sx(layout.an1.x),  sy(layout.an1.y));
        ctx.moveTo(sx(layout.core.x), sy(layout.core.y));
        ctx.lineTo(sx(layout.an3.x),  sy(layout.an3.y));
        ctx.stroke();
        ctx.restore();

        drawMidLabel();
        inputNodes.forEach((node, i) => drawInputNode(node, i));
        drawFusionCore();
        drawAnalysisPath();

        spawnParticles();
        particles.forEach(p => { p.update(); p.draw(); });
    }

    /* ------------------------------------------------------------------
       RESIZE
    ------------------------------------------------------------------ */
    function resize() {
        if (!canvas) return;
        const dpr  = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width  = rect.width  * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);
        W = rect.width;
        H = rect.height;
    }

    /* ------------------------------------------------------------------
       INIT
    ------------------------------------------------------------------ */
    function init() {
        canvas = document.getElementById('fusion-pipeline-canvas');
        if (!canvas) return;
        ctx = canvas.getContext('2d');
        resize();

        window.addEventListener('mousemove', (e) => { mouse.x = e.clientX; mouse.y = e.clientY; });
        window.addEventListener('resize', resize);

        if (RAF) cancelAnimationFrame(RAF);
        animate();
    }

    /* ------------------------------------------------------------------
       STATE TRANSITIONS
    ------------------------------------------------------------------ */
    function startProcessing(result) {
        state = 'PROCESSING';
        setTimeout(() => {
            state = 'OUTPUT';
            revealOutputCard(result);
        }, CFG.PROCESSING_DURATION);
    }

    /* ------------------------------------------------------------------
       PUBLIC EVENT LISTENER (from assessment.js)
    ------------------------------------------------------------------ */
    window.addEventListener('StartFusionPipeline', (e) => {
        const result = (e && e.detail) ? e.detail : null;
        particles = [];

        if (!canvas || !ctx) {
            setTimeout(() => {
                init();
                setTimeout(() => startProcessing(result), 400);
            }, 80);
        } else {
            state = 'IDLE';
            startProcessing(result);
        }
    });

    window.FusionPipeline = { init, startProcessing, revealOutputCard };

})();
