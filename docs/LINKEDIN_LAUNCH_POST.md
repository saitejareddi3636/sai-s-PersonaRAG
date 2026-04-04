# LinkedIn launch — PersonaRAG

Use this when you announce your AI portfolio assistant. Replace `YOUR_PORTFOLIO_URL` with your live site (e.g. Vercel) and optionally add your GitHub repo link.

---

## Simple launch post (copy-paste)

**Facts this version highlights:** no commercial LLM APIs on the default stack • **Faster-Whisper** (`tiny`) for STT • **Piper** for TTS • **Ollama** + **Qwen 2.5 3B** for chat • **Oracle Cloud** VM for API + models • **Vercel** for the Next.js frontend.

---

I’m launching **PersonaRAG** — my **RAG portfolio assistant** for recruiters and hiring teams.

**No OpenAI-style APIs on the path I ship:** inference runs on **my own stack**. Chat uses **Ollama** with **Qwen 2.5 (3B)**. Voice uses **Faster-Whisper** (**Whisper `tiny`**, English) for **STT** and **Piper** for **TTS** — all local in the backend container, no cloud speech APIs required.

**How it’s deployed:** **Next.js on Vercel** (fast global UI + HTTPS, deploy from Git) and **FastAPI + Ollama + Docker on Oracle Cloud** so models and data stay on infra I control — better for cost, privacy, and learning how production AI systems are actually run.

Ask it real questions; answers are **grounded** in my materials with **sources**.

Try it: **YOUR_PORTFOLIO_URL**  
Repo: **YOUR_GITHUB_REPO_URL**

#RAG #LLM #MachineLearning #SoftwareEngineering #OracleCloud #Vercel #NewGrad #Hiring #Portfolio #OpenSource

---

## Option A — Short (good for feed, ~1,200 characters)

**Copy from below the line**

---

I built **PersonaRAG** — an AI portfolio assistant that answers recruiter-style questions **from my own materials**, not generic LLM fluff.

**Why I shipped it**
- **No commercial LLM APIs** on my default stack: **Ollama** + **Qwen 2.5 3B** for chat; **Faster-Whisper** (**Whisper `tiny`**) for **STT**; **Piper** for **TTS** — self-hosted, not OpenAI/Anthropic calls.
- **Retrieval-first:** answers are grounded in what I’ve written (projects, experience, skills) with **source visibility**.
- **Deploy split:** **Vercel** for the **Next.js** frontend; **Oracle Cloud** VM + **Docker** for the API and models — CDN + HTTPS on the UI, full control on inference.
- **Production-minded:** FastAPI, compose, health checks — the kind of system work I want in **backend / ML engineering** roles.

If you’re **hiring new grads** in **software engineering, backend, or applied AI**, this is how I want you to evaluate me: ask technical questions, drill into tradeoffs, and see answers tied to real work — not a static PDF.

Try it: **YOUR_PORTFOLIO_URL**

#AI #MachineLearning #RAG #LLM #SoftwareEngineering #OpenSource #NewGrad #Hiring #Portfolio

---

## Option B — Story arc (longer, good for “see more”)

**Copy from below the line**

---

Recruiters and hiring managers rarely get signal from a one-page resume alone. I wanted something better: a **grounded**, **inspectable** assistant that represents how I actually work.

Today I’m sharing **PersonaRAG** — my **RAG-powered portfolio agent**.

**What it does**
- Pulls from **my curated knowledge base** (experience, projects, FAQs) and answers with **retrieval-backed context** — so responses stay tied to **my** story.
- Uses **local / self-hosted inference** for the chat model (Ollama-compatible stack), because I care about **where models run** and how systems are operated in production.
- Supports **voice**: **STT → grounded answer → TTS**, so you can have a **natural screening-style conversation**, not only chat.
- Built like a real product: **API**, **session memory**, **Docker** deployment — not a notebook demo.

**Who it’s for**
- **Recruiters & engineers hiring** for roles where **reliability, grounding, and system design** matter — especially **backend**, **ML engineering**, and **applied AI**.

**Try the assistant & ask hard questions:** **YOUR_PORTFOLIO_URL**  
Code: **YOUR_GITHUB_REPO_URL** *(optional)*

If this resonates with how your team builds AI products, I’d love to connect. I’m **graduating May 2026** and targeting roles where **shipping production systems** meets **applied ML**.

#PersonaRAG #RAG #LLM #MLOps #SoftwareEngineering #AI #Hiring #NewGrad #Portfolio #OpenSource

---

## Option C — Recruiter-focused (very direct)

**Copy from below the line**

---

**To recruiters and hiring teams:**  
Stop guessing what’s real on a resume. I built an AI assistant that only answers from **my documented experience** — **RAG** over my portfolio, **citations**, **local model** serving, **voice** optional.

**PersonaRAG** = ask behavioral & technical questions, get **grounded** answers + see **what sources** were used.

Live demo: **YOUR_PORTFOLIO_URL**

I’m a **CS grad (May 2026)** targeting **SWE / backend / ML engineering**. If you care about **production AI** and **honest evaluation**, try the demo before our first call.

#Hiring #Recruiting #AI #RAG #SoftwareEngineer #NewGrad

---

## Before you post — checklist

- [ ] Replace **YOUR_PORTFOLIO_URL** (and GitHub link if you use Option B).
- [ ] Test the live site once in an incognito window (chat + optional voice).
- [ ] Add a **headshot or project screenshot** — LinkedIn rewards posts with media.
- [ ] Pin a comment with your **email** or **Calendly** if you want inbound.
- [ ] Post **Tuesday–Thursday, morning** in your timezone for visibility (optional).

---

## Suggested first comment (pin or reply to your own post)

“Happy to go deeper on architecture: retrieval (TF-IDF vs embeddings), latency tradeoffs on CPU, and why I chose grounded answers over generic LLM replies. Drop questions below.”

---

*Internal doc — not part of the RAG corpus unless you ingest it.*
