import React, { useEffect, useRef } from 'react';

interface MoodFieldProps {
  phq9: number;  // Depression (0-27)
  gad7: number;  // Anxiety (0-21)
  hrv?: number;  // Stress/Calmness (0-100)
}

export const MoodField: React.FC<MoodFieldProps> = ({ phq9, gad7, hrv = 50 }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let particles: Particle[] = [];

    // Clinical Mapping
    const anxietyLevel = gad7 / 21;
    const depressionLevel = phq9 / 27;
    const calmLevel = hrv / 100;

    class Particle {
      x: number;
      y: number;
      size: number;
      speedX: number;
      speedY: number;
      color: string;

      constructor() {
        this.x = Math.random() * canvas!.width;
        this.y = Math.random() * canvas!.height;
        this.size = Math.random() * 5 + 1;
        
        // Velocity reacts to Anxiety
        const baseSpeed = 0.5 + (anxietyLevel * 3);
        this.speedX = (Math.random() - 0.5) * baseSpeed;
        this.speedY = (Math.random() - 0.5) * baseSpeed;

        // Color reacts to Mood
        // High Depression = Greyscale/Deep Blue
        // High Calm = Emerald/Teal
        // High Anxiety = Purple/Magenta
        if (depressionLevel > 0.5) {
          this.color = `hsla(220, 20%, ${40 + Math.random() * 20}%, 0.3)`;
        } else if (calmLevel > 0.6) {
          this.color = `hsla(160, 60%, ${50 + Math.random() * 20}%, 0.4)`;
        } else {
          this.color = `hsla(260, 50%, ${60 + Math.random() * 20}%, 0.3)`;
        }
      }

      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x > canvas!.width) this.x = 0;
        if (this.x < 0) this.x = canvas!.width;
        if (this.y > canvas!.height) this.y = 0;
        if (this.y < 0) this.y = canvas!.height;
      }

      draw() {
        ctx!.fillStyle = this.color;
        ctx!.beginPath();
        ctx!.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx!.fill();
      }
    }

    const init = () => {
      particles = [];
      const count = 100 + Math.floor(anxietyLevel * 200);
      for (let i = 0; i < count; i++) {
        particles.push(new Particle());
      }
    };

    const animate = () => {
      // Create trailing effect for liquid feel
      ctx.fillStyle = 'rgba(2, 6, 23, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Draw Connections (Mental Flow)
      ctx.strokeStyle = `rgba(129, 140, 248, ${0.03 + calmLevel * 0.05})`;
      ctx.lineWidth = 1;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (distance < 150) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      particles.forEach(p => {
        p.update();
        p.draw();
      });
      animationFrameId = requestAnimationFrame(animate);
    };

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      init();
    };

    window.addEventListener('resize', resize);
    resize();
    animate();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [phq9, gad7, hrv]);

  return (
    <div className="absolute inset-0 z-0 opacity-40 pointer-events-none overflow-hidden rounded-[40px]">
      <canvas 
        ref={canvasRef} 
        className="w-full h-full"
        style={{ filter: 'blur(40px)' }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-[#080c14] via-transparent to-transparent" />
    </div>
  );
};
