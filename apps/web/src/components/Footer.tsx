import React from "react";
import { Globe, MessageSquare } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-[#050505] border-t border-white/5 relative z-10">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          
          {/* Brand & Copyright */}
          <div className="text-center md:text-left space-y-1">
            <h3 className="text-sm font-semibold tracking-wider text-white uppercase">Pluto AI</h3>
            <p className="text-xs text-white/40 font-light">
              © 2026 Pluto AI. All rights reserved.
            </p>
          </div>

          {/* Links */}
          <div className="flex flex-wrap justify-center gap-8 text-xs font-semibold uppercase tracking-wider text-white/50">
            <a href="#features" className="hover:text-accent transition-colors">
              Features
            </a>
            <a href="#" className="hover:text-accent transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-accent transition-colors">
              Terms of Service
            </a>
            <a href="#" className="hover:text-accent transition-colors">
              Contact Us
            </a>
          </div>

          {/* Social Icons */}
          <div className="flex gap-4">
            <a
              href="#"
              className="w-10 h-10 rounded-full bg-white/3 border border-white/10 flex items-center justify-center text-white/50 hover:text-accent hover:border-accent/40 hover:bg-white/5 transition-all"
            >
              <Globe className="w-4 h-4" />
            </a>
            <a
              href="#"
              className="w-10 h-10 rounded-full bg-white/3 border border-white/10 flex items-center justify-center text-white/50 hover:text-accent hover:border-accent/40 hover:bg-white/5 transition-all"
            >
              <MessageSquare className="w-4 h-4" />
            </a>
          </div>

        </div>
      </div>
    </footer>
  );
}
