# Recruiter FAQ

This document provides grounded answers to common recruiter questions. Each answer references specific projects, roles, or skills files.

## Tell me about yourself

I'm a CS graduate from University of North Texas (graduating May 2026, 3.9 GPA) with hands-on experience in backend systems, production AI, and full-stack development. I've built voice AI systems, RAG pipelines, AI agents, microservices, and full-stack AI products.

My strongest areas are:
- **Backend engineering:** Spring Boot, FastAPI, REST APIs, databases, microservices
- **Production AI:** LLM integration, RAG systems, AI agents, structured generation
- **Full-stack development:** I can go from backend infrastructure to frontend UI and ML inference
- **Reliability:** I care deeply about testing, debugging, observability, and production readiness

I'm targeting new grad SWE, backend, AI engineer, and ML engineer roles. I'm strongest in positions where engineering discipline and AI systems both matter.

## What's your strongest technical area?

Backend systems combined with AI/LLM integration.

**Backend specifics:** REST API design, database schema design, microservices architecture, testing, CI/CD, production debugging, real-time systems (WebSockets, Kafka, Redis).

**AI/LLM specifics:** LLM API integration (OpenAI, Anthropic), RAG pipelines, multi-agent orchestration, fine-tuning, structured generation, session memory management, production AI monitoring.

**Why this combination matters:** Building production AI systems requires both solid backend engineering and understanding of LLM systems. I've done both on real projects.

See: experience.md (Niro AI, Avtar roles), projects.md (Enterprise Support Copilot, voice AI systems)

## Are you more of a software engineer or ML engineer?

I'm fundamentally a software engineer with strong ML and LLM systems experience.

My background is solid CS fundamentals (algorithms, data structures, systems), production software engineering (testing, CI/CD, reliability), and hands-on ML/AI (PyTorch, LLMs, RAG, agents). I'm particularly strong at the intersection: building production AI services with proper engineering practices.

**For SWE roles:** I bring strong fundamentals, production discipline, and ability to own systems end-to-end.

**For ML/AI roles:** I bring software engineering practices to AI development (testing, versioning, monitoring) plus hands-on LLM and model work.

**For full-stack AI roles:** I can own the complete flow: backend infrastructure, ML pipeline, model integration, and frontend.

See: education.md (CS curriculum), experience.md (roles spanning both), projects.md (full-stack projects)

## Tell me about your production experience

**Avtar (Voice AI Systems):**
- Built production voice AI pipeline
- Real-time audio streaming and inference
- Model deployment and optimization
- Monitoring and incident response
- Worked with real users and production constraints

**Niro AI (Multi-Agent Orchestration):**
- Built agent orchestration layer handling 50+ agents
- Implemented structured outputs and function calling
- Session memory and multi-turn context management
- RAG integration for knowledge grounding
- Production scaling and reliability patterns

**JPMorgan (Banking Systems):**
- Enterprise microservices (Spring Boot)
- High-volume transaction processing
- Kafka event streaming
- Banking domain compliance and reliability

**Intuit (Backend APIs):**
- REST API design and implementation
- Database optimization and indexing
- Testing, CI/CD, production debugging
- Incident response and reliability

**UNT:**
- Taught production concepts to students
- Led office hours on systems thinking and debugging

See: experience.md for detailed role descriptions

## How comfortable are you with Java and Spring Boot?

Very comfortable. Spring Boot is one of my primary backend frameworks.

**JPMorgan role:** 
- Built microservices using Spring Boot
- Database design and optimization
- Kafka integration for event streaming
- Testing and CI/CD

**Current use:**
- Used for real-time applications and microservice architecture
- Good understanding of Spring concepts: dependency injection, lifecycle, configurations
- Experience with testing frameworks (JUnit, Mockito) and CI/CD integration

I can jump into a Spring Boot codebase and be productive quickly.

See: experience.md (JPMorgan role), projects.md (project technical stacks)

## What's your RAG and agent experience?

