/* ==========================================================================
   moodcompiler — 3D Living Emotional Signal Field (Luxury Aesthetic)
   ========================================================================== */

(function () {
  const canvas = document.getElementById('emotional-signal-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width, height;
  let mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  let time = 0;

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }
  window.addEventListener('resize', resize);
  resize();

  window.addEventListener('mousemove', (e) => {
    mouse.targetX = (e.clientX - width / 2) * 0.05;
    mouse.targetY = (e.clientY - height / 2) * 0.05;
  });

  // Constellation of Thought Particles
  const PARTICLE_COUNT = window.innerWidth < 768 ? 35 : 70;
  const particles = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      radius: Math.random() * 2 + 1,
      color: Math.random() > 0.4 ? 'rgba(0, 240, 255, ' : 'rgba(168, 85, 247, ',
      alpha: Math.random() * 0.5 + 0.2
    });
  }

  // 1. Draw Volumetric Emotional Silk Waves across entire viewport
  function drawEtherealWaves() {
    const waveCount = 4;
    const waveColors = [
      { stroke: 'rgba(0, 240, 255, 0.35)', fill: 'rgba(0, 240, 255, 0.03)', speed: 0.008, amp: 55, freq: 0.0025, y: height * 0.42 },
      { stroke: 'rgba(168, 85, 247, 0.3)', fill: 'rgba(168, 85, 247, 0.025)', speed: 0.006, amp: 70, freq: 0.002, y: height * 0.50 },
      { stroke: 'rgba(56, 189, 248, 0.35)', fill: 'rgba(56, 189, 248, 0.03)', speed: 0.01, amp: 45, freq: 0.003, y: height * 0.58 },
      { stroke: 'rgba(0, 240, 255, 0.25)', fill: 'rgba(0, 240, 255, 0.02)', speed: 0.007, amp: 60, freq: 0.0018, y: height * 0.65 }
    ];

    waveColors.forEach((wave, idx) => {
      ctx.beginPath();
      ctx.moveTo(0, height);

      for (let x = 0; x <= width; x += 15) {
        // Multi-harmonic sine computation for organic, non-mechanical flow
        const y = wave.y + 
                  Math.sin(x * wave.freq + time * wave.speed * 60 + idx) * wave.amp +
                  Math.cos(x * wave.freq * 1.5 - time * 0.004) * (wave.amp * 0.45) +
                  mouse.y * (0.2 + idx * 0.1);
        ctx.lineTo(x, y);
      }

      ctx.lineTo(width, height);
      ctx.closePath();

      // Soft volumetric glowing stroke
      ctx.strokeStyle = wave.stroke;
      ctx.lineWidth = 1.6;
      ctx.shadowColor = wave.stroke;
      ctx.shadowBlur = 15;
      ctx.stroke();

      // Soft gradient wash underneath the wave
      ctx.fillStyle = wave.fill;
      ctx.fill();
      ctx.shadowBlur = 0;
    });
  }

  // 2. Draw Neural Constellation & Dynamic Connecting Synapses
  function drawNeuralNetwork() {
    // Update and draw particles
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x + mouse.x * 0.2, p.y + mouse.y * 0.2, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color + p.alpha + ')';
      ctx.shadowColor = p.color + '0.8)';
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Connect nearby particles with subtle glowing filaments
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = (p.x - p2.x);
        const dy = (p.y - p2.y);
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 130) {
          const alpha = (1 - dist / 130) * 0.22;
          ctx.beginPath();
          ctx.moveTo(p.x + mouse.x * 0.2, p.y + mouse.y * 0.2);
          ctx.lineTo(p2.x + mouse.x * 0.2, p2.y + mouse.y * 0.2);
          ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
          ctx.lineWidth = 0.7;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    time += 0.012;
    mouse.x += (mouse.targetX - mouse.x) * 0.05;
    mouse.y += (mouse.targetY - mouse.y) * 0.05;

    ctx.clearRect(0, 0, width, height);

    // Deep space radial glows (Atmosphere)
    const glow1 = ctx.createRadialGradient(width * 0.2 + mouse.x, height * 0.3 + mouse.y, 10, width * 0.2, height * 0.3, width * 0.5);
    glow1.addColorStop(0, 'rgba(0, 240, 255, 0.10)');
    glow1.addColorStop(1, 'transparent');
    ctx.fillStyle = glow1;
    ctx.fillRect(0, 0, width, height);

    const glow2 = ctx.createRadialGradient(width * 0.8 - mouse.x, height * 0.6 - mouse.y, 10, width * 0.8, height * 0.6, width * 0.55);
    glow2.addColorStop(0, 'rgba(168, 85, 247, 0.10)');
    glow2.addColorStop(1, 'transparent');
    ctx.fillStyle = glow2;
    ctx.fillRect(0, 0, width, height);

    drawEtherealWaves();
    drawNeuralNetwork();

    requestAnimationFrame(animate);
  }

  animate();
})();