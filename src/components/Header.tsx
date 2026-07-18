import React from "react";
import { Sparkles } from "lucide-react";

interface HeaderProps {
  onOpenSandbox: () => void;
}

export default function Header({ onOpenSandbox }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-dark-bg/60 backdrop-blur-md border-b border-white/10 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-black font-bold text-sm shadow-[0_0_15px_rgba(200,162,200,0.4)] group-hover:scale-105 transition-transform">
            P
          </div>
          <span className="font-sans font-light text-lg tracking-[0.25em] uppercase text-white">
            Pluto <span className="text-accent font-semibold">AI</span>
          </span>
        </a>

        {/* Navigation links */}
        <nav className="hidden md:flex items-center gap-8">
          <a
            href="#features"
            className="text-[11px] uppercase tracking-[0.2em] font-light text-white/50 hover:text-white transition-colors"
          >
            Features
          </a>
          <a
            href="#infrastructure"
            className="text-[11px] uppercase tracking-[0.2em] font-light text-white/50 hover:text-white transition-colors"
          >
            Technical
          </a>
          <a
            href="#testimonials"
            className="text-[11px] uppercase tracking-[0.2em] font-light text-white/50 hover:text-white transition-colors"
          >
            Testimonials
          </a>
          <a
            href="#sandbox-section"
            className="text-[11px] uppercase tracking-[0.2em] font-semibold text-accent hover:text-white transition-colors flex items-center gap-1"
          >
            <Sparkles className="w-3.5 h-3.5 animate-pulse" />
            Interactive Demo
          </a>
        </nav>

        {/* Action Button */}
        <div className="flex items-center">
          <button
            onClick={onOpenSandbox}
            className="px-6 py-2.5 rounded-full border border-white/20 text-[10px] font-semibold uppercase tracking-[0.2em] text-white hover:bg-accent hover:text-black hover:border-accent transition-all duration-300 cursor-pointer shadow-[0_0_15px_rgba(255,255,255,0.02)]"
          >
            Launch Demo
          </button>
        </div>
      </div>
    </header>
  );
}

