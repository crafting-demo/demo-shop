import React from 'react';
import { useTheme } from './ThemeContext';
import './DarkModeToggle.css';

const DarkModeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      className="dark-mode-toggle"
      onClick={toggleTheme}
      aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
};

export default DarkModeToggle;
