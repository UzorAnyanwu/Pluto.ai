import React from "react";
import { GitCompare, Calendar, Database, PhoneCall, Code, ArrowRight } from "lucide-react";

export default function Infrastructure() {
  return (
    <section id="infrastructure" className="py-24 bg-dark-bg border-y border-white/10">
      <div className="max-w-7xl mx-auto px-6">
        
        {/* Header Block */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-16">
          <div className="max-w-2xl text-left">
            <h2 className="text-3xl md:text-4xl font-extralight font-sans text-white tracking-tight mb-4">
              Enterprise-Grade <span className="font-normal text-white">Infrastructure</span>
            </h2>
            <p className="text-base text-white/50 font-light leading-relaxed">
              Pluto AI isn't just a chatbot. It's a robust technical layer that sits between your callers and your existing business ecosystem, across any industry.
            </p>
          </div>
          <div className="hidden md:block">
            <a
              href="#sandbox-section"
              className="text-accent hover:text-white font-semibold text-xs uppercase tracking-[0.2em] flex items-center gap-1 group transition-colors"
            >
              View Developer Demo
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </a>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          
          {/* Card 1: CRM Support */}
          <div className="p-8 rounded-2xl glass hover:border-accent/30 hover:bg-white/5 transition-all duration-300 group text-left">
            <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center mb-6 group-hover:scale-105 transition-transform duration-300">
              <GitCompare className="w-5 h-5 text-accent" />
            </div>
            <h3 className="text-lg font-medium text-white mb-3">CRM Support</h3>
            <p className="text-sm text-white/45 font-light leading-relaxed">
              Seamlessly syncing with major business CRMs including Salesforce, HubSpot, and Pipedrive. Your customer data stays unified and accurate.
            </p>
          </div>

          {/* Card 2: Calendar Integration */}
          <div className="p-8 rounded-2xl glass hover:border-accent/30 hover:bg-white/5 transition-all duration-300 group text-left">
            <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center mb-6 group-hover:scale-105 transition-transform duration-300">
              <Calendar className="w-5 h-5 text-accent" />
            </div>
            <h3 className="text-lg font-medium text-white mb-3">Calendar Integration</h3>
            <p className="text-sm text-white/45 font-light leading-relaxed">
              Real-time booking across Google, Outlook, and Calendly. Avoid double-bookings with millisecond latency checks on availability.
            </p>
          </div>

          {/* Card 3: Database Management */}
          <div className="p-8 rounded-2xl glass hover:border-accent/30 hover:bg-white/5 transition-all duration-300 group text-left">
            <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center mb-6 group-hover:scale-105 transition-transform duration-300">
              <Database className="w-5 h-5 text-accent" />
            </div>
            <h3 className="text-lg font-medium text-white mb-3">Database Management</h3>
            <p className="text-sm text-white/45 font-light leading-relaxed">
              Secure, organized client data handling. Every interaction is encrypted and stored in compliance with enterprise security and privacy standards.
            </p>
          </div>

          {/* Card 4: Phone Systems */}
          <div className="p-8 rounded-2xl glass hover:border-accent/30 hover:bg-white/5 transition-all duration-300 group text-left">
            <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center mb-6 group-hover:scale-105 transition-transform duration-300">
              <PhoneCall className="w-5 h-5 text-accent" />
            </div>
            <h3 className="text-lg font-medium text-white mb-3">Phone Systems</h3>
            <p className="text-sm text-white/45 font-light leading-relaxed">
              Integrating with existing VoIP, RingCentral, and analog phone lines. We provide dedicated virtual numbers or SIP trunking for your current hardware.
            </p>
          </div>

          {/* Card 5: Flexible APIs (Span 2 columns on desktop) */}
          <div className="p-8 rounded-2xl glass hover:border-accent/30 hover:bg-white/5 transition-all duration-300 group md:col-span-2 text-left">
            <div className="flex flex-col md:flex-row gap-8 items-center justify-between">
              
              <div className="flex-1 space-y-4">
                <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                  <Code className="w-5 h-5 text-accent" />
                </div>
                <h3 className="text-lg font-medium text-white mb-3">Flexible APIs</h3>
                <p className="text-sm text-white/45 font-light leading-relaxed">
                  For diverse custom workflows and specific industry needs. Build unique front-end experiences or connect Pluto AI to proprietary internal software with our RESTful API.
                </p>
              </div>

              {/* API UI representation */}
              <div className="hidden md:block w-52 h-36 bg-white/3 rounded-2xl border border-dashed border-white/10 p-5 space-y-3.5 select-none relative overflow-hidden shrink-0">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-white/10" />
                  <span className="w-2 h-2 rounded-full bg-white/10" />
                  <span className="w-2 h-2 rounded-full bg-white/10" />
                </div>
                <div className="space-y-2">
                  <div className="h-2 w-full bg-white/5 rounded-full" />
                  <div className="h-2 w-4/5 bg-accent/20 rounded-full" />
                  <div className="h-2 w-11/12 bg-white/5 rounded-full" />
                  <div className="h-2 w-2/3 bg-white/5 rounded-full" />
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </section>
  );
}

