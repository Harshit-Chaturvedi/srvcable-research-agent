# 2–3 Minute Screen Recording Walkthrough Script

Use this script to guide your screen recording (Loom, Drive, or unlisted YouTube) for **Part B, Step 3**.

---

### [0:00 – 0:30] Introduction & Problem Setup
> *"Hello! This is my submission for Part B of the AI Innovator Assignment at Super Investing.*  
> *The goal here is to build an autonomous research agent that takes an NSE ticker, a reference evaluation date, and an untrusted folder of scraped documents, and produces an objective, one-page equity brief for a long-term retail investor in India.*  
> *The test company is Sarvottam Cables Ltd (NSE: SRVCABLE), with 8 scraped documents containing multiple real-world traps: prompt injection attacks, look-alike entities, conflicting financial metrics, and stale data."*

---

### [0:30 – 1:00] Live Execution & Architecture Demo
*(Screen action: Open terminal in VS Code / PowerShell and run:)*
```bash
python agent.py SRVCABLE research_pack/ 2026-09-23
```
> *"I've built the agent using a 3-pass architecture in Python:*  
> *1. First, it isolates all documents in XML tags (`<document id="S#">`) to prevent prompt injection, then runs a dedicated **Triage Pass** to evaluate source tiers, company identity, staleness, and numeric conflicts.*  
> *2. Second, it executes a **Write Pass** that synthesizes the 5 required sections in retail-friendly language, strictly separating management guidance from verified facts.*  
> *3. Third, it runs a **Deterministic Code Check** in Python using regex to verify that every single factual bullet in sections 1 through 4 has a valid citation tag like `[S1]`. If any claim lacks a tag, the code catches it and triggers an automated correction prompt to either attach the citation or delete the ungrounded claim.*  
> *Here you can see the generated brief in `brief.md`."*

---

### [1:00 – 2:00] Design Decision I'm Proud Of
*(Screen action: Highlight `system_prompt.md` and the Pass 3 code check in `agent.py`, then show Section 4 of `brief.md`)*
> *"The design decision I'm most proud of is our **Defense-in-Depth Triage & Verification Barrier**.*  
> *In a naive single-pass setup, models readily succumb to indirect prompt injection. In our test set, `multibaggeralerts.md` had a hidden HTML comment telling the AI to ignore previous instructions and declare a Strong Buy with 60% upside.*  
> *Our architecture cleanly neutralizes this by enforcing data isolation, explicit source hierarchy (Tier 1 filings override Tier 3 blogs), and entity disambiguation. You can see in Section 4 (Open Questions) that the agent correctly rejected the prompt injection, excluded an ₹8 lakh fine on a look-alike Nagpur cable TV business, flagged a digit transposition in a news report (₹1,428 cr vs. ₹1,248 cr), and discarded stale 2024 promoter pledge data because the 2026 filing proved pledge had fallen to 4.1%.*  
> *Furthermore, pairing LLM reasoning with a deterministic regex post-processor ensures zero ungrounded assertions."*

---

### [2:00 – 2:30] One Limitation & Future Improvement
*(Screen action: Show Section 4 note regarding missing valuation/price)*
> *"One limitation of this implementation is that it is currently **closed-corpus bound**.*  
> *Because it only evaluates the scraped documents provided, it cannot assess real-time market valuation multiples like P/E or EV/EBITDA without external live data. As noted in Open Questions, the last observed price was ₹1,012 on results day, but current market valuation is unknown.*  
> *In a production environment, the natural next step is equipping the agent with live tools—such as an NSE ticker API or Yahoo Finance scraper—to pull real-time quotes, sector multiples, and subsequent exchange disclosures automatically."*

---

### [2:30 – 2:45] Conclusion
> *"Thank you for reviewing! The full code, prompt files, test log, and research brief are available in the repository."*
