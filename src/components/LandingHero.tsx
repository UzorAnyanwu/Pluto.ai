import React from "react";
import { Sparkles, Play, CheckCircle2 } from "lucide-react";
import { motion } from "motion/react";

interface LandingHeroProps {
  onStartDemo: () => void;
  onOpenSandbox: () => void;
}

export default function LandingHero({ onStartDemo, onOpenSandbox }: LandingHeroProps) {
  return (
    <section className="relative overflow-hidden bg-dark-bg py-20 lg:py-28 text-white">
      {/* Background radial soft light */}
      <div className="absolute top-0 right-0 -z-10 w-[500px] h-[500px] rounded-full bg-accent/5 blur-[120px]" />
      <div className="absolute bottom-0 left-0 -z-10 w-[350px] h-[350px] rounded-full bg-white/3 blur-[100px]" />

      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">
          
          {/* Left Text Column */}
          <div className="lg:col-span-5 space-y-8 text-left">
            {/* Tag Badge */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-accent/10 text-accent text-[10px] font-semibold uppercase tracking-[0.2em] border border-accent/20"
            >
              <Sparkles className="w-3 h-3 fill-accent" />
              The Intelligence Layer for SMBs
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-5xl md:text-6xl font-extralight font-sans tracking-tight leading-[1.05]"
            >
              Never Miss a <br />
              <span className="text-white font-normal">Lead Again.</span> <br />
              <span className="text-white/40 italic font-light tracking-wide">
                Pluto AI Receptionist
              </span>
            </motion.h1>

            {/* Subheading Description */}
            <motion.p
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-base text-white/50 font-light leading-relaxed max-w-xl"
            >
              The premium, professional AI receptionist built for small and medium businesses to handle inquiries, bookings, and customer support with native-level accuracy 24/7.
            </motion.p>

            {/* Call to Actions */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-4 pt-2"
            >
              <button
                onClick={onStartDemo}
                className="bg-white hover:bg-accent text-black font-semibold text-xs uppercase tracking-[0.15em] px-8 py-4 rounded-full transition-all duration-300 shadow-[0_0_15px_rgba(255,255,255,0.05)] cursor-pointer"
              >
                Start Free Trial
              </button>
              <button
                onClick={onOpenSandbox}
                className="border border-white/20 hover:border-accent hover:bg-accent/5 text-white font-semibold text-xs uppercase tracking-[0.15em] px-8 py-4 rounded-full transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5 fill-white text-white" />
                Private Demo
              </button>
            </motion.div>

            {/* Trust Footer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="flex items-center gap-4 pt-6 border-t border-white/10"
            >
              <div className="flex -space-x-2.5">
                <img
                  className="w-8 h-8 rounded-full border border-dark-bg bg-slate-800 object-cover"
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=100"
                  alt="Sarah J."
                />
                <img
                  className="w-8 h-8 rounded-full border border-dark-bg bg-slate-850 object-cover"
                  src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=100"
                  alt="Michael C."
                />
                <img
                  className="w-8 h-8 rounded-full border border-dark-bg bg-slate-900 object-cover"
                  src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=100"
                  alt="Lillian B."
                />
              </div>
              <p className="text-[10px] font-semibold text-white/40 uppercase tracking-[0.15em]">
                Trusted by 500+ premium wellness & medical clinics
              </p>
            </motion.div>
          </div>

          {/* Right Image/Mockup Column */}
          <div className="lg:col-span-7 relative flex justify-center">
            {/* Container for the illustration / mockup */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative w-full max-w-2xl aspect-[16/11] rounded-3xl overflow-hidden shadow-2xl border border-white/10 bg-slate-900 group"
            >
              <img
                alt="Modern professional office workspace"
                className="w-full h-full object-cover aspect-[16/11] transition-transform duration-700 group-hover:scale-102 opacity-75"
                src="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80&w=1000"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-dark-bg/80 via-dark-bg/10 to-transparent" />

              {/* Floating Status Card */}
              <div className="absolute bottom-6 left-6 md:bottom-8 md:left-8 glass px-5 py-3.5 rounded-2xl shadow-2xl flex items-center gap-3.5 hover:scale-[1.02] transition-transform duration-300">
                <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-black shadow-lg">
                  <CheckCircle2 className="w-4 h-4 text-black" />
                </div>
                <div className="text-left">
                  <p className="text-[9px] font-bold text-accent uppercase tracking-wider">
                    Pluto AI Active
                  </p>
                  <p className="text-xs font-semibold tracking-wide text-white">
                    Nodes Fully Optimized
                  </p>
                </div>
              </div>
            </motion.div>
          </div>

        </div>
      </div>
    </section>
  );
}

