import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";

// --- Assets & Constants ---
const ALFRED_AVATAR_URL = "https://images.unsplash.com/photo-1559548331-f9cb98001426?q=80&w=200&auto=format&fit=crop"; 
const THEME = {
  bg: "#050b14",
  panelBg: "rgba(10, 20, 35, 0.9)", 
  primary: "#62d9ff", // Cyan
  secondary: "#1a3c5e", // Dark Blue
  text: "#e0f7ff",
  muted: "#4a6fa5",
  success: "#00ff9d",
  danger: "#ff4a4a",
  warning: "#ffcc00",
  grid: "rgba(98, 217, 255, 0.07)"
};

// --- Components ---

const Waveform = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let t = 0;

    const resize = () => {
      canvas.width = canvas.parentElement?.clientWidth || 300;
      canvas.height = canvas.parentElement?.clientHeight || 150;
    };
    window.addEventListener('resize', resize);
    resize();

    const draw = () => {
      if (!ctx) return;
      const { width, height } = canvas;
      ctx.clearRect(0, 0, width, height);

      const centerY = height / 2;
      
      const lines = [
        { color: "rgba(98, 217, 255, 0.8)", speed: 0.05, amp: 30, freq: 0.02 },
        { color: "rgba(98, 217, 255, 0.5)", speed: 0.03, amp: 40, freq: 0.015 },
        { color: "rgba(0, 255, 157, 0.3)", speed: 0.07, amp: 20, freq: 0.03 },
      ];

      lines.forEach((line, i) => {
        ctx.beginPath();
        ctx.strokeStyle = line.color;
        ctx.lineWidth = 2;

        for (let x = 0; x < width; x++) {
          const modulation = Math.sin(t * 0.05 + x * 0.01) * 0.5 + 0.5; 
          const y = centerY + Math.sin(x * line.freq + t * line.speed) * (line.amp * modulation);
          ctx.lineTo(x, y);
        }
        ctx.stroke();
      });

      t += 2;
      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />;
};

const TechBorder = ({ children, title, className = "" }: { children?: React.ReactNode, title?: string, className?: string }) => (
  <div className={`relative p-1 ${className}`} style={{ background: 'transparent' }}>
    {/* Corner Brackets */}
    <div className="absolute top-0 left-0 w-4 h-4 border-l-2 border-t-2" style={{ borderColor: THEME.primary }}></div>
    <div className="absolute top-0 right-0 w-4 h-4 border-r-2 border-t-2" style={{ borderColor: THEME.primary }}></div>
    <div className="absolute bottom-0 left-0 w-4 h-4 border-l-2 border-b-2" style={{ borderColor: THEME.primary }}></div>
    <div className="absolute bottom-0 right-0 w-4 h-4 border-r-2 border-b-2" style={{ borderColor: THEME.primary }}></div>
    
    {/* Inner Box */}
    <div className="h-full w-full border border-opacity-30 p-4 flex flex-col relative" 
         style={{ backgroundColor: THEME.panelBg, borderColor: THEME.secondary }}>
      
      {/* Scanlines effect overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-5" 
           style={{ backgroundImage: `linear-gradient(${THEME.bg} 50%, transparent 50%)`, backgroundSize: '100% 4px' }}></div>

      {title && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-black px-4 text-xs tracking-widest font-bold uppercase z-20"
             style={{ color: THEME.primary, border: `1px solid ${THEME.secondary}` }}>
          {title}
        </div>
      )}
      
      {children}
    </div>
  </div>
);

const FooterButton = ({ icon, text, onClick, active = false }: { icon: string, text: string, onClick?: () => void, active?: boolean }) => (
  <div onClick={onClick} className={`relative h-12 w-full group cursor-pointer ${active ? 'opacity-100' : 'opacity-70 hover:opacity-100'}`}>
    {/* Button Frame */}
    <div className={`absolute inset-0 border transition-all duration-300 ${active ? 'bg-cyan-900/30' : ''}`} 
         style={{ borderColor: active ? THEME.primary : THEME.secondary, transform: 'skewX(-15deg)' }}></div>
    
    <div className="absolute inset-0 flex items-center justify-center space-x-2 transition-colors">
      <span className={`material-symbols-outlined text-lg ${active ? 'animate-pulse' : ''}`} style={{ color: THEME.primary }}>{icon}</span>
      <span className="text-xs font-bold tracking-wider uppercase" style={{ color: THEME.text }}>{text}</span>
    </div>
    
    {/* Decorators */}
    <div className="absolute bottom-0 left-0 w-2 h-2 bg-cyan-400" style={{ transform: 'skewX(-15deg)' }}></div>
    <div className="absolute top-0 right-0 w-2 h-2 border-r border-t border-cyan-400" style={{ transform: 'skewX(-15deg)' }}></div>
  </div>
);

