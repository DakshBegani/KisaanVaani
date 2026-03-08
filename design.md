# System Design Document: KisaanVaani

**System Name:** KisaanVaani  
**Tagline:** "An AI assistant for on-demand farming help via messaging and voice"  
**Version:** 1.0  
**Date:** February 7, 2026  
**Team:** Gradient Ascent

---

## 1. Introduction & Design Goals

### 1.1 System Purpose

KisaanVaani is an AI-driven agricultural advisory system that provides personalized, real-time farming guidance to rural Indian farmers through WhatsApp, Telegram, and voice interfaces. The system eliminates the need for app installations, dashboards, or technical knowledge, making expert agricultural advice accessible to farmers with varying literacy levels.

### 1.2 Core Design Goals

**Simplicity**
- Zero learning curve through familiar messaging platforms
- Natural language interaction in regional languages
- Voice-first design for low-literacy users
- No dashboards, logins, or complex navigation

**Accessibility**
- Works on basic smartphones with 2G/3G connectivity
- Multi-language support (text and voice)
- Low bandwidth optimization
- 24/7 availability without human intervention

**Scalability**
- Support 100,000 monthly active users
- Handle 2 million interactions per month (20 per user)
- Auto-scale during weather events and peak farming seasons
- Horizontal scaling architecture using serverless components

**Cost Efficiency**
- Target operational cost: ₹8-₹10 per user per month
- Optimize AI inference costs through caching and batching
- Leverage serverless architecture to pay only for actual usage
- Efficient resource utilization with minimal idle capacity

### 1.3 Key Differentiators

- **Proactive Intelligence:** Weather-aware alerts sent automatically
- **Context-Aware:** Recommendations based on crop stage, location, and user constraints
- **Conversational:** Free-form questions instead of rigid menus
- **Visual Diagnosis:** Photo-based pest and disease identification
- **Cost-Conscious:** Budget-aware recommendations for resource-constrained farmers

---

## 2. High-Level Architecture Overview


### 2.1 Architectural Layers

The system is organized into four primary layers:

**User Space**
- WhatsApp and Telegram messaging platforms
- User devices (smartphones with basic capabilities)
- Voice and text input modalities
- Photo capture and upload

**Interface Layer**
- Messaging platform webhooks and APIs
- API Gateway for request routing
- Authentication and rate limiting
- Protocol translation (WhatsApp/Telegram → HTTP)

**Processing Layer**
- Django backend for business logic
- AWS Lambda for serverless compute
- AI orchestration and decision engine
- Weather data integration
- Alert generation service

**Data & AI Layer**
- AWS Bedrock for LLM orchestration
- OpenAI GPT-4o-mini for natural language understanding
- PyTorch models for image analysis
- DynamoDB for user state and feedback
- S3 for media storage and logs
- External weather APIs

### 2.2 Communication Flow

```
Farmer (WhatsApp/Telegram)
    ↓
WhatsApp Business API / Telegram Bot API
    ↓
AWS API Gateway (HTTPS endpoint)
    ↓
AWS Lambda (Request Handler)
    ↓
Django Backend (Business Logic)
    ↓
┌─────────────────────────────────────┐
│  AI Orchestration Layer             │
│  ├─ AWS Bedrock                     │
│  ├─ OpenAI GPT-4o-mini              │
│  ├─ PyTorch Vision Models           │
│  ├─ Amazon Transcribe (voice)       │
│  └─ Amazon Polly (TTS)              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Data & Context Layer               │
│  ├─ DynamoDB (user profiles)        │
│  ├─ S3 (images, logs)               │
│  └─ Weather API (forecasts)         │
└─────────────────────────────────────┘
    ↓
Response Generation
    ↓
API Gateway → WhatsApp/Telegram → Farmer
```

### 2.3 Separation of Concerns

**User Space:** Handles all user interactions through familiar messaging interfaces without requiring custom apps.

**Advisor/AI Space:** Processes queries, analyzes context, generates recommendations, and manages proactive alerts independently of user interactions.

**Data Space:** Maintains user state, conversation history, feedback loops, and analytics for continuous improvement.

---

## 3. Architecture Diagram (Textual Description)

### 3.1 Complete System Architecture


