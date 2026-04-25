import React from 'react';

const MoodPulse = ({ mood = 6 }) => {
  // Determine color based on mood (1-10)
  // 1: Red/Orange, 10: Bright Teal/Blue
  const getMoodColor = (m) => {
    if (m < 4) return '#f87171'; // Red
    if (m < 7) return '#6366f1'; // Indigo
    return '#14b8a6'; // Teal
  };

  const pulseColor = getMoodColor(mood);

  return (
    <div className="mood-pulse-container" style={{ 
      position: 'relative', 
      width: '200px', 
      height: '200px', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      margin: '0 auto'
    }}>
      {/* Outer Glow */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          borderRadius: '50%',
          background: pulseColor,
          filter: 'blur(40px)',
          zIndex: 0
        }}
      />

      {/* Internal "Liquid" Pulse */}
      <motion.div
        animate={{
          borderRadius: [
            "40% 60% 70% 30% / 40% 50% 60% 50%",
            "30% 60% 70% 40% / 50% 60% 30% 60%",
            "60% 40% 30% 70% / 60% 30% 70% 40%",
            "40% 60% 70% 30% / 40% 50% 60% 50%",
          ],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "linear"
        }}
        style={{
          width: '120px',
          height: '120px',
          background: `linear-gradient(135deg, ${pulseColor}, #fff)`,
          boxShadow: `0 0 30px ${pulseColor}`,
          zIndex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 'bold',
          fontSize: '2rem'
        }}
      >
        {mood}
      </motion.div>
    </div>
  );
};

export default MoodPulse;
