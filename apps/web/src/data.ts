import { BusinessProfile } from "./types";

export const PRESET_BUSINESSES: BusinessProfile[] = [
  {
    id: "wellness-spa",
    name: "Zenith Wellness Spa",
    type: "Wellness & Spa Center",
    hours: "Mon-Sat 9:00 AM - 7:00 PM, Sun Closed",
    description: "A luxury oasis offering holistic wellness treatments, massage therapies, custom facials, and hot stone rituals designed to restore inner peace.",
    icon: "Spa",
    services: [
      { name: "Swedish Relaxation Massage (60m)", price: "$95" },
      { name: "Deep Tissue Muscle Therapy (60m)", price: "$125" },
      { name: "Radiance Botanical Facial (50m)", price: "$85" },
      { name: "Aromatherapy Detox Ritual (90m)", price: "$160" }
    ]
  },
  {
    id: "dental-clinic",
    name: "Elite Dental Care",
    type: "Medical & Dental Clinic",
    hours: "Mon-Fri 8:00 AM - 5:00 PM, Sat 9:00 AM - 2:00 PM",
    description: "State-of-the-art family and cosmetic dentistry clinic specializing in pain-free cleanings, teeth whitening, clear aligners, and dental restoration.",
    icon: "Activity",
    services: [
      { name: "Comprehensive Oral Exam & Cleaning", price: "$150" },
      { name: "Professional Laser Whitening Session", price: "$299" },
      { name: "Invisalign Aligner Consultation", price: "Free" },
      { name: "Emergency Dental Care Evaluation", price: "$99" }
    ]
  },
  {
    id: "legal-firm",
    name: "Vanguard Partners Law",
    type: "Legal & Consulting Services",
    hours: "Mon-Fri 8:30 AM - 5:30 PM",
    description: "Boutique law firm offering expert counsel on small business incorporation, IP licensing, estate planning, and corporate compliance.",
    icon: "Scale",
    services: [
      { name: "30-Minute Business Consultation", price: "$100" },
      { name: "Trademark Search & Filing Intake", price: "$450" },
      { name: "Contract & Agreement Audit", price: "$350" },
      { name: "Will & Estate Plan Core Package", price: "$800" }
    ]
  },
  {
    id: "auto-repair",
    name: "Apex Precision Auto",
    type: "Automotive Repair & Care",
    hours: "Mon-Fri 7:30 AM - 6:00 PM, Sat 8:00 AM - 1:00 PM",
    description: "Highly rated independent mechanics specializing in foreign and domestic vehicle diagnostics, scheduled maintenance, brake replacement, and AC repair.",
    icon: "Car",
    services: [
      { name: "Full Diagnostic Scan & Health Check", price: "$85" },
      { name: "Synthetic Oil Change & Inspection", price: "$75" },
      { name: "Brake Pad Replacement (Per Axle)", price: "$195" },
      { name: "Climate Control AC Recharge Service", price: "$120" }
    ]
  }
];

export const MOCK_TRIAGE_INQUIRIES = [
  {
    label: "Sales Lead",
    message: "Hi, I represent a team of 15 people and we want to book a wellness retreat. Is there a bulk discount for this Saturday?"
  },
  {
    label: "Booking Request",
    message: "Can I schedule a deep tissue massage for tomorrow afternoon at 3:00 PM? My name is Robert Vance and you can reach me at 555-0199."
  },
  {
    label: "Pricing Inquiry",
    message: "How much do you charge for professional teeth whitening? Do you take Delta Dental insurance or is that fully out-of-pocket?"
  },
  {
    label: "Angry Complaint",
    message: "My car was in your shop yesterday for an oil change and now there is oil dripping all over my driveway! Call me back immediately at 555-8822."
  }
];

export const INITIAL_BOOKINGS = [
  {
    id: "bk-1",
    customerName: "Eleanor Vance",
    phoneNumber: "555-0143",
    serviceRequested: "Swedish Relaxation Massage (60m)",
    dateTimeProposed: "Tomorrow at 2:00 PM",
    createdAt: new Date().toISOString(),
    status: "confirmed" as const
  },
  {
    id: "bk-2",
    customerName: "David Miller",
    phoneNumber: "555-0182",
    serviceRequested: "Comprehensive Oral Exam & Cleaning",
    dateTimeProposed: "Friday at 10:30 AM",
    createdAt: new Date().toISOString(),
    status: "confirmed" as const
  }
];

export const INITIAL_LEADS = [
  {
    id: "ld-1",
    message: "I need to file a trademark for my coffee brand. Do you have slots open this week to discuss rates?",
    intent: "sales_lead",
    urgency: "high" as const,
    summary: "Customer wants trademark filing consultation details.",
    sentiment: "neutral" as const,
    details: { name: null, phone: null, email: null, dateTimeProposed: "this week", serviceRequested: "Trademark Filing" },
    timestamp: new Date().toISOString()
  },
  {
    id: "ld-2",
    message: "My brakes are squealing terribly. I want to bring my Civic in on Wednesday morning around 8 AM. Call me at 555-9211.",
    intent: "booking_request",
    urgency: "high" as const,
    summary: "Customer requests Wednesday 8 AM brake replacement appointment.",
    sentiment: "negative" as const,
    details: { name: null, phone: "555-9211", email: null, dateTimeProposed: "Wednesday morning at 8 AM", serviceRequested: "Brake Repair" },
    timestamp: new Date().toISOString()
  }
];
