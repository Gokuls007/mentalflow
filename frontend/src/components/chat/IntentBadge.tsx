import React from 'react';

interface IntentBadgeProps {
  intent: string;
}

export const IntentBadge: React.FC<IntentBadgeProps> = ({ intent }) => {
  if (!intent || intent === 'CHAT') return null;

  const getStyle = () => {
    switch (intent) {
      case 'CRISIS':
        return 'bg-red-500 text-white animate-pulse';
      case 'ASSESSMENT':
        return 'bg-purple-500 text-white';
      case 'ACTIVITY':
        return 'bg-green-500 text-white';
      case 'MOOD':
        return 'bg-blue-500 text-white';
      case 'SUPPORT':
        return 'bg-indigo-400 text-white';
      default:
        return 'bg-gray-400 text-white';
    }
  };

  return (
    <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider mb-1 inline-block ${getStyle()}`}>
      {intent}
    </span>
  );
};
