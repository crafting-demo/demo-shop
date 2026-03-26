import React from 'react';
import { useTheme } from './ThemeContext';
import './ThemeToggle.css';

const ThemeToggle: React.FC = () => {
  const { theme, effectiveTheme, setTheme } = useTheme();

  const cycleTheme = () => {
    if (theme === 'light') {
      setTheme('dark');
    } else if (theme === 'dark') {
      setTheme('system');
    } else {
      setTheme('light');
    }
  };

  const getLabel = () => {
    if (theme === 'system') {
      return `Auto (${effectiveTheme === 'dark' ? '🌙' : '☀️'})`;
    }
    return theme === 'dark' ? '🌙 Dark' : '☀️ Light';
  };

  return (
    <button
      className="theme-toggle"
      onClick={cycleTheme}
      title={`Current: ${theme} theme. Click to cycle through light → dark → system`}
      aria-label="Toggle theme"
    >
      {getLabel()}
    </button>
  );
};

export default ThemeToggle;
