import React from 'react';
import { useDarkMode } from './useDarkMode';

interface DarkModeToggleProps {
  className?: string;
}

const DarkModeToggle: React.FC<DarkModeToggleProps> = ({ className }) => {
  const { isDark, toggle } = useDarkMode();

  return (
    <button
      className={`dark-mode-toggle${className ? ` ${className}` : ''}`}
      onClick={toggle}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <span>{isDark ? '☀️' : '🌙'}</span>
      <span className="toggle-label">{isDark ? 'Light' : 'Dark'}</span>
    </button>
  );
};

export default DarkModeToggle;