```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER SPACE                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  WhatsApp    │  │  Telegram    │  │  Voice Input │             │
│  │  Interface   │  │  Interface   │  │  (Audio)     │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  WhatsApp/      │
                    │  Telegram APIs  │
                    └────────┬────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                     INTERFACE LAYER (AWS)                             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  AWS API Gateway                                             │    │
│  │  - HTTPS endpoints                                           │    │
│  │  - Request validation                                        │    │
│  │  - Rate limiting                                             │    │
│  │  - Authentication                                            │    │
│  └─────────────────────┬───────────────────────────────────────┘    │
└────────────────────────┼──────────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
    ┌─────▼─────┐              ┌────────▼────────┐
    │  Lambda   │              │  Lambda         │
    │  (Text/   │              │  (Voice         │
    │  Photo)   │              │  Processing)    │
    └─────┬─────┘              └────────┬────────┘
          │                             │
          │    ┌────────────────────────┘
          │    │
┌─────────▼────▼───────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Django Backend (AWS EC2 / ECS)                              │   │
│  │  ├─ Request Router                                           │   │
│  │  ├─ Session Manager                                          │   │
│  │  ├─ Context Builder                                          │   │
│  │  └─ Response Formatter                                       │   │
│  └──────────────────────┬───────────────────────────────────────┘   │
│                         │                                             │
│  ┌──────────────────────▼───────────────────────────────────────┐   │
│  │  AI Orchestration Engine                                     │   │
│  │  ├─ Query Classification                                     │   │
│  │  ├─ Context Enrichment                                       │   │
│  │  ├─ Model Selection                                          │   │
│  │  └─ Confidence Scoring                                       │   │
│  └──────────────────────┬───────────────────────────────────────┘   │
└─────────────────────────┼─────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐  ┌──────▼──────┐  ┌────▼────┐
    │  Amazon   │  │  Amazon     │  │ Weather │
    │ Transcribe│  │   Polly     │  │   API   │
    └───────────┘  └─────────────┘  └────┬────┘
                                          │
┌─────────────────────────────────────────┼─────────────────────────────┐
│                    AI & DATA LAYER      │                             │
│  ┌──────────────────────────────────────▼──────────────────────┐     │
│  │  AWS Bedrock (LLM Orchestration)                            │     │
│  │  ├─ Prompt Management                                       │     │
│  │  ├─ Model Routing                                           │     │
│  │  └─ Response Caching                                        │     │
│  └──────────────────────┬──────────────────────────────────────┘     │
│                         │                                             │
│  ┌──────────────────────▼──────────────────────────────────────┐     │
│  │  OpenAI GPT-4o-mini                                         │     │
│  │  - Natural language understanding                           │     │
│  │  - Recommendation generation                                │     │
│  │  - Multi-language support                                   │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  PyTorch Vision Models (Lambda)                             │     │
│  │  - Crop disease detection                                   │     │
│  │  - Pest identification                                      │     │
│  │  - Confidence scoring                                       │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  AWS DynamoDB                                               │     │
│  │  ├─ User profiles (crop, location, preferences)            │     │
│  │  ├─ Conversation history                                   │     │
│  │  ├─ Feedback & ratings                                     │     │
│  │  └─ Alert state tracking                                   │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  AWS S3                                                     │     │
│  │  ├─ Uploaded crop images                                   │     │
│  │  ├─ System logs                                            │     │
│  │  ├─ Analytics data                                         │     │
│  │  └─ Model artifacts                                        │     │
│  └─────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                    PROACTIVE SERVICES (AWS EC2)                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  Alert Engine (Cron-based)                                 │     │
│  │  ├─ Weather monitoring                                     │     │
│  │  ├─ Risk assessment                                        │     │
│  │  ├─ Alert generation                                       │     │
│  │  └─ WebSocket push to users                               │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │  Weekly Plan Generator (Scheduled)                         │     │
│  │  ├─ Crop stage calculation                                │     │
│  │  ├─ Weather-adjusted planning                             │     │
│  │  └─ Task prioritization                                   │     │
│  └─────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow Summary

1. **User Input:** Farmer sends message/voice/photo via WhatsApp or Telegram
2. **API Gateway:** Receives webhook, validates, routes to appropriate Lambda
3. **Lambda Functions:** Handle protocol-specific processing (voice transcription, image upload)
4. **Django Backend:** Orchestrates business logic, builds context from user profile
5. **AI Layer:** Processes query using Bedrock + GPT-4o-mini, analyzes images with PyTorch
6. **Data Layer:** Fetches user data from DynamoDB, weather from external API
7. **Response Generation:** Formats response in user's language, sends via API Gateway
8. **Proactive Services:** EC2-based cron jobs monitor weather, generate alerts independently

---

## 4. Component-Level Design

### 4.1 Messaging & Voice Interface Layer


**Purpose:** Provide familiar, accessible interfaces for farmer interactions without requiring app installations.

**Components:**

**WhatsApp Business API Integration**
- Webhook endpoint for incoming messages
- Support for text, voice notes, and image messages
- Message status tracking (sent, delivered, read)
- Template messages for structured responses
- Rate limit handling (80 messages per second per phone number)

**Telegram Bot API Integration**
- Long polling or webhook for message reception
- Support for inline keyboards for quick responses
- File upload handling (up to 20MB)
- Bot commands for quick actions (/start, /help, /language)

**Voice Message Handler**
- Accepts audio files in common formats (OGG, MP3, M4A)
- Extracts audio from messaging platform
- Passes to Amazon Transcribe for speech-to-text
- Supports 8+ Indian languages
- Handles background noise and varying audio quality

**Media Handler**
- Downloads images from messaging platforms
- Validates file type and size
- Uploads to S3 with unique identifiers
- Generates presigned URLs for processing
- Implements retry logic for failed downloads

**Technical Specifications:**
- Protocol: HTTPS webhooks
- Authentication: Platform-specific tokens
- Timeout: 30 seconds for webhook response
- Retry: Exponential backoff for failed deliveries

### 4.2 API Gateway & Backend (Django)

**Purpose:** Route requests, manage sessions, orchestrate business logic, and coordinate AI services.

**AWS API Gateway**

**Endpoints:**
- `POST /webhook/whatsapp` - WhatsApp message webhook
- `POST /webhook/telegram` - Telegram message webhook
- `POST /api/query` - Direct query endpoint (future mobile app)
- `GET /health` - Health check endpoint

**Features:**
- Request validation and sanitization
- Rate limiting (100 requests per minute per user)
- API key authentication for platform webhooks
- Request/response logging
- CORS configuration for future web interface

**Django Backend Architecture**

**Core Modules:**

**Request Router (`router.py`)**
- Identifies message type (text, voice, image)
- Routes to appropriate handler
- Manages request queuing during high load
- Implements circuit breaker pattern for downstream services

**Session Manager (`session.py`)**
- Maintains conversation context (last 10 messages)
- Tracks user state (onboarding, active, awaiting_response)
- Implements session timeout (30 minutes of inactivity)
- Stores session data in DynamoDB with TTL

**Context Builder (`context.py`)**
- Fetches user profile from DynamoDB
- Retrieves current weather data for user location
- Calculates crop stage from planting date
- Builds comprehensive context object for AI
- Caches frequently accessed data (Redis/ElastiCache)

**Response Formatter (`formatter.py`)**
- Translates AI output to user's language
- Formats responses for messaging platform constraints
- Adds emojis and visual elements for clarity
- Splits long responses into multiple messages
- Generates quick reply buttons when appropriate

**User Profile Manager (`profile.py`)**
- Handles onboarding flow
- Updates user preferences
- Validates and stores user data
- Manages data privacy and consent

**Technical Specifications:**
- Framework: Django 4.2+
- Deployment: AWS ECS (Elastic Container Service) with Fargate
- Scaling: Auto-scaling based on CPU (target 70%)
- Database: DynamoDB for user data, ElastiCache for session cache
- Logging: CloudWatch Logs with structured JSON

### 4.3 AI Orchestration Layer

**Purpose:** Coordinate multiple AI services, manage prompts, implement confidence scoring, and ensure safe responses.

**AI Orchestrator (`orchestrator.py`)**

**Query Classification:**
- Categorizes incoming queries (pest_issue, irrigation, fertilizer, general, photo_diagnosis)
- Determines urgency level (emergency, high, normal, low)
- Selects appropriate AI model and prompt template
- Routes to specialized handlers

**Context Enrichment:**
- Combines user profile, weather data, and conversation history
- Fetches relevant agricultural knowledge from knowledge base
- Retrieves regional pest/disease outbreak data
- Builds structured prompt for LLM

**Prompt Management:**
- Template library for different query types
- Dynamic prompt construction with user context
- Few-shot examples for consistent formatting
- System prompts for safety and accuracy

**Model Selection:**
- Primary: OpenAI GPT-4o-mini for general queries
- Vision: PyTorch models for image analysis
- Fallback: Rule-based responses for high-confidence scenarios

**Confidence Scoring:**
- Analyzes LLM response certainty
- Checks for contradictions or ambiguity
- Validates against agricultural knowledge base
- Assigns confidence score (0-100%)
- Triggers fallback for scores < 70%

**Response Validation:**
- Checks for harmful or incorrect advice
- Ensures recommendations align with user constraints (organic, budget)
- Validates chemical recommendations against safety guidelines
- Filters out hallucinated information

**Technical Specifications:**
- Language: Python 3.11
- Deployment: AWS Lambda (for stateless operations)
- Timeout: 30 seconds
- Memory: 2GB
- Concurrency: 1000 concurrent executions

### 4.4 LLM & Vision Models

**OpenAI GPT-4o-mini Integration**

**Purpose:** Natural language understanding, recommendation generation, and conversational responses.

**Usage Patterns:**

**Query Understanding:**
```
System Prompt: You are an agricultural advisor for Indian farmers...
User Context: Crop=Tomato, Location=Pune, Stage=Flowering, Weather=Rain expected
User Query: "Should I spray today?"
```

**Response Generation:**
- Structured output format (action, reasoning, warnings)
- Multi-language support via prompt engineering
- Temperature: 0.3 (for consistent, factual responses)
- Max tokens: 500 (to control costs)

**Optimization Strategies:**
- Prompt caching for common patterns
- Batch processing for non-urgent queries
- Response caching for identical queries (1-hour TTL)
- Token usage monitoring and optimization

**PyTorch Vision Models**

**Purpose:** Crop disease detection, pest identification, and visual diagnosis.

**Model Architecture:**
- Base: ResNet-50 or EfficientNet-B3
- Fine-tuned on Indian crop disease dataset
- Multi-label classification (disease + severity)
- Output: Top-3 predictions with confidence scores

**Inference Pipeline:**
1. Image preprocessing (resize, normalize)
2. Model inference on Lambda (GPU-enabled)
3. Post-processing (threshold filtering, ranking)
4. Confidence calibration
5. Result formatting with recommendations

**Model Deployment:**
- Containerized with PyTorch and dependencies
- Deployed on Lambda with 10GB memory
- Cold start optimization (model preloading)
- Model versioning for A/B testing

**Supported Detections:**
- 20+ common crop diseases
- 15+ major pest species
- Nutrient deficiencies
- Environmental stress indicators

**Technical Specifications:**
- Framework: PyTorch 2.0+
- Inference time: < 5 seconds per image
- Batch size: 1 (real-time processing)
- Model size: < 500MB (for fast loading)

### 4.5 Weather & Alert Engine

**Weather Integration**

**Purpose:** Provide real-time and forecast weather data for context-aware recommendations.

**Data Sources:**
- Primary: OpenWeatherMap API or IMD (India Meteorological Department)
- Backup: Weather.com API
- Granularity: District-level or PIN code-level

**Data Points:**
- Current: Temperature, humidity, rainfall, wind speed
- Forecast: 7-day predictions with hourly breakdown
- Alerts: Severe weather warnings from IMD

**Caching Strategy:**
- Current weather: 30-minute cache
- Forecast: 6-hour cache
- Alerts: 15-minute cache
- Location-based cache keys

**Alert Engine (EC2-based Service)**

**Purpose:** Proactively monitor conditions and send timely alerts to farmers.

**Architecture:**
- Scheduled cron jobs (every 15 minutes)
- Queries weather API for all active user locations
- Evaluates alert conditions based on user context
- Generates and sends alerts via messaging platforms

**Alert Types:**

**Weather Alerts:**
- Heavy rain warning (> 50mm in 24 hours)
- Heatwave alert (> 40°C for 3+ days)
- Dry spell notification (no rain for 7+ days)
- Frost warning (temperature < 5°C)

**Crop Protection Alerts:**
- Irrigation delay recommendation (rain within 24 hours)
- Spray postponement (rain within 6 hours)
- Harvest urgency (rain before harvest window)

**Pest Risk Alerts:**
- High humidity + temperature = fungal disease risk
- Regional pest outbreak notifications
- Preventive action reminders

**Alert Logic:**
```
For each active user:
  1. Fetch user profile (crop, location, stage)
  2. Get weather forecast for location
  3. Evaluate alert conditions
  4. Check if alert already sent (deduplication)
  5. Generate personalized alert message
  6. Send via WhatsApp/Telegram
  7. Log alert in DynamoDB
```

**Deduplication:**
- Track sent alerts in DynamoDB with 24-hour TTL
- Avoid duplicate alerts for same condition
- Allow updates if condition severity changes

**Technical Specifications:**
- Platform: AWS EC2 (t3.medium)
- Schedule: Cron (every 15 minutes)
- Concurrency: Process 10,000 users per batch
- Delivery: WebSocket or direct API calls to messaging platforms

### 4.6 Data Storage & Analytics

**AWS DynamoDB**

**Purpose:** Store user profiles, conversation history, feedback, and alert state with high availability and low latency.

**Table Design:**

**Users Table:**
- Partition Key: `user_id` (phone number hash)
- Attributes: crop, variety, location, farm_size, farming_method, budget, language, planting_date
- GSI: location_index (for regional queries)
- TTL: None (persistent user data)

**Conversations Table:**
- Partition Key: `user_id`
- Sort Key: `timestamp`
- Attributes: message_type, query, response, confidence_score, feedback
- TTL: 90 days (automatic cleanup)

**Alerts Table:**
- Partition Key: `user_id`
- Sort Key: `alert_type#timestamp`
- Attributes: alert_message, condition, sent_at, acknowledged
- TTL: 7 days

**Feedback Table:**
- Partition Key: `interaction_id`
- Attributes: user_id, query, response, rating, feedback_text, timestamp
- GSI: timestamp_index (for analytics)

**Performance Characteristics:**
- Read/Write Capacity: On-demand (auto-scaling)
- Latency: Single-digit milliseconds
- Consistency: Eventually consistent reads (cost optimization)
- Backup: Point-in-time recovery enabled

**AWS S3**

**Purpose:** Store images, logs, analytics data, and model artifacts with durability and cost efficiency.

**Bucket Structure:**

**crop-images-bucket:**
- Path: `/{user_id}/{timestamp}/{image_id}.jpg`
- Lifecycle: Move to Glacier after 90 days
- Access: Presigned URLs with 1-hour expiration
- Encryption: Server-side encryption (SSE-S3)

**logs-bucket:**
- Path: `/year={YYYY}/month={MM}/day={DD}/`
- Lifecycle: Delete after 180 days
- Format: JSON lines for easy parsing
- Integration: CloudWatch Logs export

**analytics-bucket:**
- Path: `/aggregated/{date}/`
- Content: Daily aggregated metrics, user behavior patterns
- Access: Restricted to analytics team
- Retention: 2 years

**models-bucket:**
- Path: `/vision-models/{version}/`
- Content: PyTorch model weights, config files
- Versioning: Enabled for rollback capability
- Access: Lambda execution role only