const NotificationToast = ({ message }: { message: string | null }) => {
  if (!message) return null;
  return (
    <div className="absolute top-24 right-8 z-50 animate-bounce">
      <div className="bg-cyan-900/90 border border-cyan-500 text-cyan-100 px-6 py-3 rounded shadow-[0_0_15px_rgba(98,217,255,0.3)] flex items-center space-x-3">
        <span className="material-symbols-outlined text-sm animate-spin">sync</span>
        <span className="text-xs font-bold tracking-widest">{message}</span>
      </div>
    </div>
  );
};

// --- News View Components ---

interface NewsItemProps {
  headline: string;
  category: string;
  time: string;
  importance: 'HIGH' | 'MED' | 'LOW';
  onRead: () => void;
}

const NewsItem = ({ headline, category, time, importance, onRead }: NewsItemProps) => {
  return (
    <div className="border-b border-gray-800 pb-4 mb-4 last:border-0 last:mb-0 group hover:bg-white/5 p-2 transition-colors rounded">
      <div className="flex justify-between items-start mb-1">
        <span className="text-[10px] font-bold px-1.5 py-0.5 border border-opacity-50 tracking-widest"
              style={{ 
                borderColor: importance === 'HIGH' ? THEME.danger : THEME.primary,
                color: importance === 'HIGH' ? THEME.danger : THEME.primary 
              }}>
          {category}
        </span>
        <span className="text-[10px] opacity-60" style={{ color: THEME.muted }}>{time}</span>
      </div>
      <h3 className="text-sm font-bold tracking-wide mb-2" style={{ color: THEME.text }}>{headline}</h3>
      <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <button onClick={onRead} className="text-[10px] bg-cyan-900/50 hover:bg-cyan-800 text-cyan-200 px-3 py-1 border border-cyan-700 active:bg-cyan-600 transition-colors">
          ACCESS DATA
        </button>
        <button className="text-[10px] border border-gray-600 text-gray-400 hover:text-white hover:border-white px-3 py-1 active:bg-gray-700">
          DISMISS
        </button>
      </div>
    </div>
  );
};

const NewsPanel = ({ onAction }: { onAction: (msg: string) => void }) => {
  return (
    <div className="flex flex-col h-full w-full">
       <div className="flex items-center space-x-4 mb-4 pb-2 border-b border-gray-800">
         <span className="text-2xl material-symbols-outlined" style={{ color: THEME.warning }}>warning</span>
         <div>
           <h2 className="text-lg font-bold tracking-widest uppercase">Global Intel Feed</h2>
           <p className="text-[10px] text-gray-400 tracking-wider">SECURE CONNECTION // ENCRYPTED</p>
         </div>
       </div>

       <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
         <NewsItem 
           headline="Global Tech Summit Announces New AI Standards for 2026"
           category="REGULATION"
           time="08:42 AM"
           importance="HIGH"
           onRead={() => onAction("DECRYPTING REGULATION FILES...")}
         />
         <NewsItem 
           headline="Lunar Helium-3 Supply Chain Disrupted by Solar Flare Activity"
           category="OFF-WORLD"
           time="07:15 AM"
           importance="MED"
           onRead={() => onAction("ESTABLISHING LUNAR LINK...")}
         />
         <NewsItem 
           headline="Neural Interface v4.2 Patch Notes Released: Fixes Latency"
           category="SOFTWARE"
           time="06:30 AM"
           importance="LOW"
           onRead={() => onAction("DOWNLOADING PATCH NOTES...")}
         />
         <NewsItem 
           headline="SpaceX 'Starship' Enterprise Class docked at ISS-2"
           category="AEROSPACE"
           time="YESTERDAY"
           importance="MED"
           onRead={() => onAction("REQUESTING SATELLITE IMAGERY...")}
         />
       </div>

       <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between items-center">
          <div className="text-[10px] animate-pulse" style={{ color: THEME.success }}>
             ● LIVE UPDATES ACTIVE
          </div>
          <button onClick={() => onAction("COMPILING DAILY SUMMARY REPORT...")}
                  className="px-4 py-2 text-xs font-bold uppercase tracking-widest hover:bg-cyan-500/20 active:bg-cyan-500/40 transition-colors"
                  style={{ border: `1px solid ${THEME.primary}`, color: THEME.primary }}>
            Generate Summary Report
          </button>
       </div>
    </div>
  );
};

// --- Main App ---

