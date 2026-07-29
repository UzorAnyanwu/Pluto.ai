import React from "react";
import { Sparkles } from "lucide-react";

interface CallToActionProps {
  onStartDemo: () => void;
}

export default function CallToAction({ onStartDemo }: CallToActionProps) {
  return (
    <section className="relative py-28 overflow-hidden bg-[#050505]">
      {/* Background radial soft gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(200,162,200,0.06)_0%,transparent_70%)] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10 w-[600px] h-[300px] rounded-full bg-accent/5 blur-3xl" />

      <div className="max-w-4xl mx-auto px-6 text-center relative z-10 space-y-8">
        
        <h2 className="text-3xl md:text-5xl font-medium font-sans text-white leading-tight tracking-tight">
          Ready to focus on your business?
        </h2>
        
        <p className="text-base md:text-lg text-white/60 max-w-xl mx-auto leading-relaxed font-light">
          Join the elite businesses scaling their inquiry capacity with Pluto AI.
        </p>

        <div className="pt-4 space-y-4">
          <button
            onClick={onStartDemo}
            className="inline-flex items-center gap-2 bg-accent hover:bg-accent/95 text-black font-semibold uppercase tracking-[0.15em] text-sm px-10 py-4.5 rounded-full shadow-[0_0_20px_rgba(200,162,200,0.3)] active:scale-[0.98] transition-all duration-200 cursor-pointer"
          >
            <Sparkles className="w-5 h-5 fill-black" />
            Start Free Trial Today
          </button>
          
          <p className="text-[10px] font-bold text-white/30 uppercase tracking-[0.2em]">
            No credit card required • Onboarding included
          </p>
        </div>

      </div>
    </section>
  );
}