**Technical Specifications:**
- Storage Class: S3 Standard (hot data), S3 Glacier (cold data)
- Replication: Cross-region replication for disaster recovery
- Access Control: IAM roles and bucket policies
- Cost Optimization: Lifecycle policies, intelligent tiering

---

## 5. Detailed User Flow Diagrams (Textual)

### 5.1 First-Time Onboarding Flow


```
Step 1: User Initiates Contact
  Farmer → Sends "Hi" or "Start" to WhatsApp/Telegram bot
  
Step 2: Welcome & Language Selection
  System → Detects new user (no profile in DynamoDB)
  System → Sends welcome message with language options
  System → "Welcome to KisaanVaani! Please select your language:"
           [Hindi] [English] [Marathi] [Punjabi] [Tamil] [Telugu]
  
Step 3: Language Confirmation
  Farmer → Selects language (e.g., Hindi)
  System → Updates session with language preference
  System → Sends confirmation in selected language
  
Step 4: Crop Information
  System → "Which crop are you growing?"
  System → Provides common crop options or free text input
  Farmer → Responds "Tomato" (text or voice)
  System → "Which variety of tomato?" (if applicable)
  Farmer → Responds with variety or "Don't know"
  
Step 5: Location Registration
  System → "Please share your location or enter PIN code"
  Farmer → Shares GPS location OR types PIN code
  System → Validates location
  System → Confirms: "Location set to [District], [State]"
  
Step 6: Crop Stage
  System → "When did you plant this crop?"
  Farmer → Provides date OR selects from options:
           [This week] [2 weeks ago] [1 month ago] [Custom date]
  System → Calculates current crop stage
  System → Confirms: "Your crop is in [germination/vegetative/flowering] stage"
  
Step 7: Farm Size
  System → "What is your farm size?"
  Farmer → Responds "2 acres" (text or voice)
  System → Validates and confirms
  
Step 8: Farming Method
  System → "Do you practice organic or conventional farming?"
  Farmer → Selects [Organic] or [Conventional]
  System → Stores preference
  
Step 9: Budget Preference
  System → "What is your budget preference for inputs?"
  Farmer → Selects [Low] [Medium] [High]
  System → Stores preference
  
Step 10: Profile Creation
  System → Saves all data to DynamoDB Users table
  System → Generates user_id (hashed phone number)
  System → Sets user state to "active"
  
Step 11: Onboarding Complete
  System → Sends summary of profile
  System → "Setup complete! You can now ask me any farming question."
  System → Provides example questions:
           - "When should I water my crop?"
           - "What fertilizer should I use?"
           - "Send a photo for crop diagnosis"
  
Step 12: First Interaction Prompt
  System → Waits for user's first query
  System → Marks onboarding_completed = true in DynamoDB
```

**Diagram-Ready Description:**
- Box 1: User sends message → Box 2: System detects new user
- Box 3: Language selection → Box 4: Crop info collection
- Box 5: Location registration → Box 6: Crop stage input
- Box 7: Farm details → Box 8: Preferences
- Box 9: Save to DynamoDB → Box 10: Onboarding complete
- Arrow from Box 10 loops back to main query flow

### 5.2 Text Query Flow

```
Step 1: User Sends Text Query
  Farmer → Types question in WhatsApp/Telegram
  Example: "Should I water my tomatoes today?"
  
Step 2: Message Reception
  WhatsApp/Telegram → Sends webhook to API Gateway
  API Gateway → Validates request, checks rate limits
  API Gateway → Routes to Lambda (Text Handler)
  
Step 3: Lambda Processing
  Lambda → Extracts message content, user_id, timestamp
  Lambda → Invokes Django backend via internal API
  
Step 4: Session Management
  Django → Checks if active session exists in cache
  Django → If yes, retrieves conversation context
  Django → If no, creates new session
  Django → Adds current query to session history
  
Step 5: Context Building
  Django → Fetches user profile from DynamoDB
  Django → Retrieves current weather for user location (API call)
  Django → Calculates crop stage from planting date
  Django → Builds context object:
           {
             user: {crop, variety, location, stage, farm_size, method, budget},
             weather: {current, forecast_24h, forecast_7d},
             conversation: [last 5 messages],
             query: "Should I water my tomatoes today?"
           }
  
Step 6: Query Classification
  AI Orchestrator → Analyzes query type (irrigation question)
  AI Orchestrator → Determines urgency (normal)
  AI Orchestrator → Selects prompt template (irrigation_advice)
  
Step 7: Prompt Construction
  AI Orchestrator → Builds structured prompt:
           System: "You are an agricultural advisor..."
           Context: [User profile + Weather + Crop stage]
           Query: "Should I water my tomatoes today?"
           Instructions: "Provide yes/no answer with reasoning..."
  
Step 8: LLM Inference
  AI Orchestrator → Sends prompt to AWS Bedrock
  AWS Bedrock → Routes to OpenAI GPT-4o-mini
  GPT-4o-mini → Generates response:
           "No, avoid watering today. Rain is expected in 6 hours (15mm).
            Wait until tomorrow afternoon. This will save water and prevent
            root rot from excess moisture."
  
Step 9: Response Validation
  AI Orchestrator → Checks response for safety and accuracy
  AI Orchestrator → Assigns confidence score (95%)
  AI Orchestrator → Validates against weather data (confirms rain forecast)
  
Step 10: Response Formatting
  Django → Translates to user's language (if not English)
  Django → Formats for messaging platform
  Django → Adds emojis: "🌧️ No, avoid watering today..."
  Django → Generates quick reply buttons: [Got it] [Why?] [More info]
  
Step 11: Response Delivery
  Django → Sends formatted response to API Gateway
  API Gateway → Forwards to WhatsApp/Telegram API
  WhatsApp/Telegram → Delivers message to farmer
  
Step 12: Logging & Analytics
  Django → Logs interaction in DynamoDB Conversations table
  Django → Records: query, response, confidence_score, timestamp
  Django → Updates session cache with new message
  
Step 13: Feedback Collection (Optional)
  System → Waits for user reaction (thumbs up/down if available)
  System → If user asks follow-up, continues conversation
  System → Stores feedback in DynamoDB for model improvement
```

**Diagram-Ready Description:**
- Start: User message → API Gateway → Lambda → Django
- Django branches to: DynamoDB (profile), Weather API, Session Cache
- Converge at Context Builder → AI Orchestrator → Bedrock → GPT-4o-mini
- Response path: Validation → Formatting → API Gateway → User
- Parallel: Logging to DynamoDB and CloudWatch

### 5.3 Voice Query Flow

```
Step 1: User Sends Voice Message
  Farmer → Records voice note in WhatsApp/Telegram
  Example: [Audio: "Mere tamatar ke patte peelay ho rahe hain"]
  
Step 2: Message Reception
  WhatsApp/Telegram → Sends webhook with audio file URL
  API Gateway → Routes to Lambda (Voice Handler)
  
Step 3: Audio Download
  Lambda → Downloads audio file from messaging platform
  Lambda → Validates file format (OGG, MP3, M4A)
  Lambda → Uploads to S3 temp bucket with 1-hour TTL
  
Step 4: Speech-to-Text
  Lambda → Invokes Amazon Transcribe
  Amazon Transcribe → Detects language (Hindi)
  Amazon Transcribe → Transcribes audio to text
  Output: "Mere tamatar ke patte peelay ho rahe hain"
  
Step 5: Language Detection & Translation
  Lambda → Detects language from transcription
  Lambda → If not English, translates for processing
  Translation: "My tomato leaves are turning yellow"
  Lambda → Stores original language for response
  
Step 6: Text Processing
  Lambda → Passes transcribed text to Django backend
  [Flow continues same as Text Query Flow from Step 4]
  
Step 7: Response Generation
  [Same as Text Query Flow Steps 5-9]
  Django → Generates text response in English
  
Step 8: Text-to-Speech (Optional)
  Django → Checks user preference for voice response
  If voice preferred:
    Django → Invokes Amazon Polly
    Amazon Polly → Converts text to speech in user's language
    Amazon Polly → Generates audio file
    Django → Uploads audio to S3
    Django → Gets presigned URL
  
Step 9: Response Delivery
  If voice response:
    Django → Sends audio message via API Gateway
  If text response:
    Django → Sends translated text message
  WhatsApp/Telegram → Delivers to farmer
  
Step 10: Cleanup
  Lambda → Deletes temporary audio files from S3
  Lambda → Logs transcription accuracy metrics
```

**Diagram-Ready Description:**
- Start: Voice message → API Gateway → Lambda (Voice)
- Lambda → S3 (temp storage) → Amazon Transcribe
- Transcribe → Text output → Django (same flow as text query)
- Response branch: Text path OR Polly (TTS) → Audio path
- End: Delivery via API Gateway → User
- Cleanup: S3 temp file deletion

### 5.4 Photo Diagnosis Flow

