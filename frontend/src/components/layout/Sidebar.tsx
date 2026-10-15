'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  Network, 
  ShieldAlert, 
  ActivitySquare, 
  Laptop,
  Cpu,
  Database,
  X,
  ChevronLeft,
  HelpCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSidebarStore } from '@/lib/store/sidebar';
import { motion, AnimatePresence } from 'framer-motion';

const routes = [
  { name: 'Dashboard Overview', path: '/', icon: LayoutDashboard },
  { name: 'Endpoints & Agents', path: '/endpoints', icon: Laptop },
  { name: 'Alerts & Telemetry', path: '/alerts', icon: AlertTriangle },
  { name: 'MITRE ATT&CK', path: '/mitre', icon: ShieldAlert },
  { name: 'AI Swarm Engine', path: '/swarm', icon: Network },
  { name: 'AI Model Router', path: '/ai-router', icon: Cpu },
  { name: 'Database Hub', path: '/database', icon: Database },
  { name: 'Risk & SOAR Policy', path: '/risk', icon: ActivitySquare },
  { name: 'Help & Architecture', path: '/help', icon: HelpCircle },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isOpen, close } = useSidebarStore();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop blur overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={close}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 transition-opacity"
          />

          {/* Slide-out Sidebar Drawer */}
          <motion.aside
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: 'spring', damping: 26, stiffness: 240 }}
            className="fixed top-0 bottom-0 left-0 w-84 bg-white border-r-2 border-zinc-950 z-50 flex flex-col shadow-2xl select-none"
          >
            {/* Brand Header */}
            <div className="h-16 flex items-center justify-between px-6 border-b-2 border-zinc-950 bg-zinc-950 text-white">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-red-600 text-white flex items-center justify-center font-mono font-black text-sm border border-red-500 shadow-xs">
                  SX
                </div>
                <div>
                  <h1 className="text-sm font-black tracking-wider text-white font-mono uppercase leading-tight">
                    SPECTRA<span className="text-red-500">/</span>XDR
                  </h1>
                  <p className="text-[10px] font-mono text-zinc-400 uppercase tracking-widest">
                    SWISS_ARCH_CORE // 2.0
                  </p>
                </div>
              </div>

              <button
                onClick={close}
                className="w-8 h-8 hover:bg-zinc-800 rounded-none border border-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition-colors cursor-pointer"
                title="Collapse Sidebar"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Navigation Section */}
            <div className="px-5 pt-4 pb-2 border-b border-zinc-200 bg-zinc-100 flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-zinc-900 tracking-wider">
                // SYSTEM_MODULES
              </span>
              <span className="text-[11px] font-mono font-bold px-2 py-0.5 bg-zinc-950 text-white">
                09 ACTIVE
              </span>
            </div>

            {/* Navigation List */}
            <nav className="flex-1 overflow-y-auto p-3 space-y-1.5 bg-zinc-50/50">
              {routes.map((route, idx) => {
                const isActive = pathname === route.path;
                const indexStr = String(idx + 1).padStart(2, '0');
                return (
                  <Link
                    key={route.path}
                    href={route.path}
                    onClick={close}
                    className={cn(
                      'group flex items-center justify-between px-3.5 py-3 transition-all border-2 text-sm',
                      isActive
                        ? 'bg-zinc-950 text-white font-bold border-zinc-950 shadow-md translate-x-1'
                        : 'bg-white text-zinc-800 font-medium hover:text-zinc-950 hover:bg-zinc-100 border-zinc-200 hover:border-zinc-400'
                    )}
                  >
                    <div className="flex items-center gap-3.5">
                      <div
                        className={cn(
                          'w-7 h-7 flex items-center justify-center transition-colors border',
                          isActive
                            ? 'bg-red-600 border-red-500 text-white'
                            : 'bg-zinc-100 border-zinc-200 text-zinc-700 group-hover:bg-zinc-200 group-hover:text-zinc-950'
                        )}
                      >
                        <route.icon className="w-4 h-4 stroke-[2.2]" />
                      </div>
                      <span className="text-[13px] tracking-tight font-semibold">
                        {route.name}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      {isActive && (
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping mr-1" />
                      )}
                      <span
                        className={cn(
                          'font-mono text-xs font-bold px-1.5 py-0.5',
                          isActive
                            ? 'bg-zinc-800 text-zinc-300'
                            : 'bg-zinc-100 text-zinc-500 group-hover:text-zinc-900'
                        )}
                      >
                        [{indexStr}]
                      </span>
                    </div>
                  </Link>
                );
              })}
            </nav>

            {/* Footer Telemetry */}
            <div className="p-4 border-t-2 border-zinc-950 bg-white font-mono">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-zinc-200">
                <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">
                  TELEMETRY
                </span>
                <span className="text-[11px] font-bold text-emerald-600 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  REALTIME_SYNC
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-600 font-medium">SOAR Pipeline:</span>
                <span className="font-bold text-zinc-950 px-1.5 py-0.5 bg-zinc-100 border border-zinc-300">
                  DEFENSE_READY
                </span>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
