import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import dotenv from "dotenv";
import { GoogleGenAI, Type, FunctionDeclaration } from "@google/genai";

dotenv.config();

// Lazily initialize Gemini AI client to prevent crash if API key is missing on startup
let aiClient: GoogleGenAI | null = null;

function getGeminiClient(): GoogleGenAI {
  if (!aiClient) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey || apiKey === "MY_GEMINI_API_KEY") {
      throw new Error("GEMINI_API_KEY environment variable is not configured in Secrets.");
    }
    aiClient = new GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build",
        },
      },
    });
  }
  return aiClient;
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API: Health check
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", time: new Date().toISOString() });
  });

  // API: Triage incoming inquiry (Smart Inquiry Triage)
  app.post("/api/triage", async (req, res) => {
    try {
      const { message, businessContext } = req.body;
      if (!message) {
        return res.status(400).json({ error: "Message is required" });
      }

      const ai = getGeminiClient();
      const prompt = `
        You are Pluto AI's Smart Triage engine. Analyze the following incoming inquiry for a business.
        Business context: ${businessContext || "A small business"}
        
        Customer Message: "${message}"

        Deconstruct this message into a JSON response with the following fields:
        - "intent": Must be one of ["pricing_inquiry", "booking_request", "complaint", "sales_lead", "general_support"]
        - "urgency": Must be one of ["high", "medium", "low"]
        - "summary": A brief 1-sentence summary of what the customer wants.
        - "sentiment": Must be one of ["positive", "neutral", "negative"]
        - "extractedDetails": An object containing any extracted keys: "name", "phone", "email", "dateTimeProposed", "serviceRequested". Use null if not found.
      `;

      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: prompt,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              intent: {
                type: Type.STRING,
                description: "The primary intention of the user message.",
              },
              urgency: {
                type: Type.STRING,
                description: "Urgency level of the request.",
              },
              summary: {
                type: Type.STRING,
                description: "One-sentence summary.",
              },
              sentiment: {
                type: Type.STRING,
                description: "Detected emotional tone.",
              },
              extractedDetails: {
                type: Type.OBJECT,
                properties: {
                  name: { type: Type.STRING },
                  phone: { type: Type.STRING },
                  email: { type: Type.STRING },
                  dateTimeProposed: { type: Type.STRING },
                  serviceRequested: { type: Type.STRING },
                },
              },
            },
            required: ["intent", "urgency", "summary", "sentiment", "extractedDetails"],
          },
        },
      });

      const resultText = response.text;
      if (!resultText) {
        throw new Error("Empty response from AI model");
      }
      res.json(JSON.parse(resultText.trim()));
    } catch (error: any) {
      console.error("Triage Error:", error);
      res.status(500).json({ error: error.message || "Failed to process triage analysis" });
    }
  });

  // API: Interactive AI Chat Receptionist
  app.post("/api/chat", async (req, res) => {
    try {
      const { message, history, businessProfile } = req.body;
      if (!message) {
        return res.status(400).json({ error: "Message is required" });
      }

      const ai = getGeminiClient();

      const defaultProfile = {
        name: "Pluto AI Receptionist Demo",
        type: "Wellness Spa",
        hours: "Mon-Fri 9am-6pm, Sat 10am-4pm",
        description: "A luxury wellness center offering massages, facials, and relaxation treatments.",
        services: [
          { name: "Swedish Massage (60 mins)", price: "$95" },
          { name: "Deep Tissue Massage (60 mins)", price: "$120" },
          { name: "Hydrating Facial (45 mins)", price: "$80" },
        ],
      };

      const profile = businessProfile || defaultProfile;

      // Define booking tool
      const bookAppointmentTool: FunctionDeclaration = {
        name: "bookAppointment",
        description: "Call this function when the customer explicitly asks to book or schedule an appointment and has specified a service and date/time.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            customerName: { type: Type.STRING, description: "The customer's name if provided." },
            phoneNumber: { type: Type.STRING, description: "The customer's phone number if provided." },
            serviceRequested: { type: Type.STRING, description: "The specific service being booked." },
            dateTimeProposed: { type: Type.STRING, description: "The date and time proposed for the booking." },
          },
          required: ["serviceRequested", "dateTimeProposed"],
        },
      };

      // Formulate system instructions
      const systemInstruction = `
        You are Pluto AI, the premium AI receptionist for "${profile.name}" (${profile.type}).
        
        Business details:
        - Description: ${profile.description}
        - Operating Hours: ${profile.hours}
        - Services offered:
          ${JSON.stringify(profile.services, null, 2)}
        
        Your goals:
        1. Welcome the customer politely, and maintain a highly professional, helpful, and friendly tone.
        2. Keep your answers concise, natural, and engaging, as if typing over SMS/WhatsApp or speaking on a quick call. Keep responses under 2-3 sentences where possible.
        3. If the user wants to book or schedule an appointment, ask for their name, phone number, preferred service, and date/time if not already provided.
        4. Once you have a service and date/time proposed, trigger the "bookAppointment" tool.
        5. If they ask questions about services, hours, or general questions, answer them accurately based on the business details. Do not make up information.
      `;

      // Build chat prompt format or use generateContent
      // Since @google/genai SDK chats structure is simple, let's use generateContent with history formatted for reliability
      const formattedContents: any[] = [];
      
      if (history && Array.isArray(history)) {
        history.forEach((turn: any) => {
          formattedContents.push({
            role: turn.role === "user" ? "user" : "model",
            parts: [{ text: turn.text }],
          });
        });
      }

      // Add current message
      formattedContents.push({
        role: "user",
        parts: [{ text: message }],
      });

      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: formattedContents,
        config: {
          systemInstruction,
          tools: [{ functionDeclarations: [bookAppointmentTool] }],
        },
      });

      const text = response.text || "";
      const functionCalls = response.functionCalls || null;

      res.json({
        text,
        functionCalls,
      });
    } catch (error: any) {
      console.error("Chat Error:", error);
      res.status(500).json({ error: error.message || "Failed to process chat response" });
    }
  });

  // Vite middleware or static files serving
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