```
Step 1: User Uploads Photo
  Farmer → Takes photo of crop issue
  Farmer → Sends image via WhatsApp/Telegram
  Optional: Adds caption "What is this problem?"
  
Step 2: Image Reception
  WhatsApp/Telegram → Sends webhook with image URL
  API Gateway → Routes to Lambda (Image Handler)
  
Step 3: Image Download & Validation
  Lambda → Downloads image from messaging platform
  Lambda → Validates:
           - File type (JPEG, PNG, HEIC)
           - File size (< 10MB)
           - Image dimensions (min 224x224)
  Lambda → If invalid, requests new photo
  
Step 4: Image Storage
  Lambda → Generates unique image_id
  Lambda → Uploads to S3: /crop-images/{user_id}/{timestamp}/{image_id}.jpg
  Lambda → Generates presigned URL for processing
  
Step 5: Image Preprocessing
  Lambda → Invokes Vision Model Lambda
  Vision Lambda → Downloads image from S3
  Vision Lambda → Preprocesses:
           - Resize to 224x224
           - Normalize pixel values
           - Convert to tensor
  
Step 6: Model Inference
  Vision Lambda → Loads PyTorch model (cached)
  Vision Lambda → Runs inference
  Vision Lambda → Gets predictions:
           [
             {disease: "Early Blight", confidence: 0.87},
             {disease: "Septoria Leaf Spot", confidence: 0.11},
             {disease: "Healthy", confidence: 0.02}
           ]
  
Step 7: Confidence Evaluation
  Vision Lambda → Checks top prediction confidence
  If confidence > 80%:
    → High confidence diagnosis
  If confidence 60-80%:
    → Medium confidence, provide differential diagnosis
  If confidence < 60%:
    → Low confidence, ask clarifying questions
  
Step 8: Context Building
  Django → Receives vision model output
  Django → Fetches user profile (crop, location, stage)
  Django → Retrieves weather data
  Django → Builds context for LLM:
           {
             diagnosis: "Early Blight (87% confidence)",
             crop: "Tomato",
             stage: "Flowering",
             weather: "High humidity, 28°C",
             farming_method: "Organic"
           }
  
Step 9: Treatment Recommendation
  AI Orchestrator → Constructs prompt:
           "Based on Early Blight diagnosis in tomato (flowering stage),
            provide organic treatment recommendations considering high humidity."
  GPT-4o-mini → Generates recommendations:
           - Remove affected leaves
           - Apply neem oil spray
           - Improve air circulation
           - Avoid overhead watering
           - Monitor for spread
  
Step 10: Response Formatting
  Django → Formats response:
           "🔍 Diagnosis: Early Blight (87% confidence)
            
            📋 Immediate Actions:
            1. Remove yellow/brown leaves
            2. Spray neem oil (10ml per liter)
            3. Spray in evening, avoid rain
            
            ⚠️ Prevention:
            - Water at base, not leaves
            - Increase plant spacing
            
            💰 Cost: ₹150-200 for 2 acres
            
            ⏰ Spray today if no rain forecast"
  
Step 11: Response Delivery
  Django → Sends formatted message via API Gateway
  WhatsApp/Telegram → Delivers to farmer
  
Step 12: Follow-up Options
  System → Provides quick reply buttons:
           [Show me how] [Alternative treatment] [Is it serious?]
  System → Waits for user response
  
Step 13: Logging
  Django → Logs in DynamoDB:
           - image_id, diagnosis, confidence, recommendations
  Django → Stores in Feedback table for model improvement
  
Step 14: Low Confidence Handling (if confidence < 60%)
  System → "I'm not fully certain about this diagnosis.
            Can you answer these questions?
            - How long have you noticed this?
            - Is it spreading quickly?
            - Any recent weather changes?"
  Farmer → Provides additional context
  System → Re-evaluates with new information
```

**Diagram-Ready Description:**
- Start: Image upload → API Gateway → Lambda (Image)
- Lambda → S3 storage → Vision Lambda
- Vision Lambda: Preprocess → PyTorch Model → Predictions
- Branch on confidence: High (direct recommendation) / Low (clarifying questions)
- Django: Context building → GPT-4o-mini → Treatment recommendations
- Response formatting → API Gateway → User
- Parallel: Logging to DynamoDB and S3

### 5.5 Proactive Alert Flow

```
Step 1: Scheduled Trigger
  AWS EventBridge → Triggers Alert Engine (every 15 minutes)
  Alert Engine (EC2) → Starts alert evaluation cycle
  
Step 2: User Batch Retrieval
  Alert Engine → Queries DynamoDB Users table
  Alert Engine → Fetches active users (state = "active")
  Alert Engine → Groups by location for efficient weather API calls
  Alert Engine → Processes in batches of 10,000 users
  
Step 3: Weather Data Fetch
  Alert Engine → Calls Weather API for each unique location
  Alert Engine → Retrieves:
           - Current conditions
           - 24-hour forecast
           - 7-day forecast
           - Severe weather alerts
  Alert Engine → Caches weather data (15-minute TTL)
  
Step 4: Alert Condition Evaluation
  For each user:
    Alert Engine → Checks alert conditions:
    
    Condition 1: Heavy Rain Alert
      If forecast_24h.rainfall > 50mm:
        → Generate heavy_rain alert
    
    Condition 2: Irrigation Delay
      If forecast_6h.rainfall > 10mm AND user.last_irrigation < 24h_ago:
        → Generate irrigation_delay alert
    
    Condition 3: Spray Postponement
      If forecast_6h.rainfall > 5mm AND user.planned_spray_today:
        → Generate spray_postpone alert
    
    Condition 4: Heatwave Warning
      If forecast_3d.max_temp > 40°C:
        → Generate heatwave alert
    
    Condition 5: Dry Spell
      If no_rain_last_7d AND forecast_7d.rainfall < 5mm:
        → Generate dry_spell alert
  
Step 5: Deduplication Check
  Alert Engine → Queries DynamoDB Alerts table
  Alert Engine → Checks if same alert sent in last 24 hours
  If duplicate:
    → Skip alert
  If new or updated severity:
    → Proceed with alert generation
  
Step 6: Alert Personalization
  Alert Engine → Builds personalized alert message:
           User: Ramesh, Crop: Tomato, Location: Pune
           Alert: Heavy Rain
           
           Message:
           "🌧️ Heavy Rain Alert
           
           Expected: 65mm rain in next 24 hours
           
           ⚠️ Actions to take NOW:
           1. Delay irrigation (save ₹200 on water)
           2. Postpone any planned spraying
           3. Check drainage in your field
           4. Cover harvested produce
           
           🕐 Rain starts: Tomorrow 6 AM
           
           Stay safe! Reply if you have questions."
  
Step 7: Alert Delivery
  Alert Engine → Sends message via WhatsApp/Telegram API
  Alert Engine → Uses template message for faster delivery
  Alert Engine → Implements retry logic (3 attempts)
  
Step 8: Alert Logging
  Alert Engine → Stores in DynamoDB Alerts table:
           {
             user_id: "user_123",
             alert_type: "heavy_rain",
             condition: "rainfall_65mm_24h",
             message: [full message],
             sent_at: timestamp,
             acknowledged: false
           }
  Alert Engine → Sets TTL for 7 days (automatic cleanup)
  
Step 9: Delivery Confirmation
  WhatsApp/Telegram → Sends delivery status webhook
  Alert Engine → Updates alert record with delivery status
  Alert Engine → Logs failed deliveries for retry
  
Step 10: User Acknowledgment (Optional)
  Farmer → Reads alert, may reply "OK" or ask questions
  System → Marks alert as acknowledged
  System → If question asked, routes to normal query flow
  
Step 11: Metrics Collection
  Alert Engine → Logs metrics to CloudWatch:
           - Alerts generated per cycle
           - Alerts sent successfully
           - Failed deliveries
           - User acknowledgment rate
  
Step 12: Cycle Completion
  Alert Engine → Waits for next scheduled trigger (15 minutes)
  Alert Engine → Cleans up temporary data
```

**Diagram-Ready Description:**
- Start: EventBridge (cron) → Alert Engine (EC2)
- Alert Engine → DynamoDB (fetch users) → Weather API (batch fetch)
- For each user: Evaluate conditions → Check deduplication
- If alert needed: Personalize message → Send via API Gateway
- Log to DynamoDB Alerts table → Update delivery status
- Parallel: CloudWatch metrics logging
- End: Wait for next cycle

### 5.6 Weekly Action Plan Flow


```
Step 1: Scheduled Trigger
  AWS EventBridge → Triggers Weekly Plan Generator (Every Monday 6 AM IST)
  Plan Generator (EC2) → Starts plan generation cycle
  
Step 2: User Retrieval
  Plan Generator → Queries DynamoDB for active users
  Plan Generator → Filters users with complete profiles
  Plan Generator → Processes in batches of 5,000
  
Step 3: Crop Stage Calculation
  For each user:
    Plan Generator → Calculates days since planting
    Plan Generator → Determines current crop stage:
           - Germination (0-10 days)
           - Vegetative (11-30 days)
           - Flowering (31-60 days)
           - Fruiting (61-90 days)
           - Harvest (90+ days)
    Plan Generator → Identifies critical activities for stage
  
Step 4: Weather Integration
  Plan Generator → Fetches 7-day weather forecast for user location
  Plan Generator → Identifies weather constraints:
           - Rainy days (avoid spraying)
           - Hot days (increase irrigation)
           - Optimal spray windows
  
Step 5: Task Generation
  Plan Generator → Builds task list based on:
           - Crop stage requirements
           - Weather forecast
           - User farming method (organic/conventional)
           - Budget constraints
  
  Example tasks for Tomato (Flowering stage):
    - Irrigation: Monday, Wednesday, Friday (if no rain)
    - Fertilizer: Apply potassium-rich fertilizer (Thursday)
    - Pest scouting: Check for whiteflies (Tuesday, Saturday)
    - Pruning: Remove lower leaves for air circulation
    - Staking: Ensure plants are properly supported
  
Step 6: Task Prioritization
  Plan Generator → Assigns priority to each task:
           - Critical (must do this week)
           - Important (recommended)
           - Optional (if time permits)
  Plan Generator → Schedules tasks on specific days
  Plan Generator → Considers weather windows
  
Step 7: Cost Estimation
  Plan Generator → Calculates input costs:
           - Fertilizer: ₹300 for 2 acres
           - Pesticide (if needed): ₹250
           - Labor: ₹500
           Total: ₹1,050
  Plan Generator → Provides budget-friendly alternatives if needed
  
Step 8: Plan Formatting
  Plan Generator → Formats weekly plan:
           "📅 Your Weekly Action Plan (May 12-18)
           
           🌱 Crop Stage: Flowering (Day 35)
           🌤️ Weather: Mostly sunny, rain on Thursday
           
           MONDAY (May 12)
           ✅ Irrigate in morning (2 hours)
           ✅ Scout for pests (30 mins)
           
           TUESDAY (May 13)
           ✅ Apply potassium fertilizer (1 hour)
           💰 Cost: ₹300
           
           WEDNESDAY (May 14)
           ⚠️ No irrigation - rain expected
           ✅ Check drainage
           
           THURSDAY (May 15)
           🌧️ Rainy day - no field work
           
           FRIDAY (May 16)
           ✅ Irrigate if soil dry (check first)
           ✅ Prune lower leaves
           
           SATURDAY (May 17)
           ✅ Pest scouting (focus on whiteflies)
           ✅ Check staking
           
           SUNDAY (May 18)
           ✅ Rest day / catch up on pending tasks
           
           💰 Total estimated cost: ₹1,050
           ⏱️ Total time: 8-10 hours
           
           Reply 'Done' after completing tasks!"
  
Step 9: Plan Delivery
  Plan Generator → Sends plan via WhatsApp/Telegram API
  Plan Generator → Uses long message format (split if needed)
  Plan Generator → Implements retry logic
  
Step 10: Plan Storage
  Plan Generator → Stores plan in DynamoDB:
           {
             user_id: "user_123",
             week_start: "2026-05-12",
             tasks: [array of tasks],
             sent_at: timestamp,
             completion_status: {}
           }
  
Step 11: Task Tracking Setup
  Plan Generator → Enables task completion tracking
  System → Allows user to mark tasks as done
  System → Sends reminders for pending critical tasks
  
Step 12: Metrics Logging
  Plan Generator → Logs to CloudWatch:
           - Plans generated
           - Plans delivered successfully
           - Average tasks per plan
  
Step 13: Cycle Completion
  Plan Generator → Waits for next Monday 6 AM
```

