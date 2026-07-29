import React from "react";
import Header from "./components/Header";
import LandingHero from "./components/LandingHero";
import Infrastructure from "./components/Infrastructure";
import InteractiveSandbox from "./components/InteractiveSandbox";
import ServiceDelivery from "./components/ServiceDelivery";
import Testimonials from "./components/Testimonials";
import CallToAction from "./components/CallToAction";
import Footer from "./components/Footer";

export default function App() {
  const scrollToSandbox = () => {
    const element = document.getElementById("sandbox-section");
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-800">
      {/* Brand Navigation Header */}
      <Header onOpenSandbox={scrollToSandbox} />

      <main className="flex-1">
        {/* Landing Hero Section */}
        <LandingHero onStartDemo={scrollToSandbox} onOpenSandbox={scrollToSandbox} />

        {/* Enterprise Infrastructure Grid Block */}
        <Infrastructure />

        {/* Intelligent Service Delivery Feature Callouts */}
        <ServiceDelivery onScrollToSandbox={scrollToSandbox} />

        {/* Interactive Sandbox Workspace (Live AI Chat, Triage & CRM Sync) */}
        <InteractiveSandbox />

        {/* Testimonials Showcase */}
        <Testimonials />

        {/* Core Conversion Call to Action */}
        <CallToAction onStartDemo={scrollToSandbox} />
      </main>

      {/* Structured Site Footer */}
      <Footer />
    </div>
  );
}
