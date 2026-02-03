/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                display: ['Orbitron', 'sans-serif'],
            },
            colors: {
                // Dark mode (space theme)
                space: {
                    900: '#0a0e27',  // Deep space
                    800: '#1a0933',  // Dark purple
                    700: '#1e1b4b',  // Indigo night
                    600: '#312e81',  // Deep purple
                    500: '#4c1d95',  // Purple
                },
                cosmic: {
                    cyan: '#00d9ff',      // Neon cyan
                    purple: '#b829fc',    // Neon purple
                    pink: '#ff006e',      // Neon pink
                    blue: '#3b82f6',      // Electric blue
                },
                // Light mode (soft space)
                nebula: {
                    50: '#f0f9ff',   // Very light blue
                    100: '#e0f2fe',  // Light sky
                    200: '#bae6fd',  // Soft blue
                    300: '#7dd3fc',  // Light cyan
                },
            },
            backgroundImage: {
                'gradient-space': 'linear-gradient(135deg, #0a0e27 0%, #1a0933 50%, #1e1b4b 100%)',
                'gradient-cosmic': 'linear-gradient(135deg, #00d9ff 0%, #b829fc 100%)',
                'gradient-light': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
            },
            boxShadow: {
                'glow-cyan': '0 0 20px rgba(0, 217, 255, 0.5)',
                'glow-purple': '0 0 20px rgba(184, 41, 252, 0.5)',
                'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-in-out',
                'slide-up': 'slideUp 0.5s ease-out',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(0, 217, 255, 0.5)' },
                    '100%': { boxShadow: '0 0 20px rgba(0, 217, 255, 0.8)' },
                },
            },
        },
    },
    plugins: [],
}