**Diagram-Ready Description:**
- Start: EventBridge (Monday 6 AM) → Plan Generator (EC2)
- Plan Generator → DynamoDB (users) → Crop stage calculation
- Weather API → 7-day forecast → Task generation
- Task prioritization → Cost estimation → Plan formatting
- Delivery via API Gateway → WhatsApp/Telegram → User
- Store plan in DynamoDB → Enable task tracking
- End: CloudWatch metrics logging

---

## 6. AI Decision & Reasoning Logic

### 6.1 Context Building

**Purpose:** Aggregate all relevant information to provide personalized, accurate recommendations.

**Context Components:**

**User Profile Context:**
```python
user_context = {
    "crop": "Tomato",
    "variety": "Hybrid - Arka Rakshak",
    "location": {
        "district": "Pune",
        "state": "Maharashtra",
        "pin_code": "411001",
        "coordinates": [18.5204, 73.8567]
    },
    "farm_size": 2.0,  # acres
    "farming_method": "organic",
    "budget_preference": "medium",
    "language": "hindi",
    "planting_date": "2026-04-01",
    "crop_stage": "flowering",  # calculated
    "days_since_planting": 37
}
```

**Weather Context:**
```python
weather_context = {
    "current": {
        "temperature": 32,  # Celsius
        "humidity": 65,  # percentage
        "rainfall_today": 0,
        "wind_speed": 12  # km/h
    },
    "forecast_24h": {
        "max_temp": 35,
        "min_temp": 24,
        "rainfall_probability": 70,
        "expected_rainfall": 15  # mm
    },
    "forecast_7d": [
        {"date": "2026-05-08", "rainfall": 15, "temp_max": 35},
        {"date": "2026-05-09", "rainfall": 0, "temp_max": 36},
        # ... 5 more days
    ],
    "last_rainfall": "2026-05-03",  # 5 days ago
    "cumulative_rainfall_7d": 25  # mm
}
```

**Conversation Context:**
```python
conversation_context = {
    "session_id": "sess_abc123",
    "last_5_messages": [
        {"role": "user", "content": "My tomato leaves are curling", "timestamp": "..."},
        {"role": "assistant", "content": "This could be due to...", "timestamp": "..."},
        # ... 3 more exchanges
    ],
    "current_query": "Should I spray today?",
    "query_type": "spray_timing",
    "urgency": "normal"
}
```

**Regional Context (Optional):**
```python
regional_context = {
    "pest_outbreaks": [
        {"pest": "Whitefly", "severity": "moderate", "distance_km": 8}
    ],
    "disease_alerts": [],
    "government_advisories": [
        {"title": "Heatwave warning", "valid_until": "2026-05-10"}
    ]
}
```

**Aggregated Context Object:**
```python
full_context = {
    "user": user_context,
    "weather": weather_context,
    "conversation": conversation_context,
    "regional": regional_context,
    "timestamp": "2026-05-07T14:30:00Z"
}
```

### 6.2 Confidence Scoring

**Purpose:** Quantify certainty in AI recommendations to ensure safe, reliable advice.

**Scoring Methodology:**

**LLM Response Confidence:**
- Analyze response for hedging language ("might", "possibly", "could be")
- Check for contradictions within response
- Validate against knowledge base facts
- Score: 0-100%

