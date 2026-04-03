#!/usr/bin/env python3
"""Emit backend/data/prepared_interview.json from curated Q&A (edit ITEMS below)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Each entry: canonical question text + optional aliases; answer is first-person narrative.
ITEMS: list[dict] = [
    {
        "prompts": [
            "Tell me about yourself",
            "introduce yourself",
            "about yourself",
            "who are you",
        ],
        "answer": (
            "I'm Sai Teja Reddy Shaga, a Computer Science student at the University of North Texas, "
            "graduating in May 2026, and I've been building production-focused AI and software systems "
            "across machine learning, voice AI, RAG, and backend engineering. My strongest experience "
            "comes from Avtar, where I worked on a real-time voice AI platform that combined speech "
            "recognition, LLMs, and text-to-speech, and I focused heavily on latency, reliability, and "
            "deployment quality. Before that, at Niro AI, I built multi-agent workflows with tool calling, "
            "retrieval, structured outputs, and evaluation pipelines. I enjoy working on systems that are "
            "not just technically interesting, but actually usable in production, especially where model "
            "quality, backend engineering, and system reliability all matter together."
        ),
    },
    {
        "prompts": [
            "Walk me through your resume",
            "walk through your resume",
            "resume walkthrough",
            "your resume",
        ],
        "answer": (
            "My background is a mix of software engineering and applied machine learning. I'm currently "
            "completing my Computer Science degree at UNT with an AI/ML concentration. Professionally, my "
            "most relevant experience is as a Machine Learning Engineer at Avtar, where I helped build and "
            "optimize a production voice AI system. That work involved speech pipelines, model fine-tuning, "
            "GPU inference optimization, deployment workflows, and production monitoring.\n"
            "Before that, at Niro AI, I worked on agent systems that used LLM APIs, SQL tools, sandboxed "
            "Python execution, and retrieval-based grounding. That role gave me a strong foundation in "
            "orchestration, reliability, structured generation, and evaluation. Earlier, as a Data Analyst "
            "at UNT, I worked on SQL pipelines, data preprocessing, reporting automation, and dashboards, "
            "which strengthened my data engineering and analytics fundamentals.\n"
            "Alongside that, I've built projects in RAG, feedback intelligence, voice QA automation, and "
            "secure agent runtime systems, which reflect the kind of work I want to keep doing in ML and "
            "backend-heavy roles."
        ),
    },
    {
        "prompts": [
            "Why are you interested in this role",
            "why this role",
            "why this company",
            "why are you applying",
        ],
        "answer": (
            "I'm interested in this role because it sits at the intersection of the areas I've been "
            "building in most deeply: production AI systems, backend engineering, and scalable product "
            "delivery. I've enjoyed working on problems where the challenge is not only training or "
            "integrating a model, but making the entire system reliable, measurable, and useful for real "
            "users. This kind of role is exciting to me because it gives me the opportunity to contribute "
            "both from the ML side and from the software engineering side, especially in designing APIs, "
            "deployment workflows, evaluation systems, and real-time applications."
        ),
    },
    {
        "prompts": [
            "Why are you looking for a new opportunity",
            "why leave",
            "why are you leaving",
            "why look for a new job",
        ],
        "answer": (
            "I'm looking for a role where I can continue building production-grade AI and software systems "
            "at a larger scope and with strong engineering standards. I've had valuable hands-on experience "
            "working on voice AI, RAG systems, and agent workflows, and now I want to bring that experience "
            "into an environment where I can keep growing as an engineer, work on impactful products, and "
            "contribute to systems that operate at scale."
        ),
    },
    {
        "prompts": [
            "What are your strongest technical areas",
            "strongest technical skills",
            "technical strengths",
        ],
        "answer": (
            "My strongest areas are Python-based backend and ML systems, LLM application development, "
            "voice AI pipelines, retrieval-augmented generation, and production deployment. I'm especially "
            "comfortable with FastAPI, PyTorch, SQL, Docker, and cloud-based workflows. I've also spent a "
            "lot of time on model evaluation, inference optimization, tool orchestration, structured outputs, "
            "and system reliability. In practice, I'm strongest when working on end-to-end systems where "
            "models, APIs, infrastructure, and product requirements all need to work together cleanly."
        ),
    },
    {
        "prompts": [
            "What kind of roles are you targeting",
            "what roles are you looking for",
            "what type of role",
        ],
        "answer": (
            "I'm mainly targeting software engineering, machine learning engineering, and applied AI roles "
            "where I can work on backend systems, production ML pipelines, LLM applications, RAG, agent "
            "workflows, or real-time AI products. I'm especially interested in roles where engineering "
            "quality matters just as much as model capability."
        ),
    },
    {
        "prompts": [
            "Can you describe your experience at Avtar",
            "experience at Avtar",
            "what did you do at Avtar",
            "Avtar experience",
        ],
        "answer": (
            "At Avtar, I worked as a Machine Learning Engineer on a production voice AI system. The platform "
            "combined speech recognition, language modeling, and speech synthesis for real-time conversational "
            "interaction. A big part of my work was reducing end-to-end latency, improving model behavior, "
            "and building the infrastructure needed to make the system production-ready.\n"
            "I worked on ASR optimization, model fine-tuning, TTS integration, evaluation harnesses, and "
            "deployment workflows. One major improvement was helping reduce end-to-end response time down "
            "to about 2 to 3 seconds. I also worked on experiments around model quality, persona consistency, "
            "hallucination reduction, and system reliability. Beyond the models themselves, I contributed to "
            "CI/CD, checkpoint versioning, testing, monitoring, and A/B evaluation so the system could be "
            "iterated on safely in production."
        ),
    },
    {
        "prompts": [
            "What was the most impactful project you worked on",
            "most impactful project",
            "biggest impact project",
        ],
        "answer": (
            "One of the most impactful projects I worked on was the production voice AI system at Avtar. It "
            "was impactful because it required solving problems across the full stack of AI delivery: speech "
            "recognition, LLM reasoning, TTS synthesis, latency reduction, evaluation, and deployment. It "
            "wasn't just a model experiment. It had real-time constraints and user experience implications, so "
            "every design choice affected quality and responsiveness. Getting that system down to around 2 to 3 "
            "seconds end-to-end while improving reliability taught me a lot about balancing model quality with "
            "engineering practicality."
        ),
    },
    {
        "prompts": [
            "Tell me about a time you improved performance or latency",
            "improved performance or latency",
            "latency optimization",
            "performance improvement story",
        ],
        "answer": (
            "At Avtar, I worked on optimizing the speech pipeline for a real-time voice AI application. The "
            "main issue was that the end-to-end interaction was too slow for a natural conversational "
            "experience. I improved the ASR portion by moving toward a FasterWhisper and CTranslate2-based "
            "setup and also looked at the broader inference pipeline, batching, and integration points across "
            "ASR, LLM, and TTS. That work helped reduce total response time to around 2 to 3 seconds, which "
            "made the interaction much more usable in production. What I learned from that project is that "
            "latency usually isn't caused by one isolated component. You have to profile the whole system and "
            "optimize the slowest handoffs, not just the model."
        ),
    },
    {
        "prompts": [
            "Tell me about your experience with LLMs",
            "experience with LLMs",
            "large language models",
            "LLM experience",
        ],
        "answer": (
            "My LLM experience spans both API-based systems and model fine-tuning. At Niro AI, I built agent "
            "workflows using OpenAI and Anthropic models, where the focus was tool calling, multi-turn context, "
            "retrieval grounding, structured outputs, and workflow reliability. At Avtar, I worked closer to "
            "model adaptation and multimodal systems, including fine-tuning and optimizing models for "
            "conversational use cases. Across both, I've worked on hallucination mitigation, evaluation, "
            "prompt design, structured generation, and system integration. I think about LLMs less as isolated "
            "models and more as components inside reliable end-to-end systems."
        ),
    },
    {
        "prompts": [
            "Do you have experience with RAG",
            "experience with RAG",
            "retrieval augmented generation",
        ],
        "answer": (
            "Yes. I've worked on RAG both professionally and in projects. At Niro AI, I built retrieval-enabled "
            "agent workflows that used grounding, session memory, and structured prompting to keep responses "
            "accurate and context-aware. In my Enterprise Support Copilot project, I built a full-stack RAG "
            "application where users could upload support documents and receive cited answers. That included "
            "document ingestion, chunking, embeddings, vector search, hybrid retrieval, and optional "
            "reranking. My focus in RAG systems is usually on answer quality, grounding, and how retrieval "
            "fits into a usable product workflow."
        ),
    },
    {
        "prompts": [
            "Tell me about your multi-agent or agentic AI experience",
            "multi-agent experience",
            "agentic AI",
            "agents and tools",
        ],
        "answer": (
            "At Niro AI, I worked on a multi-agent orchestration platform that integrated LLM APIs with SQL "
            "tools, Python execution, and external APIs to automate business workflows. My work included tool "
            "orchestration, schema validation, retry logic, conversation state handling, safeguards for "
            "execution, and evaluation pipelines. The key challenge was making the agents reliable enough for "
            "production-style usage, so I spent a lot of time on structured outputs, reducing failure cases, "
            "and making sure actions were grounded and verifiable."
        ),
    },
    {
        "prompts": [
            "Tell me about a time you handled ambiguity",
            "handled ambiguity",
            "dealing with ambiguity",
        ],
        "answer": (
            "A lot of the AI system work I've done came with ambiguity, especially around what \"good\" "
            "behavior should look like in production. One example was working on conversational AI workflows "
            "where the product expectation was clear at a high level, but the technical path was not. In those "
            "cases, I usually break the problem down into measurable parts first, such as latency, response "
            "quality, failure modes, and observability. Then I build small experiments, define evaluation "
            "criteria, and iterate from evidence rather than assumptions. That approach has helped me stay "
            "effective even when requirements are evolving."
        ),
    },
    {
        "prompts": [
            "Tell me about a challenge you faced and how you solved it",
            "challenge you faced",
            "difficult problem you solved",
        ],
        "answer": (
            "One challenge I faced was balancing quality and latency in a real-time voice AI system. Improving "
            "model output quality often made the system slower, while aggressive optimization could hurt the "
            "experience. To solve that, I treated it as a system problem instead of just a model problem. I "
            "profiled each component, identified the biggest bottlenecks, improved the ASR stack, tuned "
            "inference behavior, and put better evaluation in place so we could compare tradeoffs objectively. "
            "That helped us improve speed while still maintaining conversational quality."
        ),
    },
    {
        "prompts": [
            "Tell me about a time you worked cross-functionally",
            "cross-functional collaboration",
            "worked with product and engineering",
        ],
        "answer": (
            "At Avtar, the work naturally required collaboration across engineering, product, and model "
            "development because the system touched infrastructure, user experience, and model behavior at "
            "the same time. I worked with others on architecture discussions, deployment decisions, model "
            "experiments, and iteration planning. I've learned that in AI product work, communication is "
            "important because not everyone is looking at the same metrics. Sometimes engineering is focused "
            "on reliability, product is focused on user experience, and ML is focused on model quality, so "
            "part of the job is aligning those perspectives into a practical implementation plan."
        ),
    },
    {
        "prompts": [
            "What are you most proud of",
            "most proud of",
            "proudest accomplishment",
        ],
        "answer": (
            "I'm most proud of having worked on systems that were actually used in realistic production "
            "contexts, especially the voice AI work at Avtar. I value projects where I can point to a real "
            "system improvement like lower latency, better reliability, stronger evaluation, or smoother "
            "deployment. I'm also proud that my experience is not limited to one layer. I've worked across "
            "model tuning, backend APIs, retrieval pipelines, orchestration logic, and deployment "
            "infrastructure, and that has helped me become a more practical engineer."
        ),
    },
    {
        "prompts": [
            "What is your experience with model evaluation",
            "model evaluation experience",
            "evaluating models",
        ],
        "answer": (
            "I've worked on evaluation in several ways depending on the system. For voice AI, that included "
            "latency profiling, quality comparisons, and looking at improvements in naturalness and reliability. "
            "For agent systems, I built task-based evaluation frameworks, automated scoring, and "
            "prompt-variant benchmarking. For classification projects, I used model metrics like F1 score to "
            "compare performance. In general, I believe evaluation should reflect how the system will actually "
            "be used, not just offline model scores."
        ),
    },
    {
        "prompts": [
            "What is your experience with production deployment",
            "production deployment experience",
            "deploying to production",
        ],
        "answer": (
            "I've worked on deployment through Dockerized services, CI/CD workflows, checkpoint versioning, "
            "cloud-based infrastructure, monitoring, and A/B evaluation pipelines. At Avtar, this was an "
            "important part of making the voice AI system reliable in production. In my project work, I've "
            "also built API backends, vector search systems, and full-stack apps that required structured "
            "ingestion, model integration, and reproducible deployment flows. I'm comfortable thinking about "
            "deployment as part of the engineering lifecycle rather than something separate from model "
            "development."
        ),
    },
    {
        "prompts": [
            "Why should we hire you",
            "why hire you",
            "what do you bring",
        ],
        "answer": (
            "You should hire me because I bring a combination of applied ML experience and strong software "
            "engineering execution. I've worked on real systems involving LLMs, voice AI, retrieval, backend "
            "APIs, and production deployment, and I care a lot about reliability, latency, and measurable impact. "
            "I can contribute across the lifecycle, from prototyping and experimentation to building APIs, "
            "evaluation systems, and production workflows. I also learn quickly, communicate well, and enjoy "
            "working on technically challenging systems that have real user impact."
        ),
    },
    {
        "prompts": [
            "What are you looking for in your next team",
            "ideal team",
            "culture you want",
        ],
        "answer": (
            "I'm looking for a team that values strong engineering fundamentals, practical problem solving, and "
            "thoughtful product building. I do my best work in environments where people care about code "
            "quality, system reliability, and clear collaboration, especially on products that combine backend "
            "systems with AI or machine learning."
        ),
    },
    {
        "prompts": [
            "Are you more interested in software engineering or machine learning engineering",
            "software engineering or machine learning",
            "SWE or MLE",
        ],
        "answer": (
            "I'm comfortable in both, but my best fit is probably where the two overlap. I enjoy machine "
            "learning engineering because it combines model understanding with real software delivery. A lot "
            "of the work I've done has required backend APIs, data pipelines, evaluation systems, deployment, "
            "and infrastructure alongside model development. So I'm especially interested in roles where I can "
            "build production AI systems rather than work only on isolated research or only on general "
            "application development."
        ),
    },
    {
        "prompts": [
            "Tell me about a project outside of work",
            "project outside of work",
            "side project",
            "personal project",
        ],
        "answer": (
            "One project I'm proud of is Enterprise Support Copilot, which is a full-stack RAG application "
            "built with FastAPI, Next.js, PostgreSQL, and pgvector. Users can upload support documents and get "
            "cited answers grounded in those documents. I implemented ingestion, chunking, embeddings, hybrid "
            "retrieval, and multi-model support. I liked this project because it reflects the kind of end-to-end "
            "product engineering I enjoy, where retrieval quality, backend design, and user experience all "
            "matter together."
        ),
    },
    {
        "prompts": [
            "Tell me about a project that shows your backend skills",
            "project that shows backend skills",
            "backend project example",
        ],
        "answer": (
            "A good example is my Open Claw project, which is a secure runtime for AI agents. I built a Go "
            "control plane and a Rust sandbox runtime that used Linux isolation primitives like namespaces, "
            "chroot, and cgroups to enforce safety. That project required backend systems thinking, API design, "
            "policy enforcement, audit logging, and runtime control. It was a strong backend and systems project "
            "because the focus was on execution safety, control, and traceability rather than just model "
            "interaction."
        ),
    },
    {
        "prompts": [
            "What is your experience with data and analytics",
            "data and analytics experience",
            "data analyst experience",
        ],
        "answer": (
            "At UNT, I worked as a Data Analyst where I built SQL-based preprocessing and validation pipelines "
            "across large datasets, including more than 500,000 records. I also automated reporting workflows and "
            "Power BI dashboards with a focus on data integrity and reproducibility. That experience helped me "
            "build a strong data foundation, which has been useful later in ML engineering work where data "
            "quality and preprocessing directly affect model outcomes."
        ),
    },
    {
        "prompts": [
            "Are you comfortable learning new technologies quickly",
            "learn new technologies quickly",
            "pick up new tech",
        ],
        "answer": (
            "Yes. Most of my experience has involved moving across different parts of the stack depending on "
            "what the problem required. For example, I've worked across speech systems, LLM APIs, fine-tuning, "
            "retrieval pipelines, backend services, vector databases, Docker-based deployment, and cloud "
            "tooling. I'm comfortable ramping up quickly because I focus on first understanding the system "
            "goals, then learning the parts of the stack that matter most for delivering results."
        ),
    },
    {
        "prompts": [
            "What are your salary expectations",
            "salary expectations",
            "compensation expectations",
        ],
        "answer": (
            "I'm open and flexible depending on the role, team, location, and overall opportunity. My main "
            "focus is finding a strong fit where I can contribute meaningfully and continue growing in "
            "production AI and software engineering."
        ),
    },
    {
        "prompts": [
            "Are you open to relocation or remote work",
            "relocation or remote",
            "open to remote",
            "willing to relocate",
        ],
        "answer": (
            "Yes, I'm based in the Dallas area and I'm open to remote roles as well as relocation within the US "
            "for the right opportunity."
        ),
    },
    {
        "prompts": [
            "When can you start",
            "start date",
            "availability to start",
        ],
        "answer": (
            "I can align based on the team's timeline. Since I'm graduating in May 2026, I'm actively looking "
            "at opportunities around that transition and can discuss availability based on the role."
        ),
    },
]


def main() -> None:
    out = ROOT / "data" / "prepared_interview.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ITEMS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(ITEMS)} entries to {out}")


if __name__ == "__main__":
    main()
