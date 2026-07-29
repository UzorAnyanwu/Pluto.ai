import React from "react";
import { Quote } from "lucide-react";

export default function Testimonials() {
  return (
    <section id="testimonials" className="py-24 bg-dark-bg border-b border-white/5 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(200,162,200,0.03),transparent_40%)] pointer-events-none" />
      <div className="max-w-7xl mx-auto px-6 relative z-10">
        
        {/* Title */}
        <div className="text-center mb-16 space-y-3">
          <p className="text-accent text-[10px] font-bold uppercase tracking-[0.2em]">Success Stories</p>
          <h2 className="text-3xl md:text-4xl font-semibold font-sans text-white tracking-tight">
            The Gold Standard
          </h2>
        </div>

        {/* Grid layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Testimonial 1 */}
          <div className="p-8 rounded-3xl border border-white/10 glass relative border-l-4 border-l-accent overflow-hidden text-left duration-300">
            {/* Soft decorative large quote sign */}
            <Quote className="w-16 h-16 text-accent/5 absolute -top-1 -right-1 scale-150 rotate-12" />
            
            <div className="space-y-6 relative z-10">
              <p className="text-base text-white/80 font-light italic leading-relaxed">
                "Pluto AI has transformed our agency operations. We no longer worry about missed calls during peak hours or after-hours inquiries. Our team can focus on client strategy while the AI handles the logistics seamlessly."
              </p>
              
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full overflow-hidden border border-white/15">
                  <img
                    alt="Sarah J."
                    referrerPolicy="no-referrer"
                    className="w-full h-full object-cover"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuBhw54O94KVjvFI6hrTtE0J4dqtNKRxZJArJK_JupbQOUemMHh7tkJlr5T1NuRQBr4yEKLgp1CW-LhXARMfVPea5lw9ExfFP22D3dokVeqLWaGibNHXQgqGdmvvBRdCBS6sjGJl2MzNRqeKAuiTbNa6eD_t0dVaFJGJIESm6mf1v4d-5v0wyq6LdXl4fhul9CZy2cFsUaaCp_ebtrMfo7ubKzSSlZh0izTaZCWeBg92KR_CZHSIVVsW"
                  />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Sarah J.</p>
                  <p className="text-xs text-white/40 uppercase tracking-wider">
                    Marketing Agency Director
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Testimonial 2 */}
          <div className="p-8 rounded-3xl border border-white/10 glass relative border-l-4 border-l-accent overflow-hidden text-left duration-300">
            {/* Soft decorative large quote sign */}
            <Quote className="w-16 h-16 text-accent/5 absolute -top-1 -right-1 scale-150 rotate-12" />
            
            <div className="space-y-6 relative z-10">
              <p className="text-base text-white/80 font-light italic leading-relaxed">
                "The AI is surprisingly intuitive. Our clients love getting instant answers even late at night. It’s significantly increased our conversion rate for new project inquiries across the board."
              </p>
              
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full overflow-hidden border border-white/15">
                  <img
                    alt="Dr. Michael Chen"
                    referrerPolicy="no-referrer"
                    className="w-full h-full object-cover"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuAPMZhbmek9m6Jj_7qcm45VFGMAMG5ffFgjpOXhzq6i3uD8fBjS_pNOx9g00bleoDMxF66bVFXgsu0nS_4fKP9lMENCCpnDEPA2M71TlnTNjdBBYld4fQtLJ3chFEAU4VkV31stNA5bOemZiK-eM2xqy6uO3-_lyWzDhWGmrWzQuTyUMtbSrRoBe49GL6bjRTfYBUspK_3eQZDb6gm3JoUeuBw-diVijmtY7EdDZBK8KzvOUjnRyZm_"
                  />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Michael Chen</p>
                  <p className="text-xs text-white/40 uppercase tracking-wider">
                    Consultancy Principal
                  </p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
