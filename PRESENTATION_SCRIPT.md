# Drug Repurposing Intelligence Platform - Presentation Script

## Introduction (30 seconds)
**SHOW:** Landing page of the application

**SAY:**
"Hi everyone! Today I'm presenting our Autonomous Drug Repurposing Intelligence Platform. This is an AI-powered research assistant that helps pharmaceutical researchers discover new therapeutic uses for existing drugs. Instead of spending weeks manually searching through clinical trials, patents, and regulatory documents, our system does it in minutes using a multi-agent architecture."

---

## Architecture Overview (45 seconds)
**SHOW:** Open `ProjectOverview.md` or architecture diagram

**SAY:**
"The system is built on LangGraph with four specialized AI agents:
- A Clinical Agent that searches ClinicalTrials.gov for trial data
- A Patent Agent that analyzes patent landscapes using EPO and Open Targets
- A Market Agent that pulls FDA drug label information
- And a Regulatory Agent that checks adverse events and regulatory status

All of this is orchestrated through a dynamic planning system that breaks down research queries into parallel tasks, executes them, and synthesizes the findings into a comprehensive report."

---

## Demo: Starting a Search (30 seconds)
**SHOW:** Frontend search form

**SAY:**
"Let me show you how it works. The interface is simple - you just enter a molecule name. For this demo, I'll use Metformin, a common diabetes drug."

**DO:** Type "Metformin" in the search box

**SAY:**
"When I click 'Start Research', the system kicks off the entire pipeline. Now, because this process involves calling multiple external APIs, embedding documents, and running LLM analysis, it typically takes 2-3 minutes. So for this presentation, I've already run this search earlier."

---

## Demo: Real-Time Progress (45 seconds)
**SHOW:** Pre-recorded or screenshot of progress viewer with SSE updates

**SAY:**
"During a live search, you'd see real-time progress updates here using Server-Sent Events. The system shows you:
- When it resolves the molecule structure from ChEMBL
- As each agent starts and completes its research
- When documents are being chunked and embedded into our vector database
- And finally when the synthesis engine combines everything

This transparency is crucial for researchers who need to trust the process."

---

## Demo: Showing Cached Results (1 minute)
**SHOW:** Enter "Metformin" again in the search form

**SAY:**
"Now here's where our caching system comes in. Let me search for Metformin again."

**DO:** Submit the search

**SHOW:** Results appear almost instantly

**SAY:**
"Notice how fast that was? Instead of 2-3 minutes, we got results in under a second. That's because we implement intelligent caching at multiple levels:

First, we cache the final reports in Redis with a 24-hour TTL. If someone searches for the same molecule within a day, we serve the cached report instantly.

Second, we cache the raw research data from each agent - clinical trials, patents, market data - so if we need to regenerate a report with different synthesis parameters, we don't have to re-fetch everything from external APIs.

And third, we store all document embeddings in Qdrant, our vector database, so we can do semantic search across previously analyzed documents without re-embedding them."

---

## Demo: Exploring the Report (1 minute 30 seconds)
**SHOW:** Scroll through the generated report

**SAY:**
"The report is structured into clear sections. Let's walk through it:

**Clinical Evidence:** Here we see Metformin's established use for Type 2 Diabetes, but also emerging research in PCOS, cancer prevention, and anti-aging. Each finding is backed by actual clinical trial data.

**Patent Landscape:** The system found patents covering various formulations and new therapeutic applications. This helps researchers understand the IP landscape before investing in new research.

**Market Analysis:** Current FDA-approved indications, available formulations, and market positioning. This gives context on commercial viability.

**Regulatory Status:** Any safety signals, adverse events, or regulatory actions. Critical for risk assessment.

**Repurposing Opportunities:** This is the key section - the AI synthesizes all the data to identify promising new therapeutic uses. For Metformin, it highlights cardiovascular protection and neuroprotection as high-potential areas based on the evidence."

**SHOW:** Scroll to citations section

**SAY:**
"And everything is cited. Every claim links back to the source - whether it's a clinical trial ID, a patent number, or an FDA document. This maintains scientific rigor."

---

## Technical Highlights (45 seconds)
**SHOW:** Briefly show code or architecture diagram

**SAY:**
"On the technical side, we're using:
- LangGraph for orchestration with dynamic replanning
- Gemini 2.5 Flash and Pro models for fast, accurate analysis
- Qdrant for vector search with 3072-dimensional embeddings
- Supabase for session management and report storage
- And a FastAPI backend with Next.js frontend

The system is designed to be modular - we can easily add new agents for different data sources or swap out LLM providers."

---

## Conflict Detection & Quality (30 seconds)
**SHOW:** Mention or show `backend/memory/conflict_detector.py`

**SAY:**
"One unique feature is our conflict detection system. When different agents return contradictory information - say one source says a drug is safe and another reports adverse events - the system flags these conflicts and asks the LLM to reconcile them with proper context. This prevents misleading conclusions."

---

## Closing (30 seconds)
**SHOW:** Return to landing page or summary slide

**SAY:**
"So in summary, we've built an end-to-end research automation platform that:
- Reduces research time from weeks to minutes
- Provides transparent, cited, and trustworthy results
- Scales efficiently with intelligent caching
- And maintains scientific rigor through conflict detection and source attribution

The code is production-ready with comprehensive error handling, graceful degradation when APIs fail, and a clean architecture that's easy to extend. Thank you! Happy to take questions."

---

## Backup Q&A Responses

**Q: What if an external API is down?**
**A:** "Great question. We implement graceful degradation - if ClinicalTrials.gov is down, the clinical agent falls back to LLM-based analysis using cached knowledge, and we flag in the report that live data wasn't available. The system never crashes."

**Q: How do you handle API rate limits?**
**A:** "We implement exponential backoff and respect rate limits. Plus, our caching strategy means we rarely hit the same API twice for the same molecule within 24 hours."

**Q: Can you add more data sources?**
**A:** "Absolutely. The agent architecture is modular. You'd just create a new agent class, implement the research method, and register it with the orchestrator. We designed it for extensibility."

**Q: How accurate are the repurposing suggestions?**
**A:** "The suggestions are based on real clinical trial data, patent filings, and published research. We're not generating speculative ideas - we're synthesizing existing evidence that researchers might have missed. That said, all suggestions should be validated through proper research channels."

**Q: What about data privacy?**
**A:** "All searches are stored with session IDs, not user identities. We don't collect personal information. The reports are cached temporarily for performance but can be configured to expire immediately if needed for sensitive research."