**Vision Model Confidence:**
- Direct output from softmax layer (model's own confidence)
- Calibrated using validation dataset
- Adjusted based on image quality metrics
- Score: 0-100%

**Weather-Based Confidence:**
- Forecast reliability decreases with time horizon
- 24-hour forecast: 90% confidence
- 7-day forecast: 70% confidence
- Adjust recommendations based on forecast confidence

**Confidence Thresholds:**

```python
def determine_action(confidence_score):
    if confidence_score >= 80:
        return "provide_direct_recommendation"
    elif confidence_score >= 60:
        return "provide_recommendation_with_caveats"
    elif confidence_score >= 40:
        return "ask_clarifying_questions"
    else:
        return "safe_fallback_advice"
```

**Confidence Communication:**
- High (80-100%): "I recommend..."
- Medium (60-79%): "Based on the information, I suggest... However, consider..."
- Low (40-59%): "I'm not fully certain, but here are some options..."
- Very Low (<40%): "I need more information to provide accurate advice..."

### 6.3 Safe Fallback Behavior

**Purpose:** Ensure farmers receive helpful, safe advice even when AI confidence is low.

**Fallback Strategies:**

**Strategy 1: Conservative Recommendations**
- Default to organic, low-risk methods
- Recommend observation before action
- Suggest consulting local experts
- Provide general best practices

**Strategy 2: Clarifying Questions**
```
Low confidence scenario: Unclear crop disease from photo

Fallback response:
"I see some discoloration on the leaves, but I need more information:
1. How long have you noticed this?
2. Is it spreading to other plants?
3. Any recent changes in watering or weather?
4. Can you send a closer photo of the affected area?

Meanwhile, remove severely affected leaves and monitor closely."
```

**Strategy 3: Multiple Options**
```
Uncertain scenario: Ambiguous fertilizer timing

Fallback response:
"Based on your crop stage, here are two safe options:
Option 1: Apply half dose now, half dose in 10 days (safer)
Option 2: Wait 5 days and apply full dose (if weather permits)

I recommend Option 1 for your organic farming method."
```

**Strategy 4: Safety-First Defaults**
- Never recommend excessive chemical use
- Always mention safety precautions
- Provide pre-harvest intervals for chemicals
- Warn about weather constraints

**Fallback Decision Tree:**
```
Query received
    ↓
Confidence < 70%?
    ↓ Yes
Can ask clarifying questions?
    ↓ Yes → Ask questions → Re-evaluate
    ↓ No
Is query safety-critical? (pesticide, disease)
    ↓ Yes → Provide conservative advice + recommend expert
    ↓ No → Provide general best practices + caveats
```

### 6.4 User Feedback Loop

**Purpose:** Continuously improve AI accuracy through user feedback and outcome tracking.

**Feedback Collection:**

**Implicit Feedback:**
- User asks follow-up questions → May indicate unclear response
- User marks task as completed → Positive signal
- User doesn't acknowledge alert → May indicate irrelevance

**Explicit Feedback:**
- Thumbs up/down on responses
- Rating scale (1-5 stars)
- Free-text feedback
- Outcome reporting ("This advice worked!" or "Problem persisted")

**Feedback Storage:**
```python
feedback_record = {
    "interaction_id": "int_xyz789",
    "user_id": "user_123",
    "query": "Should I spray today?",
    "response": "No, rain expected...",
    "confidence_score": 85,
    "feedback_type": "explicit",
    "rating": 5,
    "feedback_text": "Saved money, thanks!",
    "outcome": "positive",
    "timestamp": "2026-05-07T15:00:00Z"
}
```

**Feedback Processing:**

**Daily Aggregation:**
- Calculate average rating per query type
- Identify low-rated responses for review
- Track confidence score vs. user satisfaction correlation

**Weekly Analysis:**
- Identify patterns in negative feedback
- Detect systematic errors (e.g., weather forecast inaccuracies)
- Prioritize improvements based on impact

**Model Improvement:**
- Use feedback to fine-tune vision models
- Adjust confidence thresholds based on accuracy
- Update prompt templates for better responses
- Expand knowledge base with new scenarios

**Feedback Loop Diagram:**
```
User receives recommendation
    ↓
User provides feedback (explicit or implicit)
    ↓
Feedback stored in DynamoDB
    ↓
Daily/Weekly aggregation
    ↓
Analysis identifies improvement areas
    ↓
Model retraining / Prompt updates
    ↓
Improved recommendations
    ↓
(Loop continues)
```

---

## 7. Scalability & Cost Optimization


### 7.1 Lambda Auto-Scaling

**Purpose:** Handle variable load efficiently by scaling compute resources automatically.

**Scaling Configuration:**

**Text/Voice Query Lambda:**
- Reserved concurrency: 100 (baseline capacity)
- Provisioned concurrency: 50 (warm instances for low latency)
- Maximum concurrency: 1,000 (burst capacity)
- Scaling trigger: Queue depth > 10 messages
- Scale-up time: < 1 minute
- Scale-down time: 5 minutes (gradual)

**Image Processing Lambda:**
- Reserved concurrency: 50
- Provisioned concurrency: 10 (GPU-enabled instances)
- Maximum concurrency: 200
- Memory: 10GB (for model loading)
- Timeout: 30 seconds

**Scaling Patterns:**

**Normal Load (Off-Peak):**
- 50 provisioned instances handle ~80% of requests
- Average response time: < 2 seconds
- Cost: Provisioned concurrency charges only

**Peak Load (Morning Hours, Weather Events):**
- Auto-scale to 500+ concurrent executions
- Burst capacity handles 5x normal load
- Average response time: < 5 seconds
- Cost: Pay per invocation (on-demand pricing)

**Cost Optimization:**
- Use provisioned concurrency only for critical hours (6 AM - 10 PM IST)
- Scale down to reserved concurrency during night hours
- Monitor cold start metrics and adjust provisioned capacity

### 7.2 Efficient LLM Usage

**Purpose:** Minimize AI inference costs while maintaining response quality.

**Optimization Strategies:**

**1. Response Caching:**
```python
# Cache identical queries for 1 hour
cache_key = hash(user_context + query)
cached_response = redis.get(cache_key)
if cached_response and cache_age < 3600:
    return cached_response
else:
    response = call_llm(prompt)
    redis.set(cache_key, response, ttl=3600)
    return response
```

**Benefits:**
- Reduce duplicate LLM calls by 30-40%
- Save ~₹2-3 per user per month
- Faster response times for common queries

**2. Prompt Optimization:**
- Keep prompts concise (< 1,000 tokens)
- Use structured output formats to reduce response tokens
- Avoid unnecessary context in prompts
- Use few-shot examples sparingly

**Token Usage Targets:**
- Average prompt: 500 tokens
- Average response: 200 tokens
- Total per interaction: 700 tokens
- Cost per interaction: ~₹0.05 (at GPT-4o-mini pricing)

**3. Model Selection:**
- Use GPT-4o-mini for most queries (cost-effective)
- Reserve GPT-4 for complex, high-stakes decisions
- Use rule-based responses for simple queries (e.g., "What is your location?")

**4. Batch Processing:**
- Queue non-urgent queries (weekly plans, analytics)
- Process in batches during off-peak hours
- Reduce API call overhead

**5. Smart Routing:**
```python
def route_query(query, confidence_threshold=0.8):
    # Simple queries → Rule-based system (free)
    if is_simple_query(query):
        return rule_based_response(query)
    
    # Medium complexity → GPT-4o-mini (cheap)
    elif is_medium_complexity(query):
        return gpt4o_mini_response(query)
    
    # High complexity → GPT-4 (expensive, high quality)
    else:
        return gpt4_response(query)
```

**Cost Breakdown (per user per month):**
- 20 interactions × ₹0.05 = ₹1.00 (LLM costs)
- 30% cache hit rate → ₹0.70 actual cost
- Vision model (2 images) → ₹0.50
- Total AI costs: ₹1.20 per user per month

### 7.3 Caching & Async Processing

**Purpose:** Reduce latency and costs through intelligent caching and asynchronous operations.

**Caching Strategy:**

**1. Weather Data Caching:**
```python
# Cache weather data by location
cache_key = f"weather:{pin_code}:{date}"
ttl = 1800  # 30 minutes

weather_data = cache.get(cache_key)
if not weather_data:
    weather_data = fetch_from_weather_api(pin_code)
    cache.set(cache_key, weather_data, ttl)
```

**Benefits:**
- Reduce weather API calls by 90%
- Save ~₹0.50 per user per month
- Faster response times (cache hit: 5ms vs API call: 500ms)

**2. User Profile Caching:**
```python
# Cache user profiles in Redis
cache_key = f"user:{user_id}"
ttl = 3600  # 1 hour

user_profile = cache.get(cache_key)
if not user_profile:
    user_profile = dynamodb.get_item(user_id)
    cache.set(cache_key, user_profile, ttl)
```

**Benefits:**
- Reduce DynamoDB read costs by 70%
- Faster context building (10ms vs 50ms)

**3. LLM Response Caching:**
- Cache responses for identical queries (1-hour TTL)
- Cache common knowledge (crop care basics) indefinitely
- Invalidate cache on user profile changes

**Async Processing:**

**1. Non-Urgent Operations:**
- Analytics aggregation
- Feedback processing
- Model retraining
- Log archival

**2. Background Jobs:**
```python
# Queue non-urgent tasks
celery.send_task('process_feedback', args=[feedback_data])
celery.send_task('aggregate_metrics', args=[date])
celery.send_task('generate_weekly_report', args=[user_id])
```

**3. Async Image Processing:**
- User uploads image → Immediate acknowledgment
- Image processing happens in background
- User receives diagnosis within 10 seconds
- Allows user to continue conversation while processing

**Cache Architecture:**
```
User Request
    ↓
Check Redis Cache
    ↓ Cache Miss
Fetch from Source (DynamoDB, Weather API, LLM)
    ↓
Store in Cache (with TTL)
    ↓
Return to User
```

### 7.4 Cost Breakdown: ₹8-₹10 per User per Month

**Target:** 100,000 monthly active users, 20 interactions per user

**Cost Components:**

**1. Compute Costs (AWS Lambda):**
- Text queries: 18 × ₹0.02 = ₹0.36
- Voice queries: 2 × ₹0.05 = ₹0.10
- Image processing: 2 × ₹0.15 = ₹0.30
- **Subtotal: ₹0.76 per user**

**2. AI/ML Costs:**
- LLM inference (GPT-4o-mini): 20 × ₹0.05 × 0.7 (cache) = ₹0.70
- Vision model inference: 2 × ₹0.25 = ₹0.50
- Transcribe (voice): 2 × ₹0.10 = ₹0.20
- Polly (TTS): 2 × ₹0.05 = ₹0.10
- **Subtotal: ₹1.50 per user**

**3. Data Storage (DynamoDB + S3):**
- DynamoDB reads: 100 × ₹0.0001 = ₹0.01
- DynamoDB writes: 25 × ₹0.0005 = ₹0.0125
- S3 storage (images): ₹0.10
- S3 requests: ₹0.05
- **Subtotal: ₹0.18 per user**

**4. External APIs:**
- Weather API: ₹0.30 per user (with caching)
- WhatsApp Business API: ₹0.50 per user (20 messages)
- **Subtotal: ₹0.80 per user**

**5. Networking & Data Transfer:**
- API Gateway: ₹0.20
- Data transfer: ₹0.15
- **Subtotal: ₹0.35 per user**

**6. Proactive Services (EC2 for Alerts):**
- EC2 instance (t3.medium): ₹3,000/month
- Cost per user: ₹3,000 / 100,000 = ₹0.03
- **Subtotal: ₹0.03 per user**

**7. Monitoring & Logging:**
- CloudWatch: ₹0.10 per user
- **Subtotal: ₹0.10 per user**

**8. Overhead & Buffer:**
- Miscellaneous: ₹0.28 per user
- **Subtotal: ₹0.28 per user**

**Total Cost per User per Month: ₹4.00**

**With 50% buffer for growth and inefficiencies: ₹6.00**

**Target range: ₹8-₹10 achieved with room for additional features**

**Cost Optimization Levers:**
- Increase cache hit rates (target 80% for weather, 40% for LLM)
- Negotiate volume discounts with OpenAI and weather API providers
- Optimize Lambda memory allocation (right-sizing)
- Use spot instances for non-critical batch jobs
- Implement tiered service (free tier with ads, premium tier)

**Scaling Economics:**
- At 100K users: ₹6.00 per user
- At 500K users: ₹4.50 per user (economies of scale)
- At 1M users: ₹3.50 per user

---

## 8. Reliability, Security & Privacy

### 8.1 Data Durability

**Purpose:** Ensure user data is never lost and can be recovered in disaster scenarios.

**DynamoDB Durability:**
- Built-in replication across 3 Availability Zones
- 99.999999999% (11 nines) durability
- Point-in-time recovery (PITR) enabled
- Continuous backups for 35 days
- On-demand backups for long-term retention

**S3 Durability:**
- 99.999999999% (11 nines) durability
- Cross-region replication to secondary region (Mumbai → Singapore)
- Versioning enabled for critical data
- Lifecycle policies for cost optimization

**Backup Strategy:**
- Daily automated backups of DynamoDB tables
- Weekly full backups to S3 Glacier
- Monthly backups retained for 1 year
- Backup testing quarterly

**Recovery Objectives:**
- RPO (Recovery Point Objective): < 24 hours
- RTO (Recovery Time Objective): < 4 hours
- Data retention: 2 years for active users, 5 years for compliance

### 8.2 Fault Tolerance

**Purpose:** Maintain service availability despite component failures.

**Multi-AZ Deployment:**
- Django backend: ECS tasks across 3 Availability Zones
- Lambda: Automatically distributed across AZs
- DynamoDB: Multi-AZ by default
- Load balancing across healthy instances

**Redundancy:**
- Multiple Lambda instances (auto-scaling)
- Multiple ECS tasks (minimum 3 running)
- Multiple weather API providers (primary + backup)
- Multiple messaging platform endpoints

**Circuit Breaker Pattern:**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func):
        if self.state == "OPEN":
            if time.now() - self.last_failure > self.timeout:
                self.state = "HALF_OPEN"
            else:
                return fallback_response()
        
        try:
            result = func()
            self.failure_count = 0
            self.state = "CLOSED"
            return result
        except Exception:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure = time.now()
            raise
