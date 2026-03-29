/**
 * Demo-friendly snapshot for the recruiter sidebar. Replace with your real highlights
 * or load from an API later.
 */
export const PROFILE_HIGHLIGHTS = {
  headline: "Software & AI engineering",
  skills: [
    "Python & TypeScript",
    "Backend APIs & distributed systems",
    "ML systems & model integration",
    "Cloud & observability",
  ],
  experience:
    "Several years building production services and ML-adjacent product features—ownership across design, delivery, and ops-minded practices.",
  projects: [
    { title: "Portfolio RAG assistant", blurb: "Grounded Q&A over structured professional data." },
    { title: "Representative projects", blurb: "Add your shipped work here for this demo." },
  ],
  targetRoles: [
    "Senior / Staff software engineer (backend-leaning)",
    "ML platform or applied ML engineering",
    "Technical lead with hands-on coding",
  ],
} as const;
