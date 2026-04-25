import React from 'react';
import { Sparkles, ArrowRight, Activity as ActivityIcon } from 'lucide-react';

const ActivityCard = ({ title, category, difficulty, xp, onComplete }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
      className="glass-card"
      style={{ position: 'relative', overflow: 'hidden' }}
    >
      {/* Decorative Background Icon */}
      <div style={{ 
        position: 'absolute', 
        right: '-10px', 
        top: '-10px', 
        opacity: 0.05,
        color: 'var(--accent-primary)'
      }}>
        <ActivityIcon size={120} />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            background: 'var(--accent-secondary)',
            boxShadow: '0 0 10px var(--accent-secondary)'
          }} />
          <span style={{ 
            fontSize: '0.75rem', 
            fontWeight: 'bold', 
            color: 'var(--text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.1em'
          }}>
            {category}
          </span>
        </div>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', background: 'var(--ui-glass)', padding: '2px 8px', borderRadius: '20px' }}>
          {difficulty}x Multiplier
        </span>
      </div>
      
      <h3 style={{ fontSize: '1.4rem', marginBottom: '0.75rem', fontWeight: 700 }}>{title}</h3>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.9rem', lineHeight: '1.5' }}>
        Strategically selected to reinforce your **Connection** value and break the current avoidance cycle.
      </p>
      
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Sparkles size={16} color="var(--accent-primary)" />
          <span style={{ color: 'var(--accent-primary)', fontWeight: 'bold', fontSize: '1.1rem' }}>+{xp} XP</span>
        </div>
        
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="btn-primary" 
          onClick={onComplete}
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            padding: '0.6rem 1.2rem'
          }}
        >
          Activate <ArrowRight size={18} />
        </motion.button>
      </div>
    </motion.div>
  );
};

export default ActivityCard;