```

**Graceful Degradation:**
- Weather API down → Use cached data + disclaimer
- LLM API down → Use rule-based responses
- Vision model down → Request text description instead
- Database slow → Serve from cache, queue writes

**Health Checks:**
- Lambda: Automatic health monitoring by AWS
- ECS: Health check endpoint (`/health`) every 30 seconds
- DynamoDB: CloudWatch alarms on throttling
- External APIs: Periodic health checks (every 5 minutes)

### 8.3 User Data Protection

**Purpose:** Protect farmer data from unauthorized access and ensure privacy compliance.

**Data Encryption:**

**At Rest:**
- DynamoDB: AWS-managed encryption (AES-256)
- S3: Server-side encryption (SSE-S3)
- EBS volumes: Encrypted with AWS KMS
- Backups: Encrypted before storage

**In Transit:**
- TLS 1.3 for all API communications
- HTTPS only (no HTTP)
- Encrypted webhooks from messaging platforms
- VPC endpoints for internal AWS service communication

**Access Control:**

**IAM Policies:**
- Principle of least privilege
- Separate roles for Lambda, ECS, EC2
- No hardcoded credentials
- Temporary credentials with STS

**Data Access Logging:**
- CloudTrail: All API calls logged
- DynamoDB: Access logs to S3
- S3: Access logs enabled
- Audit trail for compliance

**Privacy Compliance:**

**Data Minimization:**
- Collect only necessary information
- No sensitive personal data (Aadhaar, bank details)
- Phone numbers hashed for storage
- Images deleted after 90 days

**User Rights:**
- Right to access: Users can request their data
- Right to deletion: Users can delete their account
- Right to portability: Users can export their data
- Consent management: Explicit opt-in during onboarding

**Data Retention:**
- Active user data: Retained indefinitely
- Inactive users (> 6 months): Data archived
- Deleted users: Data purged within 30 days
- Conversation history: 90-day retention

**Anonymization for Analytics:**
- Remove PII before analytics processing
- Aggregate data at district level (not individual)
- Use pseudonymous IDs for model training
- No sharing with third parties without consent

**Security Monitoring:**
- AWS GuardDuty: Threat detection
- CloudWatch Alarms: Anomaly detection
- Failed login attempts: Rate limiting
- Suspicious activity: Automatic blocking

**Incident Response:**
- Security incident playbook documented
- Automated alerts for security events
- 24-hour response time for critical incidents
- User notification within 72 hours (GDPR compliance)

---

## 9. Error Handling & Edge Cases

### 9.1 Unclear Images

**Problem:** User uploads blurry, dark, or irrelevant images.

**Detection:**
```python
def validate_image_quality(image):
    # Check resolution
    if image.width < 224 or image.height < 224:
        return {"valid": False, "reason": "resolution_too_low"}
    
    # Check brightness
    brightness = calculate_brightness(image)
    if brightness < 30 or brightness > 230:
        return {"valid": False, "reason": "poor_lighting"}
    
    # Check blur
    blur_score = calculate_blur(image)
    if blur_score < 100:
        return {"valid": False, "reason": "image_too_blurry"}
    
    # Check if crop is visible
    crop_detected = detect_crop_presence(image)
    if not crop_detected:
        return {"valid": False, "reason": "no_crop_visible"}
    
    return {"valid": True}
```

**Response Strategy:**
```
If resolution_too_low:
    "The image is too small. Please take a closer photo of the affected area."

If poor_lighting:
    "The image is too dark/bright. Please take a photo in natural daylight."

If image_too_blurry:
    "The image is blurry. Please hold your phone steady and take a clear photo."

If no_crop_visible:
    "I can't see the crop clearly. Please take a photo showing the leaves or affected parts."
```

**Retry Mechanism:**
- Allow up to 3 image uploads per query
- Provide specific guidance for each retry
- Offer text-based diagnosis as fallback

### 9.2 Low Confidence Predictions

**Problem:** Vision model or LLM provides low-confidence predictions.

**Handling Strategy:**

**For Vision Models (confidence < 60%):**
```python
if top_prediction_confidence < 0.6:
    response = f"""
    I'm not fully certain about this diagnosis. Here's what I see:
    
    Possible issues:
    1. {prediction_1} ({confidence_1}% confidence)
    2. {prediction_2} ({confidence_2}% confidence)
    
    To help me diagnose better, please answer:
    - How long have you noticed this problem?
    - Is it spreading to other plants?
    - Any recent changes in weather or watering?
    
    Meanwhile, as a precaution:
    - Remove severely affected leaves
    - Avoid overhead watering
    - Monitor closely for changes
    
    Send more photos or details for accurate diagnosis.
    """
```

**For LLM Responses (ambiguous queries):**
```python
if query_ambiguity_score > 0.7:
    response = """
    I need a bit more information to give you the best advice:
    
    1. Which crop are you asking about?
    2. What specific problem are you facing?
    3. When did you first notice this?
    
    Or you can send a photo for visual diagnosis.
    """
```

**Safe Fallback Advice:**
- Provide general best practices
- Recommend observation before action
- Suggest consulting local agricultural officer
- Avoid specific chemical recommendations

### 9.3 Missing User Inputs

**Problem:** User profile incomplete or missing critical information.

**Detection:**
```python
def validate_user_profile(user):
    required_fields = ["crop", "location", "planting_date"]
    missing_fields = [f for f in required_fields if not user.get(f)]
    return missing_fields
```

**Handling:**

**During Query Processing:**
```
If crop missing:
    "I need to know which crop you're growing to provide accurate advice.
     Please tell me your crop name."

If location missing:
    "I need your location to check weather and provide local advice.
     Please share your PIN code or location."

If planting_date missing:
    "When did you plant this crop? This helps me understand the growth stage."
```

**Graceful Degradation:**
- Provide generic advice if non-critical fields missing
- Prompt user to complete profile for better recommendations
- Allow partial profile for basic queries

### 9.4 Weather API Failures

**Problem:** Weather API is down or returns errors.

**Detection & Fallback:**
```python
def get_weather_data(location):
    try:
        # Try primary weather API
        weather = primary_weather_api.get(location)
        return weather
    except APIError:
        try:
            # Fallback to secondary API
            weather = secondary_weather_api.get(location)
            return weather
        except APIError:
            # Use cached data
            cached_weather = cache.get(f"weather:{location}")
            if cached_weather:
                return {
                    **cached_weather,
                    "disclaimer": "Using recent weather data (API temporarily unavailable)"
                }
            else:
                # No cache available
                return {
                    "available": False,
                    "message": "Weather data temporarily unavailable"
                }
```

**User Communication:**
```
If using cached data:
    "⚠️ Note: Using recent weather data as live data is temporarily unavailable.
     
     [Provide recommendation based on cached data]
     
     Please check local weather before taking action."

If no data available:
    "I'm unable to fetch current weather data right now.
     
     For irrigation/spraying decisions, please:
     - Check local weather forecast
     - Look at sky conditions
     - Feel soil moisture before irrigating
     
     I'll be able to provide weather-based advice once the service is restored."
```

**Monitoring & Alerts:**
- CloudWatch alarm on weather API failures
- Automatic failover to backup API
- Team notification for prolonged outages
- User notification if outage > 1 hour

### 9.5 Additional Edge Cases

**Unsupported Crop:**
```
"I currently provide detailed advice for [list of supported crops].
 
 For [unsupported crop], I can offer general farming guidance.
 Would you like general advice, or would you prefer to add another crop?"
```

**Out-of-Season Query:**
```
"It seems you're asking about [activity] for [crop], but based on your
 planting date, your crop is in [current stage].
 
 Did you mean to ask about [appropriate activity for current stage]?
 Or did you plant a new crop recently?"
```

**Conflicting Information:**
```
User says: "I planted 2 months ago" but profile shows planting_date = 1 week ago

Response: "I see a mismatch in the information. Your profile shows planting
           date as [date], but you mentioned 2 months ago.
           
           Which is correct? This helps me provide accurate advice."
```

**Rate Limiting:**
```
If user exceeds 50 messages per hour:
    "You've reached the message limit for this hour. This helps us serve
     all farmers efficiently.
     
     You can continue in [X] minutes, or for urgent issues, please call
     the agricultural helpline: [number]"
```

---

## 10. Future Enhancements


### 10.1 More Languages

**Current:** 8 Indian languages (Hindi, English, Marathi, Punjabi, Tamil, Telugu, Kannada, Bengali)

**Expansion Plan:**
- Phase 2: Add Gujarati, Malayalam, Odia, Assamese (4 languages)
- Phase 3: Add regional dialects and less common languages
- Phase 4: Support for neighboring countries (Nepali, Bangla, Sinhala)

**Technical Approach:**
- Leverage multilingual LLMs (GPT-4o supports 50+ languages)
- Expand Transcribe language support
- Add Polly voices for new languages
- Crowdsource translations for UI elements
- Partner with local agricultural universities for terminology

**Challenges:**
- Agricultural terminology varies by region
- Dialect variations within same language
- Limited training data for some languages

**Solution:**
- Build language-specific knowledge bases
- Use transliteration for technical terms
- Implement feedback loop for translation quality

### 10.2 Market Price Insights

**Feature:** Real-time crop price information to help farmers make selling decisions.

**Data Sources:**
- Government mandi (market) price APIs
- Agricultural Produce Market Committee (APMC) data
- Private market aggregators
- Historical price trends

**Capabilities:**
- Current prices for user's crop in nearby markets
- Price trends (last 7 days, 30 days, 1 year)
- Price forecasts based on supply-demand
- Best time to sell recommendations
- Nearby market locations and contact info

**User Interaction:**
```
Farmer: "What is the tomato price today?"

System: "🏪 Tomato Prices (Today)
         
         Nearby Markets:
         📍 Pune Mandi: ₹18-22/kg (↑ 10% from yesterday)
         📍 Hadapsar Market: ₹20-24/kg
         📍 Kothrud Market: ₹17-21/kg
         
         📊 7-Day Trend: Increasing
         💡 Recommendation: Good time to sell
         
         🔮 Forecast: Prices may drop next week due to
              increased supply from neighboring districts.
         
         Want directions to nearest market?"
```

**Integration:**
- Add "Market Prices" quick action button
- Proactive alerts when prices spike
- Integration with harvest timing recommendations

### 10.3 Government Advisory Integration

**Feature:** Integrate official government agricultural advisories and schemes.

**Data Sources:**
- Ministry of Agriculture & Farmers Welfare
- State agriculture departments
- Krishi Vigyan Kendras (KVKs)
- ICAR research institutes
- Meteorological department alerts

**Capabilities:**
- Government scheme notifications (subsidies, insurance)
- Official pest/disease alerts
- Soil health card information
- Crop insurance claim guidance
- Direct Benefit Transfer (DBT) status

**User Interaction:**
```
System (Proactive): "🏛️ Government Update
                     
                     New subsidy available for organic farmers in Maharashtra:
                     - 50% subsidy on organic inputs
                     - Up to ₹10,000 per acre
                     - Apply by: May 31, 2026
                     
                     You're eligible! Want help with application?"

