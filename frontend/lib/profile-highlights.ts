export const PROFILE_HIGHLIGHTS = {
  headline: "Early-career backend and applied AI engineer",
  education: {
    school: "University of North Texas",
    degree: "B.S. in Computer Science, AI/ML Concentration",
    graduation: "Expected May 2026",
    gpa: "3.9 / 4.0",
  },
  bestFitRoles: [
    "New Grad Software Engineer",
    "Backend Engineer",
    "AI Engineer",
    "ML Engineer",
  ],
  strongestAreas: [
    "Backend engineering",
    "Production AI systems",
    "RAG systems",
    "Multi-agent systems",
    "Real-time voice AI",
    "Full-stack AI products",
  ],
  coreTools: [
    "Python, TypeScript, Java, SQL",
    "FastAPI, Spring Boot, Next.js",
    "RAG pipelines, LLM integration, vector search",
    "Docker, AWS, CI/CD",
  ],
  projects: [
    {
      title: "PersonaRAG",
      blurb: "Grounded portfolio assistant with retrieval-first answers, citations, and integrated chat plus voice workflows.",
    },
    {
      title: "OpenClaw",
      blurb: "Secure Linux agent runtime with isolation-first controls using namespaces, cgroups, and policy-guarded execution.",
    },
    {
      title: "Enterprise Support Copilot",
      blurb: "Production RAG app for uploaded support docs with grounded responses, source citations, and hybrid retrieval.",
    },
    {
      title: "Customer Feedback Intelligence System",
      blurb: "NLP pipeline over 50k+ feedback records using DistilBERT classification and semantic search for faster triage.",
    },
    {
      title: "Pretty Good AI Voice QA Bot",
      blurb: "Automated voice AI QA platform with Twilio call orchestration, scenario execution, transcripts, and bug reporting.",
    },
  ],
} as const;
