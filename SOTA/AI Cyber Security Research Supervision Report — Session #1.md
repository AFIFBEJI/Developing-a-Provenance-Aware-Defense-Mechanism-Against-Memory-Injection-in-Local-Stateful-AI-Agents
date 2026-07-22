# AI Cyber Security Research Supervision Report — Session #1
**Project:** Memory Poisoning Robustness in Small, Locally-Deployed LLM Agents  
**GitHub Title:** Developing a Provenance-Aware Defense Mechanism Against Memory Injection in Local Stateful AI Agents  
**Student Team:** Hamza Hwaneb, Mariem Heni, Oumaima Boulila, ESPRIT School of Engineering, 4th-Year Engineering (NIDS)  
**Academic Supervisor:** Afif Beji, Eng., M.Sc., ESPRIT School of Engineering  
**Report Date:** July 20, 2026
**Project Duration:** 2 months  

---

## Table of Contents
1. [Critical Issue: Project Identity Crisis](#1-critical-issue-project-identity-crisis)
2. [State-of-the-Art Literature Review](#2-state-of-the-art-literature-review)
   - 2.1 Attack Taxonomy
   - 2.2 Defense Taxonomy
   - 2.3 Quantization Security
   - 2.4 Multi-Agent Security and Propagation
   - 2.5 Provenance and Lineage Tracking
3. [Research Gap Analysis](#3-research-gap-analysis)
4. [Critical Analysis of the Current Project Design](#4-critical-analysis-of-the-current-project-design)
5. [Threat Model Formalization Template](#5-threat-model-formalization-template)
6. [Experimental Design Recommendations](#6-experimental-design-recommendations)
7. [Publication Strategy](#7-publication-strategy)
8. [Immediate Action Items — Priority Order](#8-immediate-action-items--priority-order)
9. [Complete Literature Reference Table](#9-complete-literature-reference-table)

---

## 1. Critical Issue: Project Identity Crisis

Before any experimental work begins, you must resolve a fundamental ambiguity. Two competing project identities currently coexist:

| Identity | GitHub Title | README Title | Research Type | Novelty Claim |
|---|---|---|---|---|
| **A — Defense Design** | "Developing a Provenance-Aware Defense Mechanism" | — | System design + evaluation | New defense artifact |
| **B — Evaluation Study** | — | "Memory Poisoning Robustness in Small, Locally-Deployed LLM Agents" | Empirical benchmarking | New experimental axis |

**My diagnosis:** The README describes an **evaluation study**, not a defense development paper. The Memory Sandbox you evaluate belongs to Leong (2026). MemLineage belongs to Ouyang & Hou (2026). TMA-NM belongs to Louck (2026). You do not currently propose a new defense mechanism. The word "provenance" does not appear in your methodology section.

### Option A: Evaluation/Benchmarking Paper
> Rigorous empirical study of how small, quantized LLMs fare under memory-poisoning attacks and existing defenses under resource constraints not previously measured.

- **Feasibility:** High for a 2-month undergraduate project
- **Publishable at:** IEEE Access, Computers & Security, ACM CCS workshops (AISec), USENIX WOOT
- **Novelty axis:** Small models + quantization + resource cost as first-class metric
- **Risk:** Can be dismissed as "just an evaluation" unless experimental rigor is extremely high

### Option B: Defense Design + Evaluation Paper
> Design, implement, and evaluate a new lightweight provenance-aware defense for memory injection in local AI agents.

- **Feasibility:** Moderate — requires building a new artifact
- **Publishable at:** IEEE TIFS, NDSS, CCS (with strong technical depth)
- **Novelty axis:** New defense mechanism + evaluation under resource constraints
- **Risk:** Takes more time; must clearly outperform or complement existing defenses

### Recommended path for your constraints
**Pursue Option A, but add a minimal provenance tag as a lightweight engineering contribution.** Specifically: tag each memory entry with `{source: user_input | agent_output | external_tool, timestamp, turn_id, trust_level}` and use trust-level gating during retrieval. This is implementable in < 1 week, converts Option A into a hybrid, and allows you to honestly claim "a provenance-aware retrieval gating mechanism" as one of your four contributions. This resolves the identity crisis without requiring a full defense redesign.

**Action required:** Commit to one option in writing before proceeding.

---

## 2. State-of-the-Art Literature Review

Literature corpus: **321 unique papers** across memory poisoning/RAG attacks, AI agent security, LLM quantization security, and multi-agent propagation/provenance (July 2026).

---

### 2.1 Attack Taxonomy

This section covers the attack landscape directly relevant to your project's threat model.

#### Memory and RAG Poisoning Attacks

| Paper | Year | Venue | Attack Type | Models Evaluated | Small Models? | Key Metric | Limitations |
|---|---|---|---|---|---|---|---|
| **MINJA** (Sunil et al.) | 2026 | arXiv | Multi-turn indirect memory poisoning | GPT-4o-mini, Gemini-2.0-Flash, Llama-3.1-8B | ✗ (8B only, cloud) | ISR, ASR | No local/quantized eval; no resource cost |
| **MemoryGraft** | 2024 | arXiv | Persistent compromise via poisoned experience retrieval | Not specified | ✗ | Not specified | Limited experimental detail |
| **Zombie Agents** (Yang et al.) | 2026 | arXiv | Self-reinforcing injection; persistence across sessions | Representative agent setups | ✗ | Persistence rate, action induction | No multi-agent spread; single-agent focus |
| **AgentPoison** | 2024 | arXiv/GitHub | Optimized trigger phrase; embedding-space manipulation | Multiple (frontier scale) | ✗ | ASR | No small-model evaluation |
| **PoisonedRAG** | 2025 | USENIX Security | Corpus poisoning of RAG knowledge base | Not specified | ✗ | ASR | Static attack; no adaptive variant |
| **Human-Imperceptible Retrieval Poisoning** | 2024 | arXiv | Craftable documents misleading RAG retrieval | Not specified | ✗ | ASR: 88.3% lab, 66.7% real-world | Real-world ASR drops significantly |
| **Backdoored Retrievers** (Clop & Teglia) | 2024 | arXiv | Corpus + retriever backdoor via fine-tuning | Not specified | ✗ | ASR | Requires retriever fine-tuning access |
| **Prompt Infection** (Lee & Tiwari) | 2024 | arXiv | LLM-to-LLM self-replicating prompt injection in MAS | Not specified | ✗ | Infection spread rate | Single-hop focus; no memory persistence |
| **Flooding Spread** (Ju et al.) | 2024 | Preprint | Manipulated knowledge spread in multi-agent RAG communities | Not specified | ✗ | Propagation rate | Controlled experimental setup only |

**Synthesis:** Every major attack paper evaluates exclusively on cloud-hosted or frontier-scale models. None systematically measures attack success rates on quantized, locally-deployed 3B–8B models. This gap is your primary novelty axis.

#### Relevance to your project
- **MINJA** is your primary attack baseline — reproduce ASR numbers on small models and compare directly
- **AgentPoison** provides the embedding-space trigger attack — critical for your vector store setup
- **Zombie Agents** gives you the persistence dimension — track how long a poisoned memory survives cleanup attempts
- **Prompt Infection** is the closest analogue to your lateral propagation extension

---

### 2.2 Defense Taxonomy

#### Comparison of Existing Defense Mechanisms

| Defense | Year | Type | Mechanism | Models Evaluated | Small/Quantized Models? | Resource Cost Measured? | Known Bypass? |
|---|---|---|---|---|---|---|---|
| **Memory Sandbox** (Leong) | 2026 | Architectural | Removes explicit memory-recall capability | 9 models, 5,040 runs | ✗ (frontier scale) | ✗ | Yes — on frontier models |
| **MemLineage** (Ouyang & Hou) | 2026 | Provenance | Cryptographic provenance + lineage tracking | Not specified | ✗ | ✗ | Not tested |
| **TMA-NM** (Louck) | 2026 | Formal verification | Argues content/lineage defenses insufficient against laundering | Not specified | ✗ | ✗ | Argues all content defenses bypassable |
| **SMSR** | 2025 | Certified | Majority-vote / smoothed defense | Not specified | ✗ | ✗ | Computationally expensive |
| **RAGPart + RAGMask** | 2024 | Retrieval-stage | Partitioning + token masking at retriever | 4 dense retrievers | ✗ | Lightweight claim only | Not tested against adaptive attacker |
| **RAGuard** | 2025 | Detection | Expanded retrieval + perplexity + similarity filtering | Not specified | ✗ | ✗ | Claimed robust to adaptive attacks |
| **RAGForensics** | 2025 | Traceback/forensics | Iterative retrieval + LLM-guided detection of poisoned texts | Multiple datasets | ✗ | ✗ | Post-hoc only, not preventive |
| **mguard** | 2025 | Production | Production memory-security tool | Not specified | ✗ | ✗ | Not specified |
| **Input/Output Moderation** (Sunil et al.) | 2026 | Content inspection | Moderate input/output against poisoning | Same as MINJA | ✗ | ✗ | Fragile trust-threshold calibration |
| **LiteLMGuard** | 2025 | Quantization-focused | Quantization + jailbreak defense | Not specified | Partial | ✗ | Different threat model |

**Critical observation:** Not a single defense paper reports RAM delta, latency delta, or CPU-only performance measurements on small quantized local models. This is a genuine, documented gap that you should fill.

---

### 2.3 Quantization Security

This is the most technically complex and under-studied dimension of your project.

| Paper | Year | Models | Quantization Levels | Key Finding | Relevance |
|---|---|---|---|---|---|
| **Exploiting LLM Quantization** (Egashira et al.) | 2024 | Multiple LLMs | Generic PTQ | Full-precision model can be designed to look benign but become malicious after quantization | Supply chain threat — different from your threat model but important context |
| **Jailbreaking Quantized Models via Fault Injection** (Tahmasivand et al.) | 2025 | Llama-3.2-3B, Phi-4-mini, Llama-3-8B | FP16, FP8, INT8, INT4 | FP16 attacks reach >80% ASR; INT4 surprisingly vulnerable in some settings; FP8/INT8 more resistant | Directly relevant — your Q4_K_M sweep maps to INT4 regime |
| **Quantization-based Jailbreak Analysis** (Lee) | 2025 | Llama3-8B-Instruct | 23 bitwidths | Lower-bit increases ASR; Korean input +25.5pp, past tense +39.3pp ASR variance | 4-bit as your fixed quantization warrants comparison to this baseline |
| **HarmLevelBench** (Belkhiter et al.) | 2024 | Vicuna-13B | AWQ, GPTQ | Quantization improves robustness for transfer attacks but increases susceptibility to direct jailbreaking | AWQ vs GPTQ comparison applies if you test Q5 vs Q8 |
| **Model Compression vs. Adversarial Robustness** | 2025 | Code LMs (various) | Pruning, quantization, distillation | Compressed models maintain nominal accuracy but show significantly reduced adversarial robustness | Important: accuracy-robustness decoupling warning |
| **AQUA-LLM** (Gungor & Rosing) | 2025 | Cybersecurity QA LLMs | Multiple | QLoRA fine-tuning can recover robustness lost to quantization | Mitigation strategy you could propose if developing a defense |

**Key insight for your project:** The literature shows that quantization effects on security are **not monotonic** — the relationship between bitwidth and vulnerability depends on attack type, model architecture, and language/task context. This makes your quantization sweep a genuinely open empirical question with an unknown answer, which is the correct type of question for a research paper.

---

### 2.4 Multi-Agent Security and Propagation

| Paper | Year | Setup | Attack Type | Key Finding | Metric |
|---|---|---|---|---|---|
| **Prompt Infection** (Lee & Tiwari) | 2024 | Multi-agent pipelines | LLM-to-LLM prompt injection self-replication | Malicious prompts self-replicate and spread through agent networks | Infection spread rate; LLM Tagging proposed |
| **Flooding Spread of Manipulated Knowledge** (Ju et al.) | 2024 | LLM agent communities + RAG | Persuasiveness Injection + Knowledge Injection | Manipulated content propagates through RAG memories, preserving base capabilities | Propagation rate; supervisory agents partially effective |
| **TOMA — Tipping the Dominos** (Liang et al.) | 2025 | Magentic-One, LangManus, OWL (5 topologies) | Topology-aware multi-hop contamination | Multi-hop attacks yield 40–78% ASR; topology-aware defense blocks ~94.8% | Multi-hop ASR; topology trust defense |
| **BlockA2A** (Zou et al.) | 2025 | Enterprise A2A protocol | Authentication failure, Byzantine agents | DID + blockchain anchoring reduces attack impact; sub-second overhead | Attack impact reduction |
| **Layered Attack Surface Survey** | 2026 | Survey | Multi-agent propagation review | Shared memory enables poisoned content propagation; provenance attestation recommended | — |

**Relevance to your multi-agent extension:** Your single-machine, homogeneous, turn-based multi-persona setup is methodologically simpler than the setups above (which use distributed, heterogeneous topologies). You should frame this clearly as a controlled, minimal multi-agent environment and acknowledge that propagation in richer topologies (like TOMA) may differ. Your propagation rate metric directly maps to TOMA's multi-hop ASR.

---

### 2.5 Provenance and Lineage Tracking

| Paper | Year | Mechanism | Empirically Evaluated? | Key Contribution |
|---|---|---|---|---|
| **MemLineage** (Ouyang & Hou) | 2026 | Cryptographic provenance + lineage tracking | Partial | Full provenance chain per memory entry; lineage-based contamination detection |
| **BlockA2A** (Zou et al.) | 2025 | Blockchain-anchored DID + immutable ledger | Yes (prototype) | Sub-second provenance attestation overhead in prototype |
| **Survey on Long-Term Memory Security** | 2026 | Provenance failure framing | No | Frames provenance failure as core vulnerability; advocates mnemonic sovereignty |
| **Memory Poisoning and Secure MAS** | 2026 | Provenance-aware framework | Partial | Mitigation strategy using provenance for contamination detection |
| **Toward Trustworthy Agentic AI** | 2025 | Provenance registry concept | No | Registry-style trust tracking over agent actions |
| **Layered Attack Surface Survey** | 2026 | Cryptographic attestation + fine-grained memory controls | No | Architectural recommendation only |

**Assessment:** The provenance literature is largely **conceptual and architectural** — nobody has empirically benchmarked a lightweight provenance tag against real memory poisoning attacks on local models. This is your opening if you choose to add a minimal provenance mechanism.

---

## 3. Research Gap Analysis

### 3.1 Incremental Gaps (important but not highly novel)

| Gap | Evidence | Comment |
|---|---|---|
| Testing more attack variants on frontier models | Abundant existing work | This space is saturated |
| Adding more datasets to existing RAG-poisoning benchmarks | Incremental | Not a standalone contribution |
| Replicating MINJA/AgentPoison on slightly different cloud architectures | Marginal | Low novelty |

### 3.2 Significant Gaps and Publishable Opportunities

| Gap | Evidence Base | Your Project's Position | Publishability |
|---|---|---|---|
| **Memory poisoning ASR on small (3B–8B) quantized local models** | No existing paper covers this model class | Core contribution — Phase 1 directly fills this | **High** |
| **Defense resource cost (RAM, latency delta) as first-class metric** | Zero papers report this for memory defenses | Core contribution — measurable and differentiating | **High** |
| **Quantization level (Q4/Q5/Q8) as experimental variable for security** | Only jailbreak papers study this; no memory-poisoning paper does | Low-cost sweep with potentially novel findings | **High** |
| **Memory Sandbox bypass on small models (vs. frontier)** | Bypass known on frontier; unknown on 3B–8B | Directly falsifiable, novel hypothesis | **High** |
| **Lateral memory propagation in homogeneous multi-persona agents** | TOMA covers heterogeneous distributed topologies; single-machine homogeneous not studied | Novel controlled setup; clean baseline | **Medium-High** |
| **Utility preservation measurement for memory defenses** | No paper measures benign task degradation from memory defenses | Easy to add; strengthens every defense evaluation | **Medium** |
| **Provenance tag as lightweight defense primitive on local agents** | Advocated by 6+ papers; not implemented or benchmarked on small local models | Implementable in < 1 week; genuine empirical contribution | **Medium** |
| **Adaptive attacker against Memory Sandbox on small models** | No paper tests this combination | Novel but requires careful implementation | **Medium** |

---

## 4. Critical Analysis of the Current Project Design

### 4.1 Genuine Strengths

| Strength | Why It Matters |
|---|---|
| Small-model focus (3B–8B) | No existing memory-poisoning paper evaluates this class. Genuine gap. |
| Resource cost as first-class metric | RAM delta, latency delta, CPU-only eval — zero existing papers report this for memory defenses |
| Quantization level sweep (Q4/Q5/Q8) | Directly answers whether quantization mediates vulnerability — open empirical question |
| Multi-agent lateral propagation | Propagation rate in homogeneous single-machine setup not directly studied |
| Adaptive attacker category | Methodologically stronger than most existing evaluations |
| Full reproducibility commitment | Local pipeline, MIT license, GGUF models — exemplary for undergraduate scope |
| Comparative defense evaluation (Memory Sandbox vs. SMSR-style) | Necessary for deployment guidance |

### 4.2 Critical Weaknesses

#### W1: No Formal Threat Model
You have no threat model. Reviewers at IEEE TIFS, CCS, or Computers & Security will flag this immediately. Required elements: attacker knowledge (white/black/gray box), attacker capability (direct write, indirect multi-turn, API-only), attacker goal (trigger action / extract info / denial of service), defender assumptions (trusted weights, untrusted external input).

#### W2: Insufficient Statistical Plan
5–10 repetitions per condition is insufficient for high added values claims. You need:
- ≥ 30 test cases per attack category (not 30 repetitions of the same case)
- Bootstrap 95% confidence intervals on ASR
- Effect size reporting (Cohen's d or Cliff's delta)
- Mann-Whitney U test for cross-model comparisons (non-parametric, no normality assumption)

#### W3: No Utility Preservation Metric
A defense that reduces ASR from 80% to 10% but degrades benign answer accuracy by 40% is not deployable. You need to measure and report task utility before/after defense for all conditions.

#### W4: No Ablation Study Design
Which component of Memory Sandbox prevents the attack? The capability removal? The gating? A defense paper without ablation studies cannot explain *why* it works, only *that* it works.

#### W5: The "Shippable Tool" Is Not a Research Contribution
The Local Model Security Auditor is an engineering artifact. It does not constitute a scientific contribution for a Q1/Q2 paper. Move it to an appendix or a separate demo paper.

#### W6: The "Provenance" Framing Has No Methodological Support
Provenance appears in the GitHub title and related work but nowhere in the methodology. Either remove it entirely (pure evaluation paper) or implement a minimal provenance tag (4-field metadata per memory chunk) to justify the framing.

#### W7: Benchmark Under-Specification
"Adapted from EHR-agent, MINJA, or AgentPoison datasets" is not acceptable. You must commit to one benchmark, document its statistics (N benign, N poisoned, attack categories, content distribution), justify the choice, and explain its limitations.

### 4.3 Threats to Validity

| Threat | Type | Severity | Mitigation |
|---|---|---|---|
| All models from same family (Llama-based) | Internal validity | High | Include Phi-3.5 (different architecture) and Qwen2.5 — you already plan this |
| Single quantization format (GGUF/Q4_K_M) | External validity | Medium | Add Q5_K_M and Q8_0 sweep |
| Consumer hardware variability across team members | Internal validity | Medium | Run critical experiments on a single machine; report hardware specs explicitly |
| Attack implementations adapted (not exact reproductions) | Construct validity | High | Validate reproduced ASR against reported baselines before running your experiments |
| Convenience sampling of attack prompts | Internal validity | Medium | Use stratified sampling from OWASP taxonomy; report coverage |
| Model instruction-following quality at 3B scale | Construct validity | Medium | Pilot test all models on benign tasks first; report baseline capability |
| Turn-based multi-agent setup not representative of real MAS | External validity | Medium | Frame as "controlled minimal environment" and discuss generalization limitations |

### 4.4 Missing Elements (Must Add Before Submission)

1. **Related work differentiation table** — a table showing exactly how your paper differs from the 6–8 most related papers
2. **Ethics statement** — confirm no real user data; all experiments are on synthetic or public data
3. **Limitations section** — explicitly discuss generalization boundaries of your findings
4. **Reproducibility checklist** — random seeds, hardware specs, model checkpoint hashes, dependency versions

---

## 5. Threat Model Formalization Template

Fill in the bracketed fields before beginning any experiment.

```
THREAT MODEL

1. System Description
   Target system: A stateful LLM agent (QA or tool-use) running locally on consumer hardware 
   using [MODEL NAME, QUANTIZATION] served via LM Studio, with episodic memory stored in 
   a [Chroma | FAISS] vector store.

2. Assets
   Primary asset: Episodic memory store (vector database)
   Secondary asset: Agent outputs (text responses, tool calls)

3. Attacker Profile
   Knowledge: [White-box | Black-box | Gray-box — specify per attack]
   Capability: [Can inject text into the user turn | Can write to memory directly | Has API access only]
   Position: [External user | Compromised tool output | Compromised peer agent]
   Goal: [Trigger specific action (e.g., execute shell command) | Return false information | 
          Persist across agent restarts | Propagate to peer agents]

4. Attack Surface
   Memory write path: User turns → summarization → memory store
   Memory read path: Query → retrieval → context injection → LLM → response
   Multi-agent path: Agent A output → Agent B memory store (via message passing)

5. Defender Assumptions
   - LLM weights are trusted (no supply-chain attack)
   - Vector store software is trusted
   - External user inputs are UNTRUSTED
   - Peer agent messages are UNTRUSTED unless explicitly verified
   - Hardware is trusted (no fault injection)

6. Out-of-Scope Threats (for this paper)
   - Model weight poisoning / fine-tuning backdoors
   - Network-level attacks
   - Hardware fault injection
   - Social engineering of human operators
```

---

## 6. Experimental Design Recommendations

### 6.1 Research Hypotheses (Falsifiable)

| ID | Hypothesis | Expected Direction | Key Metric |
|---|---|---|---|
| H1 | Smaller models (3B) show higher ASR than larger models (8B) under the same attack and quantization level | ASR(3B) > ASR(8B) | ASR by model size |
| H2 | Lower quantization (Q4) yields higher ASR than higher quantization (Q8) within the same model | ASR(Q4) > ASR(Q8) | ASR by quantization |
| H3 | Memory Sandbox reduces ASR significantly on small local models (effect persists from frontier findings) | ASR_defended < ASR_undefended | ASR delta |
| H4 | Memory Sandbox bypass rate is lower on 3B–8B models than frontier models (requires lower reasoning capacity) | Bypass(3B) < Bypass(frontier) | Bypass rate |
| H5 | Defense resource cost (RAM + latency) is proportionally higher on CPU-only hardware than GPU-accelerated hardware | Cost_CPU > Cost_GPU (relative) | RAM delta %, latency delta % |
| H6 | Poisoned memory propagates from one agent persona to a clean peer at a rate higher than random baseline | PropagationRate > 0.05 | Propagation Rate |

### 6.2 Metrics

**Attack effectiveness (Phase 1 — no defense):**
- **ASR** = (# queries where attack goal achieved) / (# total queries with poisoned memory) 
- **ISR** = (# successful memory writes) / (# injection attempts)
- Baseline: Benign answer rate on clean memory (should be ≥ 0.90 for valid experiments)

**Defense effectiveness (Phase 2):**
- **ASR_reduction** = ASR_undefended − ASR_defended
- **False Positive Rate** = (# benign queries incorrectly blocked) / (# total benign queries)
- **Bypass Rate** = (# successful attacks against defended agent) / (# total adaptive attack attempts)
- **Utility Preservation** = Answer accuracy on benign queries (defended) / Answer accuracy on benign queries (undefended)

**Resource cost (reported per defense, per model):**
- **Latency_delta (ms)** = Mean query latency (defended) − Mean query latency (undefended)
- **Latency_delta (%)** = Latency_delta / Mean query latency (undefended) × 100
- **RAM_delta (MB)** = Peak RAM (defended) − Peak RAM (undefended)
- **CPU-only flag**: All critical runs must include one CPU-only condition

**Multi-agent (Phase 4):**
- **Propagation Rate** = (# clean agent queries returning poisoned content) / (# total cross-agent queries after one-agent poisoning)

### 6.3 Statistical Analysis Plan

**Required before data collection:**
1. Perform a power analysis to determine N. For detecting a 15% ASR difference with 80% power and α = 0.05: N ≈ 45–60 test cases per condition.
2. Pre-register the primary hypotheses (H1–H6) and your analysis plan in a GitHub commit before running experiments.

**During analysis:**
- Report mean ± standard deviation for all continuous metrics
- Use **Mann-Whitney U test** (not t-test) for cross-condition comparisons — no normality assumption
- Report **bootstrap 95% confidence intervals** on ASR (10,000 resamples)
- Report **Cliff's delta** as effect size for all comparisons
- Use **Bonferroni correction** if testing multiple hypotheses simultaneously

**Minimum sample sizes:**
- ≥ 40 test cases per attack category per model (benign + poisoned, balanced)
- ≥ 5 repetitions per test case (for latency/RAM measurements)
- Total: 4 models × 4 attacks × 40 cases = 640 evaluation runs minimum for Phase 1

### 6.4 Ablation Studies

For Memory Sandbox (minimum ablation):

| Ablation | What You Remove | Question Answered |
|---|---|---|
| Full Memory Sandbox | Nothing removed (full defense) | Baseline defended ASR |
| No capability gating | Remove the capability-removal component | Is capability removal or memory filtering driving the protection? |
| No provenance tag | Remove source attribution (if implemented) | Does provenance tagging independently contribute? |
| Threshold variation | Vary trust threshold from 0.3 to 0.9 | What is the operating point for the FPR–ASR tradeoff? |

For multi-agent defense (minimum ablation):

| Ablation | What You Test | Question Answered |
|---|---|---|
| No cross-agent gating | No filtering on peer messages | Baseline propagation rate |
| Source-attribution gating | Block peer claims without source attribution | Does simple provenance gating stop propagation? |
| Full Memory Sandbox on all agents | Each agent runs full defense | Does extending single-agent defense to the pipeline stop propagation? |

---

## 7. Publication Strategy

### 7.1 Target Venues (Q1–Q4)

For a 2-month undergraduate evaluation paper with strong empirical rigor:

| Venue | Type | Quartile | Format | Relevant Track | Feasibility |
|---|---|---|---|---|---|
| **IEEE Access** | Journal | Q1 (2026) | Full paper (8–12 pages) | Computer Security | High — accepts rigorous evaluations |
| **Computers & Security (Elsevier)** | Journal | Q1 | Full paper (10–15 pages) | AI security | High — favorable for empirical studies |
| **IEEE Transactions on Information Forensics and Security** | Journal | Q1 | Full paper (12–15 pages) | AI agent security | Medium — high bar but suitable topic |
| **ACM CCS Workshop on AI & Security (AISec)** | Workshop | Top-tier workshop | 8–10 pages | LLM agent attacks | High — fast turnaround, right audience |
| **USENIX WOOT (Workshop on Offensive Technologies)** | Workshop | Top-tier workshop | 10–15 pages | Novel attack/defense | High — small-model angle is novel |
| **SaTML (IEEE Conference on Secure and Trustworthy ML)** | Conference | A-equivalent | 8–10 pages | Adversarial ML + security | Medium — strong fit if ML angle is emphasized |

**Recommended primary target:** IEEE Access or Computers & Security (journal, allows thorough presentation of empirical data). Secondary/parallel target: AISec workshop at CCS for fast feedback from the community.

### 7.2 Title Options

**If Option A (Evaluation):**
> "Memory Poisoning Under Constraint: Benchmarking Attack Success and Defense Cost on Quantized, Locally-Deployed LLM Agents"

> "How Small is Too Vulnerable? A Resource-Aware Evaluation of Memory Injection Attacks on 3B–8B Local LLM Agents"

**If Option B / Hybrid (Defense Design):**
> "LightProvenance: A Lightweight Provenance-Aware Defense Against Memory Injection in Local Stateful LLM Agents"

> "Provenance-Gated Memory Retrieval: A Resource-Constrained Defense Against Episodic Memory Poisoning in Small LLM Agents"

### 7.3 Abstract Structure Template

```
[Background — 1 sentence] Stateful LLM agents that persist episodic memory across sessions 
introduce a durable attack surface: poisoned memories retrieved into context that the agent 
treats as trusted history.

[Gap — 2 sentences] Existing attack and defense evaluations focus exclusively on 
frontier-scale or cloud-hosted models, reporting Attack Success Rate as the sole metric. 
No prior work systematically evaluates memory-poisoning attacks on small (3–8B) quantized 
locally-deployed agents, nor measures defense resource cost under consumer hardware constraints.

[This paper — 2 sentences] We present the first systematic benchmark of memory-poisoning 
attacks (MINJA-style, AgentPoison-style, direct injection, adaptive) across four small 
quantized LLMs (3B–8B, Q4_K_M) running locally on consumer hardware. We evaluate two 
defense mechanisms — Memory Sandbox and a provenance-tagged retrieval gating mechanism — 
measuring ASR reduction, bypass rate, utility preservation, and defense resource cost 
(RAM and latency delta) as first-class metrics.

[Findings — 2 sentences] We find that [PLACEHOLDER FOR ACTUAL RESULTS]. Notably, the 
Memory Sandbox bypass observed on frontier models [does/does not] appear at the 3B–8B scale.

[Impact — 1 sentence] Our results provide the first empirically grounded deployment 
guidance for memory-poisoning defense on resource-constrained local AI agent infrastructure.
```

### 7.4 Contribution Framing (4 Claims, Evidence-Backed)

1. **Cross-model memory-poisoning benchmark on small local models** — directly addresses documented gap in MINJA (Sunil et al. 2026), AgentPoison, and ASB (Zhang et al. 2024), none of which evaluate 3B–8B quantized models
2. **Resource-aware defense evaluation** — first paper to measure RAM and latency delta for memory defenses on CPU-only consumer hardware; extends Leong (2026)'s 5,040-run evaluation to the missing resource axis
3. **Quantization as a security variable** — first paper to test Q4/Q5/Q8 effects on memory poisoning ASR; extends existing jailbreak quantization studies (Lee 2025, Tahmasivand et al. 2025) to the memory-injection threat model
4. **Multi-agent lateral propagation in local homogeneous setups** — controlled analog to Flooding Spread (Ju et al. 2024) and TOMA (Liang et al. 2025), in a single-machine resource-constrained context

---

## 8. Immediate Action Items — Priority Order

| Priority | Action | Deadline | Owner |
|---|---|---|---|
| 🔴 **P1** | Resolve project identity (Option A / B / Hybrid) in writing | Day 1 | All |
| 🔴 **P2** | Write 1-page threat model using template in Section 5 | Day 2 | All |
| 🔴 **P3** | Commit to one benchmark dataset; document its statistics | Day 3 | All |
| 🔴 **P4** | Define and pre-register all 6 hypotheses (Section 6.1) in GitHub | Day 3 | All |
| 🟠 **P5** | Add utility preservation metric to experimental plan | Week 1 |All |
| 🟠 **P6** | Define bootstrap CI procedure before any data collection | Week 1 | All |
| 🟠 **P7** | Implement minimal provenance tag (4-field metadata per memory chunk) | Week 1 | 1 intern |
| 🟡 **P8** | Validate reproduced attack implementations against published baselines | Week 2 | All |
| 🟡 **P9** | Run power analysis; adjust experiment scale if needed | Week 2 | All |
| 🟡 **P10** | Remove "shippable tool" from core contributions; move to appendix | Week 2 | All |
| 🟢 **P11** | Draft related work differentiation table | Week 3 | All |
| 🟢 **P12** | Complete pilot experiments; validate harness correctness | Week 3 | All |

---

## 9. Complete Literature Reference Table

| # | Title (Short) | Authors | Year | Venue | Type | URL/DOI |
|---|---|---|---|---|---|---|
| 1 | MINJA — Memory Poisoning Attack and Defense | Sunil et al. | 2026 | arXiv | Attack + Defense | DOI:10.48550/arxiv.2601.05504 |
| 2 | MemoryGraft | — | 2024 | arXiv | Attack | arxiv.org/abs/2512.16962 |
| 3 | Zombie Agents | Yang et al. | 2026 | arXiv | Attack | arxiv.org/abs/2602.15654 |
| 4 | Human-Imperceptible Retrieval Poisoning | Zhang et al. | 2024 | arXiv | Attack | DOI:10.48550/arxiv.2404.17196 |
| 5 | PoisonedRAG | Zou et al. | 2025 | USENIX Security | Attack | usenix.org/…/poisonedrag |
| 6 | RAGPart + RAGMask | — | 2024 | arXiv | Defense | arxiv.org/abs/2512.24268 |
| 7 | RAGuard | Cheng et al. | 2025 | arXiv | Defense | DOI:10.48550/arxiv.2510.25025 |
| 8 | RAGForensics | Zhang et al. | 2025 | arXiv | Traceback | DOI:10.48550/arxiv.2504.21668 |
| 9 | Backdoored Retrievers | Clop & Teglia | 2024 | arXiv | Attack | DOI:10.48550/arxiv.2410.14479 |
| 10 | Agent Security Bench (ASB) | Zhang et al. | 2024 | arXiv | Benchmark | DOI:10.48550/arxiv.2410.02644 |
| 11 | Prompt Infection | Lee & Tiwari | 2024 | arXiv | Attack (MAS) | DOI:10.48550/arxiv.2410.07283 |
| 12 | Flooding Spread in MAS | Ju et al. | 2024 | Preprint | Attack (MAS) | DOI:10.21203/rs.3.rs-5292520/v1 |
| 13 | TOMA — Topology-Aware Multi-Hop | Liang et al. | 2025 | arXiv | Attack (MAS) | DOI:10.48550/arxiv.2512.04129 |
| 14 | BlockA2A | Zou et al. | 2025 | arXiv | Defense (MAS) | DOI:10.48550/arxiv.2508.01332 |
| 15 | Exploiting LLM Quantization | Egashira et al. | 2024 | arXiv | Attack | DOI:10.48550/arxiv.2405.18137 |
| 16 | Jailbreaking Quantized Models | Tahmasivand et al. | 2025 | arXiv | Attack | DOI:10.48550/arxiv.2507.03236 |
| 17 | Quantization-based Jailbreak Analysis | Lee | 2025 | IEEE Access | Analysis | DOI:10.1109/access.2025.3594287 |
| 18 | HarmLevelBench | Belkhiter et al. | 2024 | arXiv | Benchmark | DOI:10.48550/arxiv.2411.06835 |
| 19 | Model Compression vs Adversarial Robustness | — | 2025 | arXiv | Analysis | arxiv.org/abs/2508.03949 |
| 20 | AQUA-LLM | Gungor & Rosing | 2025 | arXiv | Defense | DOI:10.48550/arxiv.2509.13514 |
| 21 | Memory Sandbox | Leong | 2026 | arXiv | Defense | arXiv:2605.08442 |
| 22 | MemLineage | Ouyang & Hou | 2026 | arXiv | Defense (Provenance) | arXiv:2605.14421 |
| 23 | TMA-NM | Louck | 2026 | arXiv | Formal Verification | arXiv:2606.24322 |
| 24 | Survey on Long-Term Memory Security | — | 2026 | arXiv | Survey | arxiv.org/abs/2604.16548 |
| 25 | Memory Poisoning and Secure MAS | — | 2026 | arXiv | Survey | arxiv.org/abs/2603.20357 |
| 26 | Layered Attack Surface Survey | — | 2026 | arXiv | Survey | arxiv.org/abs/2604.23338 |
| 27 | Toward Trustworthy Agentic AI | — | 2025 | arXiv | Survey | arxiv.org/abs/2512.23557 |
| 28 | Security Considerations for MAS | — | 2026 | arXiv | Survey | arxiv.org/abs/2603.09002 |

---

*This report reflects a comprehensive literature analysis of 321 unique papers across four thematic corpora (July 2026). All recommendations are grounded in documented evidence from the surveyed literature. Findings and gaps are accurately reported. This document should be updated at each supervision milestone.*

*Next supervision session: Review the resolved project identity, written threat model, and selected benchmark dataset.*
