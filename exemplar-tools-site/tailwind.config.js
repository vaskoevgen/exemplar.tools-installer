/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0a0a0f',
        'ink-light': '#12121a',
        'ink-border': '#1e1e2e',
        cyan: {
          400: '#22d3ee',
          500: '#06b6d4',
        },
        // per-tool accent palette
        constrain: '#f59e0b',
        ledger: '#10b981',
        pact: '#3b82f6',
        advocate: '#8b5cf6',
        arbiter: '#ef4444',
        baton: '#f97316',
        sentinel: '#06b6d4',
        chronicler: '#ec4899',
        stigmergy: '#84cc16',
        apprentice: '#a855f7',
        kindex: '#14b8a6',
      },
      fontFamily: {
        display: ['"Instrument Serif"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out forwards',
        'slide-up': 'slideUp 0.5s ease-out forwards',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(16px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
