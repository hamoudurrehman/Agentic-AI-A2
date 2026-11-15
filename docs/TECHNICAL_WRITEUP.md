# Why Evidence Grounding and Reciprocal Rank Fusion Beat Frontier Models in Freelancer Copilots: Lessons from 100 Multi-Agent Simulations

**By AI Engineering Team**  
*Published for Medium, LinkedIn Engineering, and AI-4016 R&D Engineering Series*

---

## Introduction: The "Vibes-Based" Proposal Epidemic

If you have spent any time browsing freelance platforms like Upwork, Freelancer, or specialized contractor boards recently, you have witnessed a profound shift: the replacement of human-written proposals with AI-generated fluff. 

With the proliferation of generic wrapper apps powered by frontier LLMs, clients are now inundated with dozens of proposals within minutes of posting a listing. Almost all of them share the exact same pathology:
> *"Dear hiring manager, I am a passionate, detail-oriented senior full-stack rockstar with extensive experience in your required technologies. I guarantee 100% satisfaction, sub-second latency, and unmatched dedication..."*

To the uninitiated developer, this sounds persuasive. To a hiring client with a technical problem, it is an instant disqualification signal. The proposals read like generic marketing copy; they make unverified promises, invent credentials out of thin air, and completely fail to cite verifiable evidence from past production deployments. Worse yet, when contractors attempt to automate bidding completely using autonomous agent loops, they invariably walk into safety minefields: falling for prompt injection attacks planted inside job descriptions, bidding on fraudulent listings soliciting off-platform communications on Telegram, or draining their valuable platform tokens (Connects) on low-probability bids.

Over the past four weeks, as part of the AI-4016 R&D initiative at FAST School of Computing, our engineering team set out to solve this by building **GigBid**—a production-grade, human-in-the-loop multi-agent copilot orchestrated with LangGraph, grounded by Advanced RAG variants, and governed through official Model Context Protocol (MCP) server adapters. 

Across 100+ controlled simulations against **GigSim** (a marketplace simulator featuring LLM-driven simulated clients with hidden preference weights, budget thresholds, and anti-spam heuristics), our experiments revealed findings that directly contradict conventional AI engineering advice.

Here is what we discovered, why our initial assumptions collapsed, and what our findings mean for the future of agentic workflow design.

---

## Finding 1: The Dense Embedding Mirage — Why Naive RAG Fails on Technical Portfolios

When constructing our initial baseline retrieval pipeline (**Variant V0**), we followed standard industry boilerplate: chunk the developer’s portfolio (CV, GitHub repositories, case studies, client reviews, and past proposals), compute dense vector embeddings, and retrieve the top-5 chunks using cosine similarity against the client's job post.

The results were abysmal. On technical listings, V0 achieved an **Evidence Recall@5 of only 0.520** and an **nDCG@10 of 0.490**, culminating in an anemic **42.0% client reply rate** in GigSim.

When we inspected the failure traces, the root cause was obvious: **dense semantic embeddings blur exact library and framework names**. 

Consider a client posting:
> *"Looking for a data engineer to orchestrate dbt transformation models on BigQuery with Celery and Redis message brokers."*

In dense vector space, `dbt`, `Celery`, `Airflow`, `Kafka`, and `Redis` occupy nearly identical semantic neighborhoods—they are all "data engineering / orchestration tools." Consequently, cosine similarity routinely pulled case studies involving Airflow or Spark, while completely overlooking the developer’s specific repository containing production `dbt` macros and Celery tasks simply because the narrative prose around the Airflow project was longer and richer.

### The Solution: Reciprocal Rank Fusion (RRF) with Sparse BM25
To solve this, we implemented **Variant V2: Hybrid Retrieval**, executing sparse Okapi BM25 keyword matching and dense vector search in parallel, fused via Reciprocal Rank Fusion:
$$\text{RRF}(d) = \sum_{m \in \{\text{BM25}, \text{Dense}\}} \frac{1}{60 + \text{rank}_m(d)}$$

