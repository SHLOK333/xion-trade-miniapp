/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Telegram theme colors
        'tg-bg': 'var(--tg-theme-bg-color, #1a1a2e)',
        'tg-text': 'var(--tg-theme-text-color, #ffffff)',
        'tg-hint': 'var(--tg-theme-hint-color, #7a7a8c)',
        'tg-link': 'var(--tg-theme-link-color, #6c5ce7)',
        'tg-button': 'var(--tg-theme-button-color, #6c5ce7)',
        'tg-button-text': 'var(--tg-theme-button-text-color, #ffffff)',
        'tg-secondary': 'var(--tg-theme-secondary-bg-color, #16213e)',
        
        // App colors
        'profit': '#00d26a',
        'loss': '#ff4757',
        'warning': '#ffa502',
        'accent': '#6c5ce7',
        'accent-light': '#a29bfe',
        'dark': '#0f0f23',
        'dark-card': '#1a1a2e',
        'dark-border': '#2d2d44',
      },
      fontFamily: {
        'display': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
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
