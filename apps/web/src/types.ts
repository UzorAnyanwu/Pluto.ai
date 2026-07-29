export interface ServiceItem {
  name: string;
  price: string;
}

export interface BusinessProfile {
  id: string;
  name: string;
  type: string;
  hours: string;
  description: string;
  services: ServiceItem[];
  icon: string; // Lucide icon identifier
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: string;
  isToolCall?: boolean;
  toolDetails?: {
    customerName?: string;
    phoneNumber?: string;
    serviceRequested: string;
    dateTimeProposed: string;
  };
}

export interface Booking {
  id: string;
  customerName: string;
  phoneNumber: string;
  serviceRequested: string;
  dateTimeProposed: string;
  createdAt: string;
  status: "confirmed" | "pending";
}

export interface LeadInquiry {
  id: string;
  message: string;
  intent: "pricing_inquiry" | "booking_request" | "complaint" | "sales_lead" | "general_support" | string;
  urgency: "high" | "medium" | "low";
  summary: string;
  sentiment: "positive" | "neutral" | "negative";
  details: {
    name?: string | null;
    phone?: string | null;
    email?: string | null;
    dateTimeProposed?: string | null;
    serviceRequested?: string | null;
  };
  timestamp: string;
}