const App = () => {
  const [activeView, setActiveView] = useState<'monitor' | 'news'>('monitor');
  const [notification, setNotification] = useState<string | null>(null);

  const handleSystemAction = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 2500);
  };

  return (
    <div className="w-full h-screen overflow-hidden flex flex-col font-mono select-none"
         style={{ 
           backgroundColor: THEME.bg,
           backgroundImage: `linear-gradient(${THEME.grid} 1px, transparent 1px), linear-gradient(90deg, ${THEME.grid} 1px, transparent 1px)`,
           backgroundSize: '40px 40px'
         }}>
      
      <NotificationToast message={notification} />

      {/* --- Header --- */}
      <header className="p-6 flex items-center space-x-6 relative z-10">
        <div className="relative w-24 h-24 flex-shrink-0">
           <div className="absolute inset-0 border-2 border-dashed rounded-full animate-spin-slow" 
                style={{ borderColor: THEME.secondary, animationDuration: '10s' }}></div>
           <div className="absolute inset-1 border border-cyan-900 rounded-full"></div>
           <div className="absolute inset-2 rounded-full overflow-hidden border-2" style={{ borderColor: THEME.primary }}>
             <img src={ALFRED_AVATAR_URL} alt="Alfred" className="w-full h-full object-cover filter contrast-125 sepia-50" />
           </div>
           <div className="absolute bottom-1 right-1 w-4 h-4 rounded-full border-2 border-black" 
                style={{ backgroundColor: THEME.success, boxShadow: `0 0 10px ${THEME.success}` }}></div>
        </div>

        <div className="flex flex-col">
          <h1 className="text-2xl font-bold tracking-[0.2em] uppercase" style={{ color: THEME.text }}>
            Alfred <span style={{ color: THEME.muted }}>|</span> System Online
          </h1>
          <div className="flex items-center space-x-2 text-xs mt-1" style={{ color: THEME.primary }}>
            <span className="animate-pulse">●</span>
            <span>VOICE CONNECTION ESTABLISHED</span>
          </div>
        </div>
        
        <div className="ml-auto border-t-2 border-r-2 h-8 w-32 opacity-50" style={{ borderColor: THEME.primary }}></div>
      </header>

      {/* --- Main Content --- */}
      <main className="flex-1 flex items-center justify-center p-8 relative">
        <TechBorder 
          title={activeView === 'monitor' ? "Audio Channel Active" : "Information Stream"} 
          className="w-full max-w-4xl h-[500px]"
        >
            {activeView === 'monitor' ? (
              <div className="flex flex-col h-full w-full justify-center items-center">
                <div className="w-full h-40 relative">
                  <Waveform />
                  <div className="absolute bottom-2 right-4 text-xs font-bold animate-pulse" style={{ color: THEME.primary }}>
                    RECEIVING DATA STREAM...
                  </div>
                </div>
                
                <div className="w-3/4 mt-8 bg-gray-900 h-6 border border-gray-700 relative overflow-hidden">
                  <div className="h-full bg-cyan-500/20 w-full flex items-center px-4 relative">
                    <div className="absolute top-0 left-0 h-full bg-cyan-400 w-[85%] opacity-20"></div>
                    <div className="absolute top-0 left-0 h-full w-[85%] border-r-2 border-cyan-400 shadow-[0_0_10px_rgba(98,217,255,0.5)]"></div>
                    <span className="relative z-10 text-xs font-bold tracking-widest" style={{ color: THEME.text }}>
                      PROCESSING... 85%
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <NewsPanel onAction={handleSystemAction} />
            )}
        </TechBorder>
      </main>

      {/* --- Footer Navigation --- */}
      <footer className="p-8 grid grid-cols-4 gap-4 max-w-5xl mx-auto w-full relative z-20">
        <FooterButton 
          icon="newspaper" 
          text="Industry News" 
          active={activeView === 'news'}
          onClick={() => setActiveView('news')}
        />
        <FooterButton 
          icon="rocket_launch" 
          text="Launch" 
          active={activeView === 'monitor'}
          onClick={() => setActiveView('monitor')}
        />
        <FooterButton icon="settings" text="System Config" />
        <FooterButton icon="shield" text="Security" />
      </footer>
      
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');
        
        body {
          font-family: 'Share Tech Mono', monospace;
          margin: 0;
          background: #000;
          color: white;
        }

        .animate-spin-slow {
          animation: spin 10s linear infinite;
        }

        /* Custom Scrollbar for News Panel */
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(10, 20, 35, 0.5);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #1a3c5e;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #62d9ff;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

const root = createRoot(document.getElementById("root")!);
root.render(<App />);