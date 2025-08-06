# CareChat Microservices Architecture & MongoDB Migration Plan

## 📋 Project Overview

This document outlines the migration of Track1 and Track2 from PostgreSQL to MongoDB, while keeping Track3 in PostgreSQL, and implementing a unified microservices architecture with an API Gateway.

---

## 🏗️ **Architecture Overview**

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                              │
│                     (Node.js/Express)                          │
│                    Port: 3000                                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
            ┌─────────┼─────────┐
            │         │         │
    ┌───────▼───┐ ┌───▼───┐ ┌───▼────────┐
    │ Track 1   │ │Track 2│ │  Track 3   │
    │ Service   │ │Service│ │  Service   │
    │Port: 3001 │ │3002   │ │ Port: 3003 │
    └───────────┘ └───────┘ └────────────┘
            │         │         │
    ┌───────▼───┐ ┌───▼───┐ ┌───▼────────┐
    │ MongoDB   │ │MongoDB│ │PostgreSQL  │
    │ Track1 DB │ │Track2 │ │ Track3 DB  │
    └───────────┘ └───────┘ └────────────┘
```

---

## 🗄️ **MongoDB Schema Design**

### **Track 1 & Track 2 Unified MongoDB Database: `carechat_unified`**

#### **1. Users Collection**
```javascript
// Collection: users
{
  _id: ObjectId(),
  userId: UUID,                    // For compatibility
  userType: "patient" | "user",    // Distinguish Track1 vs Track2 users
  trackOrigin: "track1" | "track2", // Source tracking
  
  // Common fields
  fullName: String,
  phoneNumber: String,             // Unique index
  email: String,                   // Optional, unique when present
  preferredLanguage: String,       // Default: "en"
  passwordHash: String,
  
  // Track-specific metadata
  profile: {
    // Track 1 specific
    patientId: UUID,               // Original Track1 patient_id
    medicalInfo: {
      conditions: [String],
      allergies: [String],
      medications: [String]
    },
    
    // Track 2 specific  
    chatPreferences: {
      preferredProvider: "gemini" | "groq",
      contextRetention: Boolean,
      analyticsOptIn: Boolean
    }
  },
  
  // Status and tracking
  isActive: Boolean,
  isVerified: Boolean,
  lastLogin: Date,
  loginHistory: [{
    timestamp: Date,
    ipAddress: String,
    userAgent: String
  }],
  
  // Audit
  createdAt: Date,
  updatedAt: Date,
  migratedFrom: {
    source: "postgresql_track1" | "postgresql_track2",
    originalId: UUID,
    migratedAt: Date
  }
}
```

#### **2. Conversations Collection**
```javascript
// Collection: conversations
{
  _id: ObjectId(),
  conversationId: UUID,
  userId: UUID,                    // Reference to users.userId
  trackOrigin: "track1" | "track2",
  conversationType: "chat" | "feedback" | "reminder_feedback",
  
  // Conversation metadata
  title: String,                   // Optional, can be AI-generated
  summary: String,                 // AI-generated conversation summary
  status: "active" | "archived" | "deleted",
  
  // Tracking and analytics
  messageCount: Number,
  totalTokens: Number,             // Cumulative token usage
  avgResponseTime: Number,         // Milliseconds
  
  // Timeline
  startedAt: Date,
  lastMessageAt: Date,
  archivedAt: Date,
  
  // Audit
  createdAt: Date,
  updatedAt: Date
}
```

#### **3. Messages Collection**
```javascript
// Collection: messages
{
  _id: ObjectId(),
  messageId: UUID,
  conversationId: UUID,            // Reference to conversations
  userId: UUID,                    // Message author
  
  // Message content
  role: "user" | "assistant" | "system",
  content: String,
  contentType: "text" | "feedback" | "reminder_response",
  
  // Language and translation
  originalLanguage: String,
  translatedContent: {
    [languageCode]: String         // e.g., { "en": "Hello", "fr": "Bonjour" }
  },
  
  // AI/LLM metadata (Track 2)
  llmMetadata: {
    provider: "gemini" | "groq",
    model: String,                 // e.g., "gemini-2.0-flash"
    tokenCount: Number,
    responseTime: Number,          // Milliseconds
    temperature: Number,
    confidence: Number
  },
  
  // Feedback analysis (Track 1)
  feedbackAnalysis: {
    rating: Number,                // 1-5 scale
    sentiment: "positive" | "negative" | "neutral",
    sentimentScore: Number,        // -1 to 1
    topics: [String],              // AI-extracted topics
    urgency: "high" | "medium" | "low",
    urgencyScore: Number,          // 0-1
    actionRequired: Boolean,
    department: String,
    category: String
  },
  
  // Context and threading
  replyToMessageId: UUID,          // For threaded conversations
  context: {
    location: String,
    device: String,
    sessionData: Object            // Flexible session context
  },
  
  // Audit and tracking
  timestamp: Date,
  editHistory: [{
    editedAt: Date,
    oldContent: String,
    reason: String
  }],
  
  createdAt: Date,
  updatedAt: Date
}
```

#### **4. Feedback Sessions Collection**
```javascript
// Collection: feedback_sessions
{
  _id: ObjectId(),
  sessionId: UUID,
  userId: UUID,
  conversationId: UUID,            // Optional link to conversation
  
  // Session details
  sessionType: "post_visit" | "medication" | "service_quality" | "general",
  department: String,
  visitDate: Date,
  visitType: String,
  
  // Overall assessment
  overallRating: Number,           // 1-5
  overallSentiment: String,
  recommendationScore: Number,     // NPS-style 0-10
  
  // Structured feedback
  responses: [{
    questionId: String,
    question: String,
    responseType: "text" | "rating" | "choice" | "boolean",
    response: Mixed,               // Flexible response type
    rating: Number,
    sentiment: String,
    topics: [String],
    urgency: String
  }],
  
  // Analytics and insights
  analytics: {
    completionRate: Number,        // Percentage of questions answered
    timeSpent: Number,            // Seconds
    abandonedAt: String,          // Question ID where user stopped
    satisfactionIndex: Number,    // Calculated satisfaction score
    actionItems: [String],        // AI-generated action items
    followUpRequired: Boolean,
    escalationLevel: Number       // 0-3 (none, low, medium, high)
  },
  
  // Language and accessibility
  language: String,
  accessibilityFeatures: [String], // Screen reader, high contrast, etc.
  
  // Status and workflow
  status: "in_progress" | "completed" | "abandoned",
  reviewStatus: "pending" | "reviewed" | "acted_upon",
  assignedTo: String,             // Staff member for follow-up
  
  // Audit
  createdAt: Date,
  updatedAt: Date,
  submittedAt: Date,
  reviewedAt: Date
}
```

#### **5. Reminders Collection**
```javascript
// Collection: reminders
{
  _id: ObjectId(),
  reminderId: UUID,
  userId: UUID,
  
  // Reminder content
  title: String,
  message: String,
  reminderType: "medication" | "appointment" | "followup" | "custom",
  category: String,               // e.g., "prescription", "lab_test"
  
  // Scheduling configuration
  schedule: {
    type: "one_time" | "recurring",
    startDate: Date,
    endDate: Date,
    
    // For one-time reminders
    scheduledTime: Date,
    
    // For recurring reminders
    recurrence: {
      pattern: "daily" | "weekly" | "monthly" | "custom",
      interval: Number,           // Every N days/weeks/months
      daysOfWeek: [Number],       // 0-6 (Sunday-Saturday)
      daysOfMonth: [Number],      // 1-31
      times: [String]             // ["08:00", "20:00"]
    }
  },
  
  // Delivery configuration
  delivery: {
    methods: ["sms" | "email" | "push" | "in_app"],
    preferences: {
      sms: { phone: String, enabled: Boolean },
      email: { address: String, enabled: Boolean },
      push: { deviceTokens: [String], enabled: Boolean }
    },
    retryPolicy: {
      maxRetries: Number,
      retryInterval: Number,      // Minutes
      backoffMultiplier: Number
    }
  },
  
  // Smart features
  smartFeatures: {
    adaptiveScheduling: Boolean,   // Adjust based on user response patterns
    contextAwareness: Boolean,     // Consider user activity/location
    escalationRules: [{
      missedCount: Number,
      action: "notify_caregiver" | "call_patient" | "schedule_visit",
      recipient: String
    }]
  },
  
  // Status and analytics
  status: "active" | "paused" | "completed" | "cancelled",
  analytics: {
    totalScheduled: Number,
    totalSent: Number,
    totalDelivered: Number,
    totalAcknowledged: Number,
    responseRate: Number,
    avgResponseTime: Number,      // Minutes
    missedConsecutive: Number,
    lastMissedAt: Date
  },
  
  // Audit
  createdAt: Date,
  updatedAt: Date,
  createdBy: UUID,               // Staff member who created
  lastModifiedBy: UUID
}
```

#### **6. Reminder Deliveries Collection**
```javascript
// Collection: reminder_deliveries
{
  _id: ObjectId(),
  deliveryId: UUID,
  reminderId: UUID,
  userId: UUID,
  
  // Delivery details
  scheduledFor: Date,
  sentAt: Date,
  deliveredAt: Date,
  acknowledgedAt: Date,
  
  // Delivery method and status
  method: "sms" | "email" | "push" | "in_app",
  status: "pending" | "sent" | "delivered" | "failed" | "acknowledged",
  
  // Provider response and tracking
  provider: {
    name: String,                 // Twilio, SendGrid, etc.
    messageId: String,            // Provider's tracking ID
    response: Object,             // Full provider response
    cost: Number,                 // Delivery cost in cents
    errorCode: String,
    errorMessage: String
  },
  
  // User interaction
  userResponse: {
    acknowledged: Boolean,
    responseTime: Number,         // Seconds from delivery
    feedback: String,             // Optional user feedback
    rating: Number,               // 1-5 satisfaction
    actionTaken: String           // "took_medication", "scheduled_appointment", etc.
  },
  
  // Retry tracking
  retryCount: Number,
  maxRetries: Number,
  nextRetryAt: Date,
  finalAttempt: Boolean,
  
  // Context
  context: {
    userTimezone: String,
    deviceType: String,
    location: Object,             // If available and permitted
    batteryLevel: Number,         // For push notifications
    networkType: String
  },
  
  // Audit
  createdAt: Date,
  updatedAt: Date
}
```

#### **7. System Analytics Collection**
```javascript
// Collection: system_analytics
{
  _id: ObjectId(),
  analyticsId: UUID,
  
  // Metric identification
  metricName: String,
  metricType: "counter" | "gauge" | "histogram" | "timer",
  category: "user_engagement" | "message_analytics" | "feedback_analytics" | "reminder_performance",
  
  // Metric value and dimensions
  value: Number,
  dimensions: {
    trackOrigin: String,
    userSegment: String,
    department: String,
    timeOfDay: String,
    dayOfWeek: String,
    // Additional flexible dimensions
  },
  
  // Time series data
  timestamp: Date,
  aggregationPeriod: "minute" | "hour" | "day" | "week" | "month",
  
  // Context and metadata
  metadata: {
    userId: UUID,
    sessionId: UUID,
    conversationId: UUID,
    source: String,
    version: String
  },
  
  createdAt: Date
}
```

---

## 🚀 **Microservices Implementation**

### **Directory Structure**
```
carechat-microservices/
├── api-gateway/                 # Main API Gateway
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── services/
│   ├── track1-service/          # Feedback & Reminders
│   ├── track2-service/          # Chat & AI
│   ├── track3-service/          # Blood Management
│   └── shared/                  # Shared utilities
├── databases/
│   ├── mongodb/                 # Track 1 & 2
│   └── postgresql/              # Track 3
├── infrastructure/
│   ├── docker-compose.yml
│   ├── nginx/
│   └── monitoring/
└── docs/
```

Let me create the implementation files:
