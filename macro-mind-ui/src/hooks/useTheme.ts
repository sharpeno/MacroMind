import { useCallback, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

function initialTheme(): Theme {
  try {
    const saved = localStorage.getItem('mm-theme');
    if (saved === 'light' || saved === 'dark') return saved;
  } catch {
    /* 存储不可用时使用默认 */
  }
  // 默认深色（科技感基调）；用户切换后以保存的偏好为准
  return 'dark';
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(initialTheme);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    try {
      localStorage.setItem('mm-theme', theme);
    } catch {
      /* 忽略 */
    }
  }, [theme]);

  const toggle = useCallback(() => setTheme((t) => (t === 'dark' ? 'light' : 'dark')), []);
  return { theme, toggle };
}
