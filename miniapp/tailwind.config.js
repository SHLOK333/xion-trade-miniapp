/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Telegram theme colors - Dark terminal style
        'tg-bg': 'var(--tg-theme-bg-color, #0d0d0d)',
        'tg-text': 'var(--tg-theme-text-color, #e5e5e5)',
        'tg-hint': 'var(--tg-theme-hint-color, #6b6b6b)',
        'tg-link': 'var(--tg-theme-link-color, #00d26a)',
        'tg-button': 'var(--tg-theme-button-color, #00d26a)',
        'tg-button-text': 'var(--tg-theme-button-text-color, #000000)',
        'tg-secondary': 'var(--tg-theme-secondary-bg-color, #1a1a1a)',
        
        // App colors - Clean trading terminal
        'profit': '#00d26a',
        'profit-light': '#00ff88',
        'loss': '#ff3b3b',
        'loss-light': '#ff5252',
        'warning': '#f0b90b',
        'accent': '#00d26a',
        'accent-light': '#00ff88',
        'dark': '#0d0d0d',
        'dark-card': '#141414',
        'dark-secondary': '#1a1a1a',
        'dark-border': '#2a2a2a',
        'dark-text': '#e5e5e5',
        'dark-hint': '#6b6b6b',
      },
      fontFamily: {
        'display': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        'mono': ['SF Mono', 'Monaco', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(108, 92, 231, 0.3)' },
          '100%': { boxShadow: '0 0 40px rgba(108, 92, 231, 0.6)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: 0 },
          '100%': { transform: 'scale(1)', opacity: 1 },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
