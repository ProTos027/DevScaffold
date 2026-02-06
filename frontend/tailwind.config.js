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
                sans: ['var(--font-main)', 'Inter', 'sans-serif'],
                display: ['var(--font-display)', 'Orbitron', 'sans-serif'],
            },
            colors: {
                // Map to CSS variables
                cosmic: {
                    cyan: 'rgb(var(--color-primary) / <alpha-value>)',
                    blue: 'rgb(var(--color-secondary) / <alpha-value>)',
                    pink: 'rgb(var(--color-accent) / <alpha-value>)',
                    purple: 'rgb(var(--color-secondary-accent) / <alpha-value>)',
                },
                space: {
                    950: 'rgb(var(--bg-primary) / <alpha-value>)',
                    900: 'rgb(var(--bg-secondary) / <alpha-value>)',
                },
                // Keep some legacy aliases for safety but point to variables
                nebula: {
                    50: 'rgb(var(--bg-secondary) / 0.5)',
                }
            },
            backgroundImage: {
                'gradient-primary': 'var(--gradient-primary)',
                'gradient-secondary': 'var(--gradient-secondary)',
                'gradient-cosmic': 'var(--gradient-primary)', // Keeping alias for safety
            },
            animation: {
                'fade-in': 'fade-in 0.5s ease-out forwards',
                'slide-in-left': 'slide-in-left 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'slide-in-right': 'slide-in-right 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
            }
        },
    },
    plugins: [],
}