Farmer: "Yes, how to apply?"

System: "Here's the step-by-step process:
         1. Visit nearest agriculture office with:
            - Aadhaar card
            - Land records (7/12 extract)
            - Organic certification (if available)
         
         2. Fill Form ABC-123
         
         3. Submit within 15 days
         
         📍 Nearest office: [Address]
         📞 Contact: [Phone]
         
         I can remind you before the deadline!"
```

**Integration:**
- Daily sync with government databases
- Personalized scheme recommendations
- Application deadline reminders
- Document checklist for applications

### 10.4 Human Expert Escalation

**Feature:** Seamless handoff to human agricultural experts for complex cases.

**When to Escalate:**
- AI confidence < 40% on critical issues
- User explicitly requests human expert
- Repeated unsuccessful diagnosis attempts
- Emergency situations (crop failure, severe outbreak)
- Legal or policy questions

**Expert Network:**
- Partner with agricultural universities
- Engage retired agricultural officers
- Collaborate with Krishi Vigyan Kendras
- Build network of certified crop consultants

**Escalation Flow:**
```
Step 1: AI Identifies Need for Escalation
  System: "This seems like a complex issue that would benefit from
           expert review. I can connect you with an agricultural expert.
           
           Options:
           1. Chat with expert (₹50, available in 2 hours)
           2. Schedule call (₹100, 15-min consultation)
           3. Field visit (₹500, expert visits your farm)
           
           Or I can continue trying to help for free."

Step 2: User Selects Option
  Farmer: "Chat with expert"

Step 3: Expert Assignment
  System: "Great! I've assigned your case to Dr. Sharma, a tomato
           specialist with 20 years of experience.
           
           I've shared your:
           - Crop details
           - Photos you sent
           - Our conversation
           
           Dr. Sharma will respond within 2 hours.
           You'll be notified here."

Step 4: Expert Response
  Expert: [Provides detailed diagnosis and recommendations]

Step 5: Follow-up
  System: "Did Dr. Sharma's advice help? Please rate the consultation."
```

**Expert Dashboard:**
- Queue of escalated cases
- Full context (user profile, conversation, images)
- Response templates for common issues
- Payment tracking for consultations

**Hybrid Model:**
- AI handles 90% of queries
- Experts handle 10% complex cases
- Experts train AI with feedback
- Continuous improvement loop

### 10.5 Additional Future Features

**Soil Health Monitoring:**
- Integration with soil testing labs
- Soil health card digitization
- Fertilizer recommendations based on soil test results
- Soil improvement tracking over seasons

**Crop Planning Assistant:**
- Crop rotation recommendations
- Intercropping suggestions
- Seasonal planning based on market demand
- Water availability-based crop selection

**Community Features:**
- Connect farmers growing same crop
- Share success stories and tips
- Local farmer groups and cooperatives
- Peer-to-peer learning

**IoT Integration:**
- Soil moisture sensors
- Weather stations
- Automated irrigation systems
- Real-time field monitoring

**Financial Services:**
- Crop loan recommendations
- Insurance claim assistance
- Input purchase financing
- Savings and investment advice

**Supply Chain Integration:**
- Direct buyer connections
- Contract farming opportunities
- Input supplier marketplace
- Logistics and transportation

**Advanced Analytics:**
- Yield prediction models
- Profit optimization
- Risk assessment
- Multi-season planning

**Voice-First Features:**
- Fully voice-navigable interface
- Voice-based tutorials
- Audio content library
- Podcast-style farming tips

---

## 11. System Architecture Summary

### 11.1 Key Design Decisions

**1. Serverless-First Architecture**
- Rationale: Auto-scaling, pay-per-use, minimal operational overhead
- Trade-off: Cold starts vs. cost savings
- Mitigation: Provisioned concurrency for critical paths

**2. Multi-Platform Messaging**
- Rationale: Meet users where they are (WhatsApp, Telegram)
- Trade-off: Platform dependency vs. accessibility
- Mitigation: Abstract messaging layer, support multiple platforms

**3. Hybrid AI Approach**
- Rationale: Balance cost, accuracy, and response time
- Components: LLM (reasoning) + Vision models (diagnosis) + Rules (simple queries)
- Trade-off: Complexity vs. flexibility

**4. Proactive Alert System**
- Rationale: Prevent problems before they occur
- Implementation: Separate EC2-based service for reliability
- Trade-off: Additional infrastructure vs. user value

**5. Context-Aware Recommendations**
- Rationale: Personalization improves accuracy and relevance
- Implementation: Rich context object built from multiple sources
- Trade-off: Latency vs. personalization quality

### 11.2 Scalability Characteristics

**Horizontal Scaling:**
- Lambda: Automatic, up to 1,000 concurrent executions
- ECS: Auto-scaling based on CPU/memory
- DynamoDB: On-demand capacity, automatic scaling
- S3: Unlimited storage, automatic scaling

**Vertical Scaling:**
- Lambda memory: Adjustable per function (128MB - 10GB)
- ECS task size: Adjustable based on load
- DynamoDB: Provisioned capacity for predictable workloads

**Geographic Scaling:**
- Current: Single region (Mumbai)
- Future: Multi-region deployment for lower latency
- CDN: CloudFront for static content

### 11.3 Performance Targets

**Response Times:**
- Text queries: < 3 seconds (95th percentile)
- Voice queries: < 5 seconds (95th percentile)
- Photo diagnosis: < 10 seconds (90th percentile)
- Proactive alerts: < 1 minute from trigger

**Throughput:**
- 2 million interactions per month
- 1,000 concurrent users
- 10,000 alerts per hour during weather events

**Availability:**
- 99.5% uptime (3.6 hours downtime per month)
- 99.9% uptime for critical paths (query processing)
- Graceful degradation during partial outages

### 11.4 Technology Stack Summary

**Cloud Platform:** Amazon Web Services (AWS)

**Compute:**
- AWS Lambda (serverless functions)
- AWS ECS with Fargate (containerized Django backend)
- AWS EC2 (alert engine, scheduled jobs)

**AI/ML:**
- AWS Bedrock (LLM orchestration)
- OpenAI GPT-4o-mini (natural language processing)
- PyTorch (computer vision models)
- Amazon Transcribe (speech-to-text)
- Amazon Polly (text-to-speech)

**Data Storage:**
- AWS DynamoDB (user profiles, conversations, feedback)
- AWS S3 (images, logs, analytics)
- ElastiCache/Redis (session cache, response cache)

**Networking:**
- AWS API Gateway (REST APIs, webhooks)
- AWS CloudFront (CDN for static content)
- VPC (network isolation)

**Monitoring & Operations:**
- AWS CloudWatch (logs, metrics, alarms)
- AWS X-Ray (distributed tracing)
- AWS CloudTrail (audit logs)

**External Services:**
- WhatsApp Business API
- Telegram Bot API
- Weather APIs (OpenWeatherMap, IMD)

**Backend Framework:**
- Django 4.2+ (Python web framework)
- Celery (async task processing)
- Django REST Framework (API development)

### 11.5 Deployment Architecture

**Development Environment:**
- Local development with Docker Compose
- Mock external APIs for testing
- SQLite for local database

**Staging Environment:**
- Mirrors production architecture
- Reduced capacity (10% of production)
- Synthetic data for testing
- Automated testing pipeline

**Production Environment:**
- Multi-AZ deployment for high availability
- Auto-scaling enabled
- Production-grade monitoring
- Automated backups and disaster recovery

**CI/CD Pipeline:**
```
Code Commit (GitHub)
    ↓
Automated Tests (GitHub Actions)
    ↓
Build Docker Images
    ↓
Push to ECR (Elastic Container Registry)
    ↓
Deploy to Staging
    ↓
Integration Tests
    ↓
Manual Approval
    ↓
Deploy to Production (Blue-Green)
    ↓
Health Checks
    ↓
Route Traffic to New Version
```

**Deployment Strategy:**
- Blue-green deployment for zero-downtime updates
- Canary releases for high-risk changes
- Automated rollback on health check failures
- Feature flags for gradual rollout

---

## 12. Conclusion

KisaanVaani's architecture is designed to deliver accessible, personalized agricultural advisory services to rural Indian farmers at scale. The system leverages modern cloud technologies, AI/ML capabilities, and familiar messaging platforms to bridge the gap between expert agricultural knowledge and farmers who need it most.

**Key Strengths:**

1. **Accessibility:** Zero learning curve through WhatsApp/Telegram interfaces
2. **Scalability:** Serverless architecture supports 100K+ users with auto-scaling
3. **Cost Efficiency:** ₹8-₹10 per user per month through optimization strategies
4. **Intelligence:** Context-aware AI provides personalized, weather-adapted recommendations
5. **Proactivity:** Alert system prevents problems before they escalate
6. **Reliability:** Multi-AZ deployment, fault tolerance, and graceful degradation

**Design Philosophy:**

- **User-Centric:** Every design decision prioritizes farmer experience and accessibility
- **Safety-First:** Conservative recommendations when confidence is low
- **Cost-Conscious:** Optimized for resource-constrained farmers and sustainable operations
- **Scalable:** Built to grow from 100K to 1M+ users without architectural changes
- **Maintainable:** Clean separation of concerns, modular components, comprehensive monitoring

This architecture provides a solid foundation for KisaanVaani's mission to democratize agricultural knowledge and empower farmers with timely, accurate, and actionable advice.

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Prepared By:** Gradient Ascent Team  
**Review Status:** Ready for Hackathon Evaluation

---

*This design document is intended for technical evaluation by hackathon judges, potential investors, and development teams. It provides a comprehensive blueprint for implementing KisaanVaani as a production-ready system.*