The outcome was immediate:
- **Evidence Recall@5 leaped from 0.520 to 0.885** (+36.5 points).
- **nDCG@10 increased from 0.490 to 0.842**.
- Specific technical tokens (`dbt`, `FastAPI`, `PostgreSQL`, `vLLM`) achieved 100% retrieval precision.

**The Takeaway**: For domain-specific agent retrieval, pure dense semantic search is inadequate. Sparse BM25 is not a legacy relic; it is an indispensable precision anchor that prevents embeddings from hallucinating false equivalencies.

---

## Finding 2: The Cross-Encoder Trap — When 0.5% Quality Gain Costs 62% Latency

Once Hybrid RAG was functional, we tested a common optimization recommended across academic retrieval literature: adding a secondary **Cross-Encoder Reranker (Variant V3)** over the candidate pool. The intuition was straightforward: since cross-encoders evaluate the query and document tokens jointly via full cross-attention, they should eliminate false positives that slip through bi-encoder stages.

The experimental data humbled our expectations.

While V3 Cross-Encoder reranking nudged Evidence Recall@5 marginally from **0.885 to 0.890** (+0.005) and nDCG@10 from **0.842 to 0.850**, the cost was staggering:
- **p95 Latency surged from 0.42 seconds to 0.68 seconds**—a **62% latency penalty**.
- Cost per proposal rose from **$0.0022 to $0.0035**.
- Most critically, the simulated client **reply rate remained completely unchanged at 84.0%**.

Why did higher precision fail to produce more client replies? Because in real-world proposal generation, once an agent retrieves the top 2-3 genuine, high-quality evidence items supporting the client's core requirements, **further reordering among the top candidates yields zero downstream value to the writer agent**. The Proposal Writer needs *sufficient, true evidence*, not an obsessively micro-ranked list. 

We made the deliberate engineering decision **not to ship the cross-encoder in production**. Efficiency and execution speed trumped marginal, non-converting benchmark increments.

---

## Finding 3: The "Hallucination Tax" — How Grounded Claim Verification Rescued Client Conversion

The single most consequential component in GigBid’s architecture is not an LLM prompt; it is our **Claim Verification Engine (Requirement R5)**.

Even when provided with verified retrieved chunks, generative language models possess an innate tendency to embellish. In our ablation experiments (**Ablate Claim Verification**), when the writer agent drafted freely from retrieved evidence without verification, it introduced subtle exaggerations:
- Transforming *"optimized a local vLLM pipeline"* into *"architected enterprise LLM infrastructure for 5 years"*.
- Inventing unsubstantiated metrics: *"guaranteed 10x throughput increases"*.

While a naive human reviewer might skim past these claims, GigSim’s client evaluation models—modeled after skeptical real-world hiring managers—penalize ungrounded superlative phrasing. In our ablation study:
- Without claim verification, **unsupported claims averaged 0.28 per proposal**.
- Client reply rates **plummeted from 84.0% down to 61.0%** (a 23-point penalty).

### How We Enforced Zero Hallucinations
We designed the **Claim Verifier Node** as a mandatory deterministic gate positioned between the `ProposalWriter` and the `Critic`:
1. **Sentence Decomposition**: The draft is parsed into atomic assertions.
2. **Evidence Cross-Checking**: Each assertion is evaluated against the source text of the retrieved portfolio chunks using token overlap and semantic bounds.
3. **Tri-State Classification**: Claims are tagged as `supported`, `partly_supported`, or `unsupported`.
4. **Automated Redaction/Rewriting**: Any assertion lacking direct factual grounding is excised or reformulated to reflect strictly verifiable reality before the human ever sees the proposal.

By enforcing this discipline, GigBid achieved an **unsupported claim rate of exactly 0.0%**, directly driving our **84.0% reply rate** and **44.0% hire conversion rate**.

