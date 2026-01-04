import { Sun, Moon } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useTheme } from 'next-themes';

interface Particle {
    id: number;
    delay: number;
    duration: number;
}

export default function CinematicThemeSwitcher() {
    const { theme, setTheme, resolvedTheme } = useTheme();

    // State Management
    const [mounted, setMounted] = useState(false);
    const [particles, setParticles] = useState<Particle[]>([]);
    const [isAnimating, setIsAnimating] = useState(false);

    // Ref to track toggle button DOM element
    const toggleRef = useRef<HTMLButtonElement>(null);

    // Track whether toggle is in checked (dark) or unchecked (light) position
    const isDark = mounted && (theme === 'dark' || resolvedTheme === 'dark');

    // Handle hydration
    useEffect(() => {
        setMounted(true);
    }, []);

    const generateParticles = () => {
        const newParticles: Particle[] = [];
        const particleCount = 3;

        for (let i = 0; i < particleCount; i++) {
            newParticles.push({
                id: Date.now() + i,
                delay: i * 0.1,
                duration: 0.6 + i * 0.1,
            });
        }

        setParticles(newParticles);
        setIsAnimating(true);

        setTimeout(() => {
            setIsAnimating(false);
            setParticles([]);
        }, 1000);
    };

    const handleToggle = () => {
        generateParticles();
        setTheme(isDark ? 'light' : 'dark');
    };

    if (!mounted) {
        return <div className="w-[104px] h-[64px]" />;
    }

    return (
        <div className="relative inline-block transform scale-75 origin-right">
            <svg className="absolute w-0 h-0">
                <defs>
                    <filter id="grain-dark">
                        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" result="noise" />
                        <feColorMatrix in="noise" type="saturate" values="0" result="desaturatedNoise" />
                        <feBlend in="SourceGraphic" in2="desaturatedNoise" mode="overlay" />
                    </filter>
                </defs>
            </svg>

            <motion.button
                ref={toggleRef}
                onClick={handleToggle}
                className="relative flex h-[64px] w-[104px] items-center rounded-full p-[6px] transition-all duration-300 focus:outline-none"
                style={{
                    background: isDark
                        ? 'radial-gradient(ellipse at top left, #1e293b 0%, #0f172a 40%, #020617 100%)'
                        : 'radial-gradient(ellipse at top left, #ffffff 0%, #f1f5f9 40%, #cbd5e1 100%)',
                    boxShadow: isDark
                        ? 'inset 5px 5px 12px rgba(0,0,0,0.9), inset -5px -5px 12px rgba(71,85,105,0.4), inset 0 2px 4px rgba(0,0,0,1)'
                        : 'inset 5px 5px 12px rgba(148,163,184,0.5), inset -5px -5px 12px rgba(255,255,255,1)',
                    border: isDark ? '2px solid rgba(51, 65, 85, 0.6)' : '2px solid rgba(203, 213, 225, 0.6)',
                }}
                whileTap={{ scale: 0.98 }}
            >
                {/* Background Icons */}
                <div className="absolute inset-0 flex items-center justify-between px-4">
                    <Sun size={20} className="text-amber-500" />
                    <Moon size={20} className="text-slate-600" />
                </div>

                {/* Thumb */}
                <motion.div
                    className="relative z-10 flex h-[44px] w-[44px] items-center justify-center rounded-full"
                    style={{
                        background: isDark
                            ? 'linear-gradient(145deg, #64748b 0%, #475569 50%, #334155 100%)'
                            : 'linear-gradient(145deg, #ffffff 0%, #fefefe 50%, #f8fafc 100%)',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                        border: isDark ? '2px solid rgba(148,163,184,0.3)' : '2px solid rgba(255,255,255,0.9)',
                    }}
                    animate={{ x: isDark ? 40 : 0 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                >
                    {/* Particles */}
                    {isAnimating && particles.map((p) => (
                        <motion.div
                            key={p.id}
                            className="absolute inset-0 flex items-center justify-center pointer-events-none"
                        >
                            <motion.div
                                className="absolute rounded-full"
                                style={{
                                    width: '10px', height: '10px',
                                    background: isDark ? 'rgba(147, 197, 253, 0.8)' : 'rgba(251, 191, 36, 0.8)',
                                }}
                                initial={{ scale: 0, opacity: 1 }}
                                animate={{ scale: 6, opacity: 0 }}
                                transition={{ duration: p.duration, delay: p.delay, ease: 'easeOut' }}
                            />
                        </motion.div>
                    ))}

                    <div className="relative z-10">
                        {isDark ? <Moon size={20} className="text-yellow-200" /> : <Sun size={20} className="text-amber-500" />}
                    </div>
                </motion.div>
            </motion.button>
        </div>
    );
}
