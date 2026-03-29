/**
 * Curated prompts by audience. Add or reorder strings here—no app logic changes required.
 */
export type QuestionPackId = "recruiter" | "hiring_manager" | "technical_interviewer";

export type QuestionPack = {
  id: QuestionPackId;
  label: string;
  subtitle: string;
  questions: readonly string[];
};

export const QUESTION_PACKS: readonly QuestionPack[] = [
  {
    id: "recruiter",
    label: "Recruiter",
    subtitle: "Screening, logistics, and role fit",
    questions: [
      "What roles is he targeting?",
      "What is his availability or notice period situation?",
      "How would you summarize his background in two sentences for a hiring manager?",
      "What type of company stage or domain is he most interested in?",
    ],
  },
  {
    id: "hiring_manager",
    label: "Hiring manager",
    subtitle: "Ownership, impact, and team fit",
    questions: [
      "Tell me about his strongest project.",
      "Is he stronger in SWE or ML, and how does that show up in his work?",
      "Where has he owned end-to-end delivery versus contributing as part of a team?",
      "How does he communicate tradeoffs and priorities to stakeholders?",
    ],
  },
  {
    id: "technical_interviewer",
    label: "Technical interviewer",
    subtitle: "Depth, systems, and how he builds",
    questions: [
      "What backend experience does he have?",
      "What kind of production AI systems has he built?",
      "How does he approach reliability and debugging?",
      "How does he think about testing, observability, or production incidents?",
      "Walk through a technical decision he made on a recent project.",
    ],
  },
] as const;

export const QUESTION_PACK_ORDER: readonly QuestionPackId[] = [
  "recruiter",
  "hiring_manager",
  "technical_interviewer",
];
