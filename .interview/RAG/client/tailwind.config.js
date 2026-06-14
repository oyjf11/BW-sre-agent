/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#165DFF',
          dark: '#044AE9',
          light: '#F0F5FF',
          border: '#E8ECFF',
        },
        text: {
          primary: '#151515',
          secondary: '#6C6F7D',
        },
        bg: {
          page: '#F8FAFF',
          hover: '#F0F5FF',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', "'Segoe UI'", "'PingFang SC'", "'Hiragino Sans GB'", "'Microsoft YaHei'", 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 16px rgba(22, 93, 255, 0.08)',
        'card-hover': '0 12px 32px rgba(22, 93, 255, 0.15)',
        'btn': '0 4px 12px rgba(22, 93, 255, 0.3)',
        'modal': '0 20px 60px rgba(0, 0, 0, 0.15)',
      },
      borderRadius: {
        card: '16px',
        btn: '6px',
        input: '12px',
      },
      transitionTimingFunction: {
        standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      keyframes: {
        'slide-in-left': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'slide-in-up': {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        // 眨眼动画：自然双眨眼效果，每 5s 循环
        // 第一次眨眼 72-78%，短暂谁眼 79-82%，第二次祸眼 84-88%
        'blink': {
          '0%, 70%, 100%':   { opacity: '0' },  // 睡眼张开
          '72%, 76%':         { opacity: '1' },  // 第一次闭眼
          '78%, 82%':         { opacity: '0' },  // 短暂閏亮（双眨间隔）
          '84%, 87.5%':       { opacity: '1' },  // 第二次闭眼
          '90%':              { opacity: '0' },  // 简开
        },
        // 轻盈浮动：上下微幅浮动，赋予生命感
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-8px)' },
        },
      },
      animation: {
        'slide-in-left': 'slide-in-left 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
        'slide-in-up': 'slide-in-up 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
        'fade-in': 'fade-in 0.15s ease',
        'blink': 'blink 5s step-start infinite',
        'float': 'float 3s ease-in-out infinite',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
