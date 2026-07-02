import React, { useEffect, useState } from 'react';
import './ThemeToggle.css';

type Theme = 'light' | 'dark';

const THEME_KEY = 'demo-shop-theme';

function getInitialTheme(): Theme {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === 'dark' || stored === 'light') return stored;
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
  return 'light';
}

const ThemeToggle: React.FC = () => {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const toggle = () => setTheme(prev => (prev === 'light' ? 'dark' : 'light'));

  return (
    <button
      className="theme-toggle"
      onClick={toggle}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <span className="theme-toggle-icon">{theme === 'light' ? '🌙' : '☀️'}</span>
    </button>
  );
};

export default ThemeToggle;