---

## Finding 4: ReAct Agents Break Down Under Tool Overload

A heated debate in the modern AI community centers on architecture: should developers use open-ended, single ReAct agents with function calling, prebuilt supervisors, or rigid, hand-built state graphs?

To answer this empirically (**R&D Question C**), we benchmarked all three paradigms across 50 development jobs with known ground-truth actions:

| Architectural Pattern | Decision Accuracy | Unsupported Claims Caught | Compliance Violations Caught | Tokens / Run | p95 Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **(a) Single ReAct Agent** | 78.0% | 45.0% | 60.0% | 3,450 | 1.25s |
| **(b) Prebuilt Supervisor** | 86.0% | 78.0% | 82.0% | 2,800 | 0.88s |
| **(c) GigBid Hand-Built StateGraph** | **96.0%** | **100.0%** | **100.0%** | **1,820** | **0.42s** |

The single ReAct agent suffered catastrophic failures when presented with our full catalog of 12+ MCP tools. It frequently entered tool-calling loops, passed arguments with corrupted types, and—most dangerously—frequently bypassed compliance and safety checks entirely in its rush to complete the task.

In contrast, our **Hand-Built LangGraph StateGraph**:
- **Forked parallel branches** (`JobAnalyst`, `RiskAssessor`, `FitMatcher`), executing simultaneously to cut wall-clock latency by 66%.
- Guaranteed that safety guards (`RiskAssessor`, `ComplianceGuard`, `ClaimVerifier`) execute **deterministically on every single thread**.
- Reduced token consumption by **47%** by presenting each specialized node with only the narrow context and tool allowlist it strictly needed.

---

## Finding 5: Why True Human-in-the-Loop Demands Memory from Diffs

Many AI products claim to be "human-in-the-loop," but treat the human as a rubber stamp: presenting a modal with a simple "Send" button.

In GigBid, we realized that human oversight is only sustainable if the agent **learns from human intervention**. When a freelancer reviews an agent's proposal draft in GigBid's Proposal Studio, they have three options: approve, reject with a reason, or edit inline.

When the user edits a draft, GigBid computes a token-level `difflib` sequence match against the original agent output. An explicit promotion rule (`evaluate_style_promotion`) analyzes the deletion and insertion patterns:
- Did the user delete the conversational opening? $\rightarrow$ Promote rule: *"Cut greetings; lead directly with technical alignment."*
- Did the user delete adjectives like "passionate"? $\rightarrow$ Promote rule: *"Never use emotional adjectives."*

These promoted rules are stored in a persistent **Style Memory Store**. On subsequent jobs in that category, the Proposal Writer injects these rules directly into its prompt context. As a result, the agent’s drafts continuously converge toward the freelancer’s distinct authentic voice.

---

## Conclusion: Engineering Principles for the Next Generation of AI Copilots

Building GigBid taught us that winning in applied AI is rarely about swapping in a larger frontier model. It is about architectural rigor, deterministic grounding, and absolute respect for platform boundaries.

If you are architecting agentic systems in 2026, keep these four principles close:
1. **Never send a raw LLM to do a retriever's job**: Combine BM25 with dense vectors via RRF to capture exact jargon.
2. **Enforce factual grounding at the architectural layer**: Strip ungrounded assertions before human review; do not rely on prompts alone to prevent hallucinations.
3. **Prefer hand-built state graphs over open-ended tool agents**: Explicit topologies guarantee safety, cut token costs in half, and eliminate infinite routing loops.
4. **Human approval is non-negotiable**: In high-stakes domains involving client reputation and financial transactions, the human must hold the final key.

The full open-source implementation of GigBid, including the complete evaluation runners, MCP servers, and LangGraph orchestrator, is available on GitHub.

---
*Published as part of the FAST-NUCES AI-4016 R&D Assignment Series. Source code, evaluation suites, and engineering design documents are licensed under MIT.*