**RAG (Retrieval-Augmented Generation):**
- Built complete RAG pipeline: chunking, embedding, retrieval, answer generation
- Worked with both TF-IDF and embedding-based retrieval
- Implemented semantic search with multiple embedding models (nomic-embed-text, OpenAI embeddings)
- Built production RAG systems with hybrid retrieval (semantic + keyword fallback)
- Integrated RAG with LLM chat for grounded, source-cited responses
- Optimized retrieval quality: proper chunking, embedding selection, hybrid search scoring
- Production RAG deployment: monitoring quality, handling edge cases, graceful degradation

**AI Agents:**
- Built multi-agent orchestration from scratch: agent loops, tool calling, execution safeguards
- Implemented tool calling with function signatures, error handling, and execution sandboxes (SQL, Python)
- Session memory and multi-turn context: managing token limits, history pruning, context injection
- Structured output generation: JSON schema validation, retry logic, fallback strategies
- Production agent patterns: hallucination mitigation, safety guardrails, confidence scoring
- Integration with multiple LLM providers (OpenAI, Anthropic) and self-hosted models (Ollama)

See: experience.md (Niro AI and Avtar roles), projects.md (RAG + agent projects)
- Integrated with OpenAI APIs
- Tested retrieval quality and relevance
- Example: Enterprise Support Copilot (retrieve from company docs, generate support answers)
- Example: This AI Portfolio Agent (you're talking to it now)

**AI Agents:**
- Multi-agent orchestration system (Niro AI)
- Tool calling and function execution
- Structured outputs for reliable parsing
- Session memory for multi-turn context
- Agent routing and fallback patterns
- Evaluation frameworks for agent behavior

**LLM Integration:**
- OpenAI API (gpt-4o-mini, gpt-4, gpt-3.5-turbo)
- Anthropic Claude API
- Structured generation with JSON schemas
- Temperature and parameter tuning
- Token counting and cost optimization
- Streaming responses

See: experience.md (Niro AI), projects.md (Enterprise Support Copilot, voice AI agents)

## What's your project portfolio like?

I have 7 completed projects spanning systems, AI, and full-stack development:

1. **Open Claw** – Agent runtime framework for building/running agents
2. **Enterprise Support Copilot** – RAG system for support teams (retrieval + LLM)
3. **Feedback Intelligence** – NLP pipeline processing customer feedback
4. **Voice QA** – Real-time voice AI system for quality assurance
5. **RSVP Platform** – Full-stack event management application
6. **Onboarding/Billing System** – Backend APIs for user management and billing
7. **Developer Tooling (Code Time)** – VS Code extension and backend for developer metrics

Projects demonstrate:
- Backend infrastructure (APIs, databases, microservices)
- Full-stack capability (frontend, backend, infrastructure)
- AI/ML systems (NLP, voice, agents, RAG)
- Production thinking (testing, reliability, monitoring)
- Diverse tech stacks (Python, Java, JavaScript/TypeScript, React, Spring Boot, FastAPI)

See: projects.md (detailed breakdown of each)

## What are your programming languages?

**Strong (production use):**
- Python (backend, ML, scripting)
- Java (Spring Boot microservices)
- JavaScript/TypeScript (frontend, backend with Node.js)
- SQL (database design, queries, optimization)

**Comfortable:**
- C++ (systems programming, algorithms)
- Bash (scripting, CI/CD)

**Applied in:**
- Python: FastAPI, PyTorch, Hugging Face, data processing
- Java: Spring Boot, microservices, Kafka
- JavaScript/TypeScript: React frontend, Express/Node.js backend, Next.js
- SQL: PostgreSQL, MySQL, schema design, performance optimization

See: skills_shared.md (comprehensive language and tool list)

## How do you approach learning new technologies?

1. **Understand why it exists** – what problem does it solve?
2. **Build something real** – not tutorials, actual projects
3. **Debug failures** – understand how it breaks under stress
4. **Document patterns** – write about what you learned
5. **Stay pragmatic** – choose tools based on fit, not hype

I'm comfortable with:
- New frameworks (learn by building real projects)
- New languages (if they solve a real problem)
- New AI/ML tools (LLMs, embedding models, inference frameworks)
- New infrastructure (Docker, Kubernetes, serverless)

Recent learning:
- FastAPI (built RAG backends with it)
- Next.js (frontend for this AI portfolio agent)
- Embedding models and vector search (for RAG systems)
- LLM APIs and structured generation (OpenAI, Anthropic)

## What are you looking for in a role?

**Ideal characteristics:**
- **Production focus:** Real systems with real users, not just prototypes
- **Engineering discipline:** Testing, observability, reliability matter
- **Interesting problems:** Backend infrastructure, AI systems, full-stack challenges
- **Learning opportunities:** Strong mentors, code review culture, space to grow
- **Autonomy:** Trust to understand problems and propose solutions

**Seniority level:** Entry-level / new grad positions. Looking for roles where I can own systems and learn from experienced team members.

**Role types:** New grad SWE, Backend Engineer, AI Engineer, ML Engineer, full-stack AI roles.

**Location:** Open to remote, on-site, or hybrid. US-based preferred.

See: target_roles.md (detailed role positioning and positioning strategy)

## How do you handle ambiguity and unclear requirements?

I ask questions first.

**My approach:**
1. Clarify the problem, not the solution
2. Understand constraints (performance, cost, reliability, timeline)
3. Identify edge cases and failure modes
4. Propose solutions with trade-offs, not prescriptions
5. Get alignment before building

I don't assume I understand the problem. Clear requirements prevent rework and better products.

This is why I value teams with good documentation and communication. See: working_style.md for details on my engineering approach.

## What's your debugging philosophy?

Debugging is systematic detective work, not random guessing.

**My process:**
1. **Reproduce** – reliably trigger the bug, understand the exact conditions
2. **Trace** – follow execution: logs, debugger, profiler, stack traces
3. **Understand** – identify the root cause, not just symptoms
4. **Fix carefully** – address the root cause; verify the fix doesn't break something else
5. **Monitor** – add logging/alerts to catch similar issues in future

**Tools I use:**
- Debuggers (breakpoints, stepping, inspection)
- Profilers (CPU, memory, flame graphs)
- Log aggregation and tracing
- Error tracking (stack traces, reproduction info)
- Monitoring and alerting

I value systems built with observability in mind: good logs, metrics, and traces make debugging possible.

See: working_style.md (emphasis on debugging and observability)

## Why PersonaRAG? What motivated building this project?

PersonaRAG is a hands-on demonstration of full-stack AI engineering:

**Why it matters:**
- Shows practical RAG implementation (retrieval + LLM generation)
- Demonstrates full-stack thinking (backend API, frontend UI, data pipeline)
- Serves a real purpose (helping recruiters understand my actual capabilities)
- Real production constraints (cost, latency, reliability)

**Technical goals:**
- Build production-quality RAG pipeline
- Integrate with real LLM APIs
- Add optional voice synthesis for accessibility
- Clean architecture that supports extensibility
- Docker-based development and deployment

**What it demonstrates:**
- Backend API design (FastAPI)
- RAG fundamentals (chunking, retrieval, generation)
- Session memory and conversation context
- Frontend integration (Next.js chat UI)
- Service abstraction and graceful degradation
- Production practices (testing, Docker, error handling)

The system is designed so that when you ask me a question, it retrieves relevant information from this knowledge base, grounds the LLM response in that context, and optionally synthesizes audio. It's both a demo and a tool.

## Any other questions about your background?

Check out these files for more details:
- **education.md** – Full academic background and coursework
- **experience.md** – Detailed descriptions of each role and company
- **projects.md** – Complete project portfolio with technical breakdowns
- **skills_shared.md** – Languages, tools, databases, cloud platforms
- **skills_swe.md** – Backend frameworks, testing, CI/CD, reliability
- **skills_ml.md** – Deep learning, LLMs, RAG, agents, inference
- **working_style.md** – Engineering philosophy, communication style, what I value
- **target_roles.md** – Detailed role targeting and positioning strategy

Or ask me directly—I'm here to help you understand if I'd be a good fit for your team.
