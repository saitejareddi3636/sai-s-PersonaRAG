# Projects

## Enterprise Support Copilot

**Type:** Full-stack AI application, RAG, document intelligence  
**Status:** Shipped

### Overview

Full-stack RAG application where users upload support documents and receive cited answers. End-to-end system from ingestion through frontend, demonstrating production RAG patterns.

### Technical Architecture

**Document Processing:**
- Document ingestion, parsing, chunking with metadata preservation
- Semantic and keyword embedding for hybrid search
- Structured metadata for filtering and tracking

**Retrieval & Search:**
- Semantic search with vector embeddings (pgvector)
- Hybrid retrieval combining semantic + keyword search for robustness
- Optional reranking for answer quality

**Generation:**
- Grounded answer generation with explicit source citations
- Multi-model support (OpenAI, Gemini, configurable)
- Structured JSON responses with confidence scoring

**Frontend:**
- Document upload interface
- Real-time chat with message history
- Source inspection and citation display

### Technical Stack

- **Backend:** FastAPI, Python async, real-time streaming
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Database:** PostgreSQL with pgvector extension
- **Embeddings:** OpenAI, Gemini (configurable)
- **Deployment:** Docker, AWS

### Key Learnings

- Hybrid retrieval beats pure semantic or keyword search
- Citation accuracy matters more than throughput
- Vector database integration with SQL metadata
- Frontend + backend coordination for real-time UX

---

## Customer Feedback Intelligence System

**Type:** NLP, ML pipeline, semantic search, evaluation  
**Status:** Production

### Overview

NLP pipeline analyzing 50,000+ user feedback reports using BERT embeddings and semantic search to identify recurring themes and critical issues automatically, eliminating manual triage.

### Technical Architecture

**Data Processing:**
- Built NLP pipelines for clustering and thematic analysis
- Processed 50,000+ feedback records with quality assurance

**Classification:**
- Fine-tuned DistilBERT for multi-label text classification
- Achieved 91% F1 score for categorizing by product area and severity
- Structured JSON outputs for downstream systems

**Triage & Escalation:**
- LLM-powered automated triage using tool calling
- Structured summarization prompts for escalation
- Reduced average response time for high-severity feedback by ~50%

**Inference & Search:**
- Scalable batch processing pipeline
- Vector database similarity search (FAISS, Qdrant)
- SQL-backed metadata filtering

### Technical Stack

- **ML:** PyTorch, Hugging Face Transformers, DistilBERT, PEFT
- **Embeddings:** BERT embeddings, FAISS, Qdrant vector DB
- **Backend:** FastAPI, SQL
- **LLMs:** OpenAI API for triage and summarization
- **Infrastructure:** Batch processing, real-time inference

### Key Outcomes

- Automated analysis of 50,000+ feedback records
- 91% F1 score on multi-label classification
- ~50% reduction in response time for critical issues
- End-to-end pipeline from raw feedback to actionable alerts

---

## Pretty Good AI – Voice QA Bot

**Type:** Voice AI, telephony, evaluation framework  
**Status:** Shipped

### Overview

Automated voice AI QA platform that places real phone calls with Twilio, executes multi-turn patient scenarios, records responses, and generates transcripts and structured bug reports for conversational agent testing.

### Technical Architecture

**Telephony Orchestration:**
- Real phone call placement via Twilio API
- Multi-turn scenario execution with state management
- Response recording and transcription

**Evaluation:**
- Batch evaluation pipeline analyzing call outcomes
- Scenario performance ranking
- Summary reports and failure analysis

**Backend:**
- Modular Python workflows for orchestration
- Artifact storage and report generation
- Reproducible test execution and traceability

### Technical Stack

- **Telephony:** Twilio API
- **Backend:** FastAPI, Uvicorn, Python async
- **LLMs:** OpenAI API for scenario execution
- **Storage:** Local/cloud artifact storage

### Key Outcomes

- Scalable regression testing for voice agents
- Reproducible failure analysis and reporting
- Real-world conversation simulation
- Faster issue identification vs. manual testing

---

## Open Claw – Secure Agent Runtime

**Type:** Systems engineering, security, runtime isolation  
**Status:** Completed

### Overview

Secure runtime for AI agents on Linux using OS-level isolation rather than prompt-based safety alone. Demonstrates that agents need infrastructure-level guarantees.

### Technical Architecture

**Control Plane (Go):**
- Agent run lifecycle management
- Configuration loading and management
- API exposure for run operations
- Audit event logging and state storage

**Sandbox Runtime (Rust):**
- Linux namespaces for process isolation
- Chroot and cgroups v2 for filesystem/resource restrictions
- Dedicated user execution for permission isolation
- Network namespace isolation

**Execution Layer:**
- Deny-by-default tool execution model
- Policy validation for all file and command operations
- Structured logging for allowed and denied actions
- Traceable and enforceable agent behavior

### Technical Stack

