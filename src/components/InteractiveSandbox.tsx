import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  Calendar,
  Database,
  PhoneCall,
  Send,
  RefreshCw,
  AlertTriangle,
  ChevronRight,
  User,
  CheckCircle,
  BrainCircuit,
  Maximize2,
  Clock,
  Briefcase,
  Smile,
  ShieldAlert,
  Sliders,
  PhoneOff,
  CalendarDays,
  FileText,
  UserCheck
} from "lucide-react";
import { PRESET_BUSINESSES, MOCK_TRIAGE_INQUIRIES, INITIAL_BOOKINGS, INITIAL_LEADS } from "../data";
import { BusinessProfile, Message, Booking, LeadInquiry } from "../types";
import { motion, AnimatePresence } from "motion/react";

export default function InteractiveSandbox() {
  // Preset Selection
  const [selectedProfile, setSelectedProfile] = useState<BusinessProfile>(PRESET_BUSINESSES[0]);
  
  // Tabs for mobile or workspace layout
  const [activeTab, setActiveTab] = useState<"simulator" | "triage" | "dashboard">("simulator");
  const [chatMode, setChatMode] = useState<"sms" | "call">("sms");
  
  // AI Chat state
  const [chatMessages, setChatMessages] = useState<Message[]>([
    {
      id: "initial",
      role: "assistant",
      text: "Hi there! Welcome to Zenith Wellness Spa. I'm Pluto, your virtual AI assistant. How can I help you today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isChatTyping, setIsChatTyping] = useState(false);
  const [callActive, setCallActive] = useState(false);
  const [callTranscription, setCallTranscription] = useState<string[]>([]);
  
  // Real-time Mock Database & CRM State
  const [bookingsList, setBookingsList] = useState<Booking[]>(INITIAL_BOOKINGS);
  const [leadsList, setLeadsList] = useState<LeadInquiry[]>(INITIAL_LEADS);
  const [showNotification, setShowNotification] = useState<string | null>(null);

  // Smart Triage state
  const [triageInput, setTriageInput] = useState(MOCK_TRIAGE_INQUIRIES[0].message);
  const [triageResult, setTriageResult] = useState<any>(null);
  const [isTriaging, setIsTriaging] = useState(false);

  // References
  const chatScrollRef = useRef<HTMLDivElement>(null);

  // Auto scroll chat
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages, isChatTyping]);

  // Handle business preset switch
  const handleProfileSwitch = (profile: BusinessProfile) => {
    setSelectedProfile(profile);
    setChatMessages([
      {
        id: `initial-${profile.id}`,
        role: "assistant",
        text: `Hi there! Welcome to ${profile.name}. I'm Pluto, your virtual AI receptionist. How can I help you today?`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
    setCallTranscription([]);
    setCallActive(false);
  };

  // Trigger brief alert notification
  const triggerNotification = (message: string) => {
    setShowNotification(message);
    setTimeout(() => setShowNotification(null), 4000);
  };

  // Perform lead triage in background
  const triggerBackgroundTriage = async (messageText: string) => {
    try {
      const response = await fetch("/api/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: messageText,
          businessContext: `${selectedProfile.name} is a ${selectedProfile.type}`
        })
      });
      if (response.ok) {
        const result = await response.json();
        const newLead: LeadInquiry = {
          id: `lead-${Date.now()}`,
          message: messageText,
          intent: result.intent,
          urgency: result.urgency,
          summary: result.summary,
          sentiment: result.sentiment,
          details: result.extractedDetails,
          timestamp: new Date().toISOString()
        };
        setLeadsList(prev => [newLead, ...prev]);
        triggerNotification(`Smart Triage: Classified as "${result.intent.replace('_', ' ')}" (${result.urgency} urgency)`);
      }
    } catch (err) {
      console.error("Background triage failed", err);
    }
  };

  // Send message to AI Chat Route
  const handleSendMessage = async (customMessage?: string) => {
    const textToSend = (customMessage || chatInput).trim();
    if (!textToSend || isChatTyping) return;

    if (!customMessage) {
      setChatInput("");
    }

    // Append user message
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setChatMessages(prev => [...prev, userMsg]);
    setIsChatTyping(true);

    // Format chat history for endpoint
    const historyPayload = chatMessages.map(msg => ({
      role: msg.role,
      text: msg.text
    }));

    try {
      // Trigger background smart triage on raw inquiry text for dashboard sync
      triggerBackgroundTriage(textToSend);

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: textToSend,
          history: historyPayload,
          businessProfile: selectedProfile
        })
      });

      if (!response.ok) {
        throw new Error("Failed to contact Pluto AI assistant");
      }

      const data = await response.json();
      
      const assistantMsg: Message = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        text: data.text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      // Check for function calling (mock booking trigger)
      if (data.functionCalls && data.functionCalls.length > 0) {
        const call = data.functionCalls[0];
        if (call.name === "bookAppointment") {
          const args = call.args;
          
          // Create real-time booking record
          const newBooking: Booking = {
            id: `bk-${Date.now()}`,
            customerName: args.customerName || "Valued Customer",
            phoneNumber: args.phoneNumber || "Captured on call",
            serviceRequested: args.serviceRequested || selectedProfile.services[0].name,
            dateTimeProposed: args.dateTimeProposed,
            createdAt: new Date().toISOString(),
            status: "confirmed"
          };

          setBookingsList(prev => [newBooking, ...prev]);
          
          // Append success indicator
          assistantMsg.isToolCall = true;
          assistantMsg.toolDetails = {
            customerName: newBooking.customerName,
            phoneNumber: newBooking.phoneNumber,
            serviceRequested: newBooking.serviceRequested,
            dateTimeProposed: newBooking.dateTimeProposed
          };

          triggerNotification(`🎉 Appointment Booked! ${newBooking.serviceRequested} on ${newBooking.dateTimeProposed}`);
        }
      }

      setChatMessages(prev => [...prev, assistantMsg]);
    } catch (error: any) {
      console.error(error);
      setChatMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          text: `I apologize, but I encountered an error. Please verify that your GEMINI_API_KEY is configured in Settings.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsChatTyping(false);
    }
  };

  // Perform Smart Triage Sandbox request
  const handlePerformTriage = async () => {
    if (!triageInput.trim() || isTriaging) return;
    setIsTriaging(true);

    try {
      const response = await fetch("/api/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: triageInput,
          businessContext: `${selectedProfile.name} is a ${selectedProfile.type}`
        })
      });

      if (!response.ok) {
        throw new Error("Failed to triage inquiry");
      }

      const result = await response.json();
      setTriageResult(result);

      // Add to Lead logs
      const triageLead: LeadInquiry = {
        id: `lead-sandbox-${Date.now()}`,
        message: triageInput,
        intent: result.intent,
        urgency: result.urgency,
        summary: result.summary,
        sentiment: result.sentiment,
        details: result.extractedDetails,
        timestamp: new Date().toISOString()
      };
      setLeadsList(prev => [triageLead, ...prev]);
      triggerNotification("Triage parsed! Lead added to CRM Pipeline.");
    } catch (error) {
      console.error(error);
      triggerNotification("Failed to triage. Ensure your API Key is valid.");
    } finally {
      setIsTriaging(false);
    }
  };

  // Pre-configured suggestions based on current business
  const getSuggestions = () => {
    switch (selectedProfile.id) {
      case "wellness-spa":
        return [
          "Book a Radiance Botanical Facial for Saturday",
          "Are you open on Sundays?",
          "How much is the Swedish Massage?"
        ];
      case "dental-clinic":
        return [
          "I want to book an exam and cleaning for Friday morning",
          "Is the Invisalign consultation free?",
          "What are your emergency care hours?"
        ];
      case "legal-firm":
        return [
          "Need a 30-minute consultation for business setup",
          "How much do you charge for trademarks?",
          "Do you review employment contracts?"
        ];
      case "auto-repair":
        return [
          "Schedule brake pad replacement for Wednesday afternoon",
          "Do you do Synthetic oil changes?",
          "How much is full health diagnostics?"
        ];
      default:
        return [];
    }
  };

  return (
    <section id="sandbox-section" className="py-20 bg-dark-bg border-b border-white/10 scroll-mt-16 text-white">
      <div className="max-w-7xl mx-auto px-6">
        
        {/* Intro Banner */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent/10 text-accent text-[10px] font-semibold uppercase tracking-[0.2em] border border-accent/20">
            <Sliders className="w-3.5 h-3.5 animate-spin-slow" />
            Pluto AI Live Sandbox Workspace
          </div>
          <h2 className="text-3xl md:text-5xl font-extralight font-sans text-white tracking-tight">
            Experience Pluto <span className="font-normal text-white">AI in Action</span>
          </h2>
          <p className="text-base text-white/50 font-light leading-relaxed">
            Test our core features live. Interact with Pluto AI under different business configurations, witness real-time CRM updates, and watch the Smart Triage engine extract structured leads instantly.
          </p>
        </div>

        {/* Global Floating Alerts */}
        <AnimatePresence>
          {showNotification && (
            <motion.div
              initial={{ opacity: 0, y: -20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.9 }}
              className="fixed top-20 right-6 z-50 max-w-sm bg-accent text-black font-semibold text-xs uppercase tracking-wider px-5 py-3.5 rounded-xl shadow-2xl flex items-center gap-3 border border-accent/30"
            >
              <CheckCircle className="w-5 h-5 shrink-0 text-black" />
              <span>{showNotification}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Bento Grid Sandbox Environment */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: Preset Switcher & Profile Details (4 Columns) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Presets Block */}
            <div className="glass rounded-3xl p-6 space-y-6 text-left">
              <div>
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-white/40 mb-1">
                  1. Choose Business Preset
                </h3>
                <p className="text-xs text-white/60 font-light">
                  Switch configurations instantly to see Pluto's adaptability.
                </p>
              </div>

              <div className="space-y-2.5">
                {PRESET_BUSINESSES.map((profile) => {
                  const isActive = selectedProfile.id === profile.id;
                  return (
                    <button
                      key={profile.id}
                      onClick={() => handleProfileSwitch(profile)}
                      className={`w-full flex items-center justify-between p-3.5 rounded-2xl border text-left transition-all cursor-pointer ${
                        isActive
                          ? "bg-accent/10 border-accent text-white font-semibold shadow-[0_0_15px_rgba(200,162,200,0.1)]"
                          : "bg-white/2 border-white/5 hover:border-white/15 text-white/80"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm transition-all ${
                            isActive ? "bg-accent text-black shadow-[0_0_10px_rgba(200,162,200,0.4)]" : "bg-white/5 border border-white/10 text-white/60"
                          }`}
                        >
                          {profile.name[0]}
                        </div>
                        <div>
                          <p className="text-sm font-semibold tracking-wide">{profile.name}</p>
                          <p className="text-[10px] text-white/40 uppercase tracking-widest">
                            {profile.type}
                          </p>
                        </div>
                      </div>
                      {isActive && <ChevronRight className="w-4 h-4 text-accent" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Profile Config Details Card */}
            <div className="glass rounded-3xl p-6 text-left space-y-5">
              <div className="flex items-center gap-2 border-b border-white/15 pb-3">
                <Briefcase className="w-4 h-4 text-accent" />
                <h4 className="text-[10px] font-bold uppercase tracking-widest text-accent">
                  Active Business Parameters
                </h4>
              </div>

              <div className="space-y-4 text-xs text-white/60">
                <div>
                  <p className="font-bold text-white/40 mb-1">Description</p>
                  <p className="leading-relaxed bg-white/3 p-3.5 rounded-xl border border-white/5 font-light">
                    {selectedProfile.description}
                  </p>
                </div>

                <div>
                  <p className="font-bold text-white/40 mb-1 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-accent" /> Operating Hours
                  </p>
                  <p className="font-medium text-white/80">{selectedProfile.hours}</p>
                </div>

                <div>
                  <p className="font-bold text-white/40 mb-2">Available Services & Rates</p>
                  <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                    {selectedProfile.services.map((s, idx) => (
                      <div
                        key={idx}
                        className="flex justify-between items-center bg-white/3 p-2.5 rounded-xl border border-white/5"
                      >
                        <span className="font-medium text-white/80 tracking-wide truncate max-w-[170px]">
                          {s.name}
                        </span>
                        <span className="font-bold text-accent shrink-0">{s.price}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Right Column: Central Tabs + Main Interactive Area (8 Columns) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* Desktop Tab Selector */}
            <div className="flex border border-white/10 bg-white/3 p-1.5 rounded-2xl gap-2">
              <button
                onClick={() => setActiveTab("simulator")}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-semibold uppercase tracking-[0.15em] transition-all cursor-pointer ${
                  activeTab === "simulator"
                    ? "bg-accent text-black shadow-[0_0_15px_rgba(200,162,200,0.35)]"
                    : "text-white/55 hover:text-white"
                }`}
              >
                <PhoneCall className="w-4 h-4" />
                AI Chat Simulator
              </button>
              
              <button
                onClick={() => setActiveTab("triage")}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-semibold uppercase tracking-[0.15em] transition-all cursor-pointer ${
                  activeTab === "triage"
                    ? "bg-accent text-black shadow-[0_0_15px_rgba(200,162,200,0.35)]"
                    : "text-white/55 hover:text-white"
                }`}
              >
                <BrainCircuit className="w-4 h-4" />
                Smart Triage
              </button>
              
              <button
                onClick={() => setActiveTab("dashboard")}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-xs font-semibold uppercase tracking-[0.15em] transition-all cursor-pointer ${
                  activeTab === "dashboard"
                    ? "bg-accent text-black shadow-[0_0_15px_rgba(200,162,200,0.35)]"
                    : "text-white/55 hover:text-white"
                }`}
              >
                <Database className="w-4 h-4" />
                Live CRM Sync
              </button>
            </div>

            {/* TAB CONTENT: 1. AI Receptionist Chat Simulator */}
            {activeTab === "simulator" && (
              <div className="glass rounded-3xl overflow-hidden flex flex-col h-[550px] relative text-left">
                {/* Simulator Header */}
                <div className="bg-[#050505]/80 backdrop-blur-md p-4 border-b border-white/10 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-2.5 h-2.5 rounded-full bg-accent animate-pulse" />
                    <div>
                      <h4 className="text-sm font-semibold tracking-wide text-white">{selectedProfile.name} Reception</h4>
                      <p className="text-[10px] text-white/40 uppercase tracking-widest font-light">Pluto AI Receptionist Active</p>
                    </div>
                  </div>
                  
                  {/* Mode Selector */}
                  <div className="flex bg-white/3 p-1 rounded-lg text-[10px] font-semibold uppercase tracking-wider border border-white/10">
                    <button
                      onClick={() => { setChatMode("sms"); setCallActive(false); }}
                      className={`px-3 py-1 rounded-md transition-colors cursor-pointer ${chatMode === "sms" ? "bg-accent text-black animate-pulse" : "text-white/40"}`}
                    >
                      SMS
                    </button>
                    <button
                      onClick={() => { setChatMode("call"); setCallActive(true); }}
                      className={`px-3 py-1 rounded-md transition-colors cursor-pointer ${chatMode === "call" ? "bg-accent text-black animate-pulse" : "text-white/40"}`}
                    >
                      Simulate Call
                    </button>
                  </div>
                </div>

                {/* Simulated Conversation Flow */}
                {chatMode === "sms" ? (
                  <>
                    <div ref={chatScrollRef} className="flex-1 overflow-y-auto p-6 space-y-4">
                      {chatMessages.map((msg) => {
                        const isAI = msg.role === "assistant";
                        return (
                          <div
                            key={msg.id}
                            className={`flex gap-3 max-w-[85%] ${isAI ? "mr-auto text-left" : "ml-auto flex-row-reverse text-right"}`}
                          >
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isAI ? "bg-accent/15 border border-accent/25 text-accent" : "bg-white/5 border border-white/10 text-white/85"}`}>
                              {isAI ? <Sparkles className="w-4 h-4 fill-accent" /> : <User className="w-4 h-4" />}
                            </div>
                            <div className="space-y-1">
                              <div className={`p-4 rounded-2xl leading-relaxed text-sm ${isAI ? "bg-white/3 border border-white/10 text-white" : "bg-accent text-black font-semibold"}`}>
                                <p>{msg.text}</p>
 
                                {/* Tool Booking visual trigger rendering */}
                                {msg.isToolCall && msg.toolDetails && (
                                  <div className="mt-3 p-3 bg-accent/10 border border-accent/20 rounded-xl space-y-1.5 text-xs text-accent">
                                    <div className="flex items-center gap-1.5 font-bold">
                                      <UserCheck className="w-3.5 h-3.5" /> Tool Executed: bookAppointment
                                    </div>
                                    <p className="opacity-80">Syncing with Calendar...</p>
                                    <div className="grid grid-cols-2 gap-2 text-[11px] pt-1 border-t border-emerald-500/20">
                                      <div>
                                        <p className="text-[10px] text-emerald-400 font-bold uppercase">Customer</p>
                                        <p className="font-semibold text-white">{msg.toolDetails.customerName || "Eleanor"}</p>
                                      </div>
                                      <div>
                                        <p className="text-[10px] text-emerald-400 font-bold uppercase">Proposed Slot</p>
                                        <p className="font-semibold text-white">{msg.toolDetails.dateTimeProposed}</p>
                                      </div>
                                    </div>
                                  </div>
                                )}
                              </div>
                              <span className="text-[10px] text-gray-500 block px-1">{msg.timestamp}</span>
                            </div>
                          </div>
                        );
                      })}

                      {isChatTyping && (
                        <div className="flex gap-3 max-w-[80%] mr-auto text-left">
                          <div className="w-8 h-8 rounded-full bg-accent/15 border border-accent/25 text-accent flex items-center justify-center animate-spin-slow">
                            <RefreshCw className="w-4 h-4" />
                          </div>
                          <div className="bg-white/3 border border-white/10 p-4 rounded-2xl flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-accent animate-bounce" />
                            <span className="w-2 h-2 rounded-full bg-accent animate-bounce delay-150" />
                            <span className="w-2 h-2 rounded-full bg-accent animate-bounce delay-300" />
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Suggestions list */}
                    <div className="px-6 py-2 border-t border-white/5 flex flex-wrap gap-2 bg-white/2">
                      {getSuggestions().map((sug, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSendMessage(sug)}
                          className="text-[11px] bg-white/3 border border-white/5 hover:border-accent/40 text-white/70 hover:text-white px-3.5 py-1.5 rounded-full transition-all cursor-pointer whitespace-nowrap"
                        >
                          {sug}
                        </button>
                      ))}
                    </div>

                    {/* Input Block */}
                    <div className="p-4 border-t border-white/10 bg-[#050505] flex gap-2">
                      <input
                        type="text"
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                        placeholder={`Ask or book with Pluto AI receptionist...`}
                        className="flex-1 bg-white/3 text-white rounded-xl px-4 py-3 border border-white/10 focus:outline-none focus:border-accent/50 text-sm font-light"
                      />
                      <button
                        onClick={() => handleSendMessage()}
                        className="bg-accent hover:bg-accent/95 text-black px-5 py-3 rounded-xl transition-all cursor-pointer flex items-center justify-center"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                  </>
                ) : (
                  /* Call mode simulation view */
                  <div className="flex-1 flex flex-col items-center justify-center p-8 space-y-8 bg-[radial-gradient(circle_at_center,rgba(200,162,200,0.12)_0%,transparent_70%)] relative">
                    <div className="absolute inset-0 bg-[#050505]/40 pointer-events-none" />

                    <div className="text-center space-y-3 relative z-10">
                      <div className="w-24 h-24 rounded-full bg-accent/15 border border-accent/20 flex items-center justify-center mx-auto relative">
                        <div className="w-16 h-16 rounded-full bg-accent flex items-center justify-center text-black shadow-xl shadow-accent/30">
                          <PhoneCall className="w-8 h-8 animate-pulse text-black" />
                        </div>
                        {/* Audio Pulse Rings */}
                        <span className="absolute inset-0 rounded-full border-2 border-accent/30 animate-ping" />
                      </div>
                      
                      <div className="space-y-1">
                        <h4 className="text-lg font-semibold text-white">{selectedProfile.name}</h4>
                        <p className="text-[10px] font-bold text-accent flex items-center justify-center gap-1.5 uppercase tracking-widest">
                          <span className="w-2 h-2 rounded-full bg-accent animate-ping" />
                          Pluto AI Active Call
                        </p>
                      </div>
                    </div>

                    {/* Styled Waveforms */}
                    <div className="flex items-center gap-1.5 h-12 w-full max-w-xs justify-center">
                      {[...Array(12)].map((_, i) => (
                        <span
                          key={i}
                          style={{ animationDelay: `${i * 120}ms` }}
                          className="w-1 bg-accent rounded-full animate-wave h-4"
                        />
                      ))}
                    </div>

                    <div className="space-y-4 text-center max-w-md">
                      <p className="text-sm text-white/60 font-light leading-relaxed">
                        "Hello! Welcome to {selectedProfile.name}. I'm Pluto AI. How may I assist you or coordinate your booking today?"
                      </p>
                      <button
                        onClick={() => { setChatMode("sms"); setCallActive(false); }}
                        className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-full text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 mx-auto shadow-lg shadow-red-950/40 cursor-pointer"
                      >
                        <PhoneOff className="w-4 h-4" />
                        End Call Simulation
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB CONTENT: 2. Smart Triage Sandbox */}
            {activeTab === "triage" && (
              <div className="glass rounded-3xl p-6 space-y-6 text-left">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-widest text-accent mb-1">
                    Smart Triage Playground
                  </h4>
                  <p className="text-xs text-white/50 font-light">
                    Input custom inquiries below to evaluate how Gemini extracts structures and evaluates urgency.
                  </p>
                </div>

                {/* Preconfigured templates list */}
                <div className="space-y-2">
                  <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Select Template to Load:</p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
                    {MOCK_TRIAGE_INQUIRIES.map((item, idx) => (
                      <button
                        key={idx}
                        onClick={() => setTriageInput(item.message)}
                        className="bg-white/3 border border-white/5 hover:border-accent/35 text-white/80 text-[11px] p-2.5 rounded-xl font-medium tracking-wide transition-colors cursor-pointer text-center truncate"
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Input Text Area */}
                <div className="space-y-2">
                  <textarea
                    value={triageInput}
                    onChange={(e) => setTriageInput(e.target.value)}
                    rows={4}
                    placeholder="Type or edit a customer inquiry message..."
                    className="w-full bg-white/3 border border-white/10 rounded-2xl p-4 text-sm text-white focus:outline-none focus:border-accent/40 leading-relaxed font-light"
                  />
                  <button
                    onClick={handlePerformTriage}
                    disabled={isTriaging}
                    className="w-full bg-white hover:bg-accent text-black font-semibold uppercase tracking-[0.15em] py-3.5 px-6 rounded-xl text-xs transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-white/5"
                  >
                    {isTriaging ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin text-black" />
                        Analyzing with Gemini...
                      </>
                    ) : (
                      <>
                        <BrainCircuit className="w-4 h-4 text-black" />
                        Run Smart Triage Analysis
                      </>
                    )}
                  </button>
                </div>

                {/* Triage Output Visual Blocks */}
                {triageResult && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass rounded-2xl p-6 space-y-6"
                  >
                    <div className="flex items-center justify-between border-b border-white/10 pb-3">
                      <span className="text-xs font-bold text-white/40 uppercase tracking-widest flex items-center gap-1.5">
                        <CheckCircle className="w-4 h-4 text-accent" /> Triage Output Result
                      </span>
                      <span className="text-[10px] text-accent font-mono uppercase tracking-widest">Status: PARSED</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Intent Card */}
                      <div className="bg-white/3 p-4 rounded-xl border border-white/5 text-center space-y-1">
                        <p className="text-[10px] text-white/40 uppercase tracking-widest font-bold">Intent</p>
                        <p className={`text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full inline-block ${
                          triageResult.intent === "sales_lead" ? "bg-accent/15 text-accent border border-accent/20" :
                          triageResult.intent === "booking_request" ? "bg-accent/15 text-accent border border-accent/20" :
                          triageResult.intent === "complaint" ? "bg-red-500/15 text-red-400 border border-red-500/20" :
                          "bg-white/5 text-white/80 border border-white/10"
                        }`}>
                          {triageResult.intent.replace('_', ' ')}
                        </p>
                      </div>

                      {/* Urgency Card */}
                      <div className="bg-white/3 p-4 rounded-xl border border-white/5 text-center space-y-2">
                        <p className="text-[10px] text-white/40 uppercase tracking-widest font-bold">Urgency</p>
                        <div className="flex items-center justify-center gap-1 bg-white/2 p-1.5 rounded-lg border border-white/5">
                          <span className={`w-2 h-2 rounded-full ${triageResult.urgency === "high" ? "bg-red-500 animate-pulse" : triageResult.urgency === "medium" ? "bg-orange-400" : "bg-accent"}`} />
                          <p className="text-xs font-bold uppercase tracking-wider text-white">
                            {triageResult.urgency}
                          </p>
                        </div>
                      </div>

                      {/* Sentiment Card */}
                      <div className="bg-white/3 p-4 rounded-xl border border-white/5 text-center space-y-1">
                        <p className="text-[10px] text-white/40 uppercase tracking-widest font-bold">Sentiment</p>
                        <div className="flex items-center justify-center gap-2 py-1">
                          <Smile className={`w-5 h-5 ${triageResult.sentiment === "positive" ? "text-accent" : triageResult.sentiment === "negative" ? "text-red-400" : "text-yellow-400"}`} />
                          <span className="text-xs font-bold uppercase tracking-wider text-white">
                            {triageResult.sentiment}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Summary Row */}
                    <div className="space-y-1.5">
                      <p className="text-[10px] text-white/40 uppercase tracking-widest font-bold">Inquiry Summary</p>
                      <p className="text-sm font-light text-white/95 bg-white/2 p-3.5 rounded-xl border border-white/5 leading-relaxed">
                        {triageResult.summary}
                      </p>
                    </div>

                    {/* Extracted details table */}
                    <div className="space-y-2">
                      <p className="text-[10px] text-white/40 uppercase tracking-widest font-bold">Extracted Lead Parameters</p>
                      <div className="bg-white/2 rounded-xl border border-white/5 overflow-hidden text-xs">
                        <table className="w-full text-left">
                          <thead>
                            <tr className="border-b border-white/10 bg-[#050505]/40 text-white/40 font-bold uppercase tracking-widest text-[10px]">
                              <th className="p-3">Entity Name</th>
                              <th className="p-3">Extracted Value</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-white/5 font-medium text-white/80">
                            <tr>
                              <td className="p-3 text-white/40">Client Name</td>
                              <td className="p-3 font-light">{triageResult.extractedDetails.name || <span className="text-white/20 font-semibold uppercase tracking-widest text-[9px]">Not Found</span>}</td>
                            </tr>
                            <tr>
                              <td className="p-3 text-white/40">Phone Number</td>
                              <td className="p-3 font-mono text-white/70">{triageResult.extractedDetails.phone || <span className="text-white/20 font-semibold uppercase tracking-widest text-[9px]">Not Found</span>}</td>
                            </tr>
                            <tr>
                              <td className="p-3 text-white/40">Email Address</td>
                              <td className="p-3 font-light text-white/70">{triageResult.extractedDetails.email || <span className="text-white/20 font-semibold uppercase tracking-widest text-[9px]">Not Found</span>}</td>
                            </tr>
                            <tr>
                              <td className="p-3 text-white/40">Proposed Slot</td>
                              <td className="p-3 text-accent font-semibold">{triageResult.extractedDetails.dateTimeProposed || <span className="text-white/20 font-semibold uppercase tracking-widest text-[9px]">Not Found</span>}</td>
                            </tr>
                            <tr>
                              <td className="p-3 text-white/40">Service Requested</td>
                              <td className="p-3 font-semibold text-white">{triageResult.extractedDetails.serviceRequested || <span className="text-white/20 font-semibold uppercase tracking-widest text-[9px]">Not Found</span>}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            )}

            {/* TAB CONTENT: 3. CRM & Live Data Sync */}
            {activeTab === "dashboard" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Bookings Calendar Sync Block */}
                <div className="glass rounded-3xl p-6 text-left space-y-4">
                  <div className="flex items-center justify-between border-b border-white/10 pb-3">
                    <span className="text-xs font-bold uppercase tracking-widest text-accent flex items-center gap-1.5">
                      <CalendarDays className="w-4 h-4" /> Live Calendar
                    </span>
                    <span className="text-[9px] bg-accent/15 text-accent border border-accent/25 px-2 py-0.5 rounded-full font-bold uppercase tracking-widest">
                      Synced
                    </span>
                  </div>

                  <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
                    {bookingsList.map((bk) => (
                      <div
                        key={bk.id}
                        className="bg-white/3 border border-white/5 p-4 rounded-2xl space-y-3"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h5 className="font-semibold text-sm text-white">{bk.customerName}</h5>
                            <p className="text-xs text-white/45 font-light font-mono">{bk.phoneNumber}</p>
                          </div>
                          <span className="text-[9px] bg-accent text-black px-2 py-0.5 rounded-md font-bold uppercase tracking-widest">
                            {bk.status}
                          </span>
                        </div>

                        <div className="p-2.5 bg-white/2 rounded-xl border border-white/5 text-xs text-white/70">
                          <p className="font-semibold text-white">{bk.serviceRequested}</p>
                          <p className="text-accent font-medium mt-1 font-mono text-[11px]">{bk.dateTimeProposed}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* CRM Leads Pipeline Sync Block */}
                <div className="glass rounded-3xl p-6 text-left space-y-4">
                  <div className="flex items-center justify-between border-b border-white/10 pb-3">
                    <span className="text-xs font-bold uppercase tracking-widest text-accent flex items-center gap-1.5">
                      <FileText className="w-4 h-4" /> CRM Pipeline
                    </span>
                    <span className="text-[9px] bg-white/10 text-white/80 border border-white/10 px-2 py-0.5 rounded-full font-bold uppercase tracking-widest">
                      Leads
                    </span>
                  </div>

                  <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
                    {leadsList.map((ld) => (
                      <div
                        key={ld.id}
                        className="bg-white/3 border border-white/5 p-4 rounded-2xl space-y-3 text-xs"
                      >
                        <div className="flex justify-between items-center">
                          <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded border ${
                            ld.intent === "sales_lead" ? "bg-accent/10 text-accent border-accent/25" :
                            ld.intent === "booking_request" ? "bg-accent/10 text-accent border-accent/25" :
                            ld.intent === "complaint" ? "bg-red-500/10 text-red-400 border-red-500/25" :
                            "bg-white/5 text-white/80 border-white/10"
                          }`}>
                            {ld.intent.replace('_', ' ')}
                          </span>

                          <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded ${
                            ld.urgency === "high" ? "bg-red-500/20 text-red-400" : "bg-white/5 text-white/40"
                          }`}>
                            {ld.urgency} Urgency
                          </span>
                        </div>

                        <div>
                          <p className="font-semibold text-white mb-1 leading-snug">{ld.summary}</p>
                          <p className="text-[11px] text-white/50 italic font-light">"{ld.message}"</p>
                        </div>

                        {/* Extracted Details */}
                        <div className="grid grid-cols-2 gap-2 text-[10px] border-t border-white/5 pt-2 text-white/70">
                          <div>
                            <span className="text-white/30 font-bold uppercase text-[8px] tracking-widest block">Customer</span>
                            <span className="font-semibold text-white/90">{ld.details.name || ld.details.phone || "Guest"}</span>
                          </div>
                          <div>
                            <span className="text-white/30 font-bold uppercase text-[8px] tracking-widest block">Extracted Slot</span>
                            <span className="font-semibold text-accent truncate block font-mono">{ld.details.dateTimeProposed || "N/A"}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

          </div>

        </div>

      </div>
    </section>
  );
}
