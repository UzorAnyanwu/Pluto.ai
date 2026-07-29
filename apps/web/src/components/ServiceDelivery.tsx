import React from "react";
import { Globe, BrainCircuit, ArrowRight } from "lucide-react";

interface ServiceDeliveryProps {
  onScrollToSandbox: () => void;
}

export default function ServiceDelivery({ onScrollToSandbox }: ServiceDeliveryProps) {
  return (
    <section id="features" className="py-24 bg-dark-bg border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6">
        
        {/* Title Block */}
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-4">
          <h2 className="text-3xl md:text-4xl font-extralight font-sans text-white tracking-tight">
            Intelligent <span className="font-normal">Service Delivery</span>
          </h2>
          <p className="text-base text-white/50 font-light leading-relaxed">
            Pluto AI handles the complex nuances of professional hospitality with human-like understanding for any SMB.
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Card 1: Multilingual Global Support */}
          <div className="p-8 rounded-3xl glass flex flex-col justify-between hover:border-accent/30 hover:bg-white/5 transition-all duration-300 group text-left">
            <div>
              <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-105 transition-transform duration-300">
                <Globe className="w-5 h-5 text-accent" />
              </div>
              <h3 className="text-xl font-medium text-white mb-3">
                Multilingual Global Support
              </h3>
              <p className="text-sm text-white/45 font-light leading-relaxed">
                Native-level fluency in over 50 languages. Provide premium, welcoming service to your international clientele without any staffing overhead or translation delays.
              </p>
            </div>
          </div>

          {/* Card 2: Smart Inquiry Triage (Elegant Dark Violet Glass) */}
          <div className="p-8 rounded-3xl border border-accent/20 bg-accent/5 text-white flex flex-col justify-between hover:border-accent/40 transition-all duration-300 group text-left relative overflow-hidden">
            {/* Subtle light background glow */}
            <div className="absolute top-0 right-0 -z-10 w-48 h-48 rounded-full bg-accent/10 blur-3xl" />
            
            <div className="space-y-6">
              <div className="w-12 h-12 bg-accent/15 border border-accent/25 rounded-2xl flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                <BrainCircuit className="w-5 h-5 text-accent" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-medium text-white">Smart Inquiry Triage</h3>
                <p className="text-sm text-white/70 font-light leading-relaxed">
                  Pluto AI understands customer intent in real-time. It instantly differentiates between a routine pricing inquiry, an urgent service complaint, and a high-value sales lead to prioritize properly.
                </p>
              </div>

              {/* Quick try-it CTA in-card */}
              <button
                onClick={onScrollToSandbox}
                className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.15em] text-accent hover:text-white transition-colors cursor-pointer group/btn pt-2"
              >
                Test Triage Engine Live
                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-1" />
              </button>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}

