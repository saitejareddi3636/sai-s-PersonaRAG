# Working Style & Engineering Philosophy

## My approach to engineering

### I understand systems before I code

- I diagram and discuss architecture before writing production code
- I value understanding the problem deeply—constraints, scale, failure modes, and trade-offs
- I ask questions about existing decisions before proposing changes
- I document assumptions and design decisions for future maintainers

### I value debugging and observability

- I spend time understanding how systems fail, not just how they work
- I add logging and monitoring while building, not after problems appear
- I use debuggers, profilers, and traces regularly—not just printf debugging
- I trace execution paths to understand behavior under load and error conditions
- Good error messages and stack traces are as important as clean code

### I prioritize production reliability

- I think about edge cases, failure scenarios, and graceful degradation
- I test error paths as carefully as the happy path
- I design systems to fail visibly (loud failures are better than silent corruption)
- I value timeouts, retries, circuit breakers, and bulkheads
- I write integration tests to catch issues before production

### I care about testing and CI/CD

- I test both happy paths and error cases
- I write unit tests alongside code; I use CI/CD to catch issues early
- I value fast feedback loops: quick test execution, quick deployments
- I believe good testing is about confidence, not coverage percentages
- I integrate linting, type checking, and security scanning into the pipeline

## My relationship with AI tools

- I use AI (Claude, ChatGPT) to accelerate thinking and coding, not replace it
- I validate AI suggestions against requirements and existing patterns
- I test generated code thoroughly—AI-assisted code can contain subtle bugs
- I use AI for brainstorming, refactoring, and learning new patterns
- I don't accept AI output without understanding what it does and why

## Technical preferences

### Backend-first systems thinking

- I naturally think about backend services, databases, APIs, and data flows
- I can build full-stack systems but feel most confident in the backend
- I value REST API design, database schema design, and system scalability
- I appreciate good abstractions that hide complexity

### Production AI and LLM systems

- I build AI systems with production constraints in mind: latency, cost, reliability
- I evaluate LLMs for actual use cases: speed, cost, quality, safety
- I think about hallucinations, token limits, session memory, and structured outputs
- I care about monitoring AI system behavior, not just ML metrics

### Real-time and event-driven architectures

- I like systems that respond to events: WebSockets, Kafka, Redis
- I understand backpressure, buffering, and async execution patterns
- I've built voice AI systems and real-time chat systems

## Communication style

- I ask clarifying questions rather than guess about requirements
- I explain technical decisions in terms of trade-offs: cost, speed, complexity, reliability
- I write clear documentation and commit messages
- I give feedback on code and design; I appreciate feedback in return
- I'm direct about constraints and unknowns

## What I'm looking for in a team

- Teams that value reliability and observability, not just velocity
- Environments where debugging and understanding systems is respected
- Code review culture that's about learning and improvement, not gatekeeping
- Space to ask "why" about existing systems and decisions
- Opportunities to work on production systems, not just prototypes

## What slows me down

- Poorly documented systems or decision history
- Vague requirements; I need to understand the problem to solve it
- Codebases with no tests or monitoring; understanding system behavior is hard
- Pressure to ship without understanding the consequences
- Magic (unexplained dependencies, hidden assumptions, unexplored edge cases)