- **Control:** Go, SQLite
- **Runtime:** Rust, Linux system calls
- **Infrastructure:** Linux namespaces, cgroups, seccomp
- **Logging:** Structured audit logs

### Why This Matters

- Production AI agents need OS-level guarantees, not just prompt engineering
- Demonstrates systems thinking applied to AI safety
- Shows comfort with systems programming (Go + Rust)
- Real defense-in-depth (isolation + policy enforcement)
- Vector search and semantic retrieval
- Citation and source tracking

### Why this matters

Demonstrates full-stack capability in RAG: ingestion, embeddings, retrieval quality, grounded generation, and user experience. Shows production thinking about retrieval quality and user transparency.

---

## Customer Feedback Intelligence System – NLP Classification

**Type:** Machine learning, NLP, classification pipeline

### Overview

Processed 50,000+ user feedback records. Extracted insights using embeddings and fine-tuned classification models.

### Technical approach

- BERT embeddings for semantic representation
- Vector search and clustering for insight discovery
- Fine-tuned DistilBERT for multi-label classification
- Strong classification metrics on test data
- Structured output and integration with downstream systems
- Scalable inference and triage workflows

### Technical stack

- PyTorch, Hugging Face Transformers
- BERT, DistilBERT, fine-tuning
- Vector search (FAISS or similar)
- Inference optimization

### Why this matters

Demonstrates hands-on ML experience: model selection, fine-tuning, evaluation, and production deployment of classification systems at scale.

---

## Pretty Good AI Voice QA Bot – Voice AI Testing

**Type:** Voice AI, testing and automation, QA platform

### Overview

Built automated QA system for voice AI. System placed real calls via Twilio, executed multi-turn scenarios, and generated structured bug reports.

### Technical approach

- Twilio integration for real phone calls
- Multi-turn conversation scripting and execution
- Transcript generation and analysis
- Structured failure reporting and root-cause classification
- Evaluation and regression testing workflows

### Technical stack

- Python, Twilio API
- Voice AI system under test
- Call scripting and automation
- Structured output generation

### Why this matters

Production voice systems need rigorous testing frameworks. This project shows ability to build automation around complex systems and create effective evaluation workflows.

---

## Event Organizer Platform – Real-time RSVP System

**Type:** Backend, real-time systems, concurrency

### Overview

Built real-time RSVP system for event management. Handled concurrent user interactions with WebSockets and Redis.

### Technical architecture

- **Real-time updates:** WebSockets for live RSVP status
- **Concurrency handling:** Transactional workflows with proper locking
- **State management:** Redis for session data and caching
- **Persistence:** PostgreSQL for event and RSVP data
- **Deployment:** Docker containerization for reliability

### Technical stack

- Node.js, Express, WebSockets
- Redis (caching, pub/sub)
- PostgreSQL (persistence)
- Docker (deployment)

### Why this matters

Real-time systems expose concurrency challenges. Shows experience with WebSocket architecture, Redis patterns, and thinking about race conditions and transactional safety.

---

## Client Onboarding and Billing System – Workflow Automation

**Type:** Backend automation, microservices

### Overview

Built automated onboarding and billing platform. Provisioned customer accounts with validation and billing integration.

### Technical architecture

- **Workflow orchestration:** Microservice-based pipeline
- **Event streaming:** Kafka for asynchronous task coordination
- **Cloud services:** AWS S3 for document storage, Lambda for compute
- **Backend services:** Flask and GraphQL for API
- **Document handling:** Secure document processing and validation

### Technical stack

- Python Flask, GraphQL
- Apache Kafka (event streaming)
- AWS (S3, Lambda)
- Microservices architecture

### Why this matters

Demonstrates event-driven architecture, cloud services integration, and orchestration of complex workflows across services.

---

## Code Time – Developer Tooling & VS Code Extension

**Type:** Full-stack tooling, developer experience

### Overview

Built VS Code extension that records editor events for deterministic replay. Enabled debugging and instruction generation through event history.

### Technical architecture

- **Extension:** TypeScript and React for VS Code UI
- **Event recording:** Captures editor state and changes
- **Backend:** Flask/Node.js for event processing
- **Storage:** PostgreSQL for event history
- **Access control:** Role-based access and permission validation
- **Quality:** CI workflows to reduce regression testing burden

### Technical stack

- TypeScript, React (VS Code extension)
- Node.js / Flask (backend)
- PostgreSQL (persistence)
- AWS (deployment)

### Why this matters

Demonstrates full-stack capability across extension development, backend services, and state consistency challenges. Shows product engineering thinking and CI/CD discipline.

### Stack

[Languages, frameworks, infra — list plainly.]

### Outcome

[Qualitative outcome. If you later add metrics, ensure they are accurate and defensible.]

### Links (optional)

- Repository or demo: [URL or “Not public”]

---

## [Second project name]

**Context:** [Replace]  
**Timeframe:** [Replace]

### Problem

[Replace]

### What I did

- [Replace]

### Stack

[Replace]

### Outcome

[Replace]

### Links (optional)

- [Replace]
