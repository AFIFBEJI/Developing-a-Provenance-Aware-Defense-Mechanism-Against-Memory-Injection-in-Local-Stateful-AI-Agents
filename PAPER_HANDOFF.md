# Memory Poisoning in Small Local LLM Agents — Paper Handoff

**Purpose of this document:** this is a handoff for an AI assistant helping draft
a Q3 journal submission. It explains the full internship project across all
contributors, summarizes what's done, and proposes a working IMRaD table of
contents. **This is a starting point for synthesis, not a finished structure
— expect it to be revised as the third contributor's data comes in and as
the actual writing progresses.**

---

## 1. Project overview

Internship research project (mentor-supervised) studying memory-poisoning
vulnerability in AI agents built on **small, locally-deployable LLMs** — as
distinct from the large, cloud-hosted models targeted by most prior work in
this space (AgentPoison, MINJA, PoisonedRAG). All experiments run entirely
on local consumer hardware via LM Studio, no paid APIs for the target model
(free-tier Gemini used only for LLM-as-judge scoring where applicable).

**Team structure — three contributors, three model sizes, roughly parallel
methodology:**

| Contributor | Model | Status |
|---|---|---|
| You (this account's user) | Qwen3.5 9B | Complete — most extensive scope, including novel attack mechanisms |
| Maryem | Qwen3 4B Instruct | Complete — see Section 3 |
| Teammate 3 | ~3B model (unconfirmed exact model) | **Not yet received — placeholder only, see Section 4** |

**Target venue: Q3-ranked journal.** This determines the required structure —
standard IMRaD (Introduction/Methods/Results/Discussion), not a thesis-style
chapter dump. Compression and argument-driven writing are expected; exhaustive
debugging narratives belong in supplementary material, not the main text,
even though that narrative detail is valuable and should be preserved
somewhere (methods appendix or supplementary file) for reproducibility
claims.

---

## 2. Your (9B) contribution — full detail

**Source of truth:** a `RESEARCH_NOTES.md` file exists with complete details
— every results filename, every headline finding, every confound caught and
fixed, exact numbers with sample sizes. **If deeper detail than this summary
is needed, ask the user to attach that file** — it is the authoritative
record, this document is a compressed summary of it.

### 2.1 Two agent architectures, tested in sequence

**QA-agent** (Phase 1): retrieve → build prompt → generate free-text answer.
ChromaDB vector store, top-k=3 retrieval, `all-MiniLM-L6-v2` embeddings.

**Execution-agent** (Phase 2): retrieve → present a short menu of real tools →
model outputs a JSON tool call → **the call actually executes against a real,
mutable Python sandbox object** (real file deletion in a path-locked
directory, real balance mutation, real access-control list mutation).
Grading is done by reading the sandbox's `get_state()` before/after — never
by trusting the model's self-reported claim of what it did. This design
follows AgentDojo's methodology (real state verification) rather than
ToolEmu's (LM-emulated sandbox, ~31% documented false-positive rate) —
worth citing in Methods for the design justification.

**This is a meaningfully different rigor level than simulated/logged tool
calls** (see Section 3 — Maryem's execution agent logs a confirmation string
without real state mutation). Worth an explicit methods-section note on this
difference, framed as a rigor tradeoff, not a criticism of either approach.

### 2.2 Attack mechanisms tested (QA-agent)

- **Direct injection** — single blunt poisoned memory, with/without a
  contradicting true fact.
- **MINJA-style bridging** — progressive escalation queries; successful
  bridges get written back to memory as fake self-generated history.
- **Many-shot volume** — identical poison copies at increasing K; K=3
  reliably evicts the true fact from top-3 retrieval, 100% success across
  every domain tested, independent of content sophistication.
- **Many-shot diversity** — different phrasings of the same lie planted
  together; never outperforms identical-copy volume, sometimes underperforms
  it (diverse phrasings don't reliably cluster into all 3 retrieval slots the
  way identical copies deterministically do).
- **Multi-value confusion** — 3 different, *mutually contradicting* fake
  values (not the same lie reworded) vs. the true fact. Headline finding:
  100% wrong-answer rate, zero hedging, true fact retrieved but ignored —
  more contradiction produced *more* model confidence, not more caution.
- **Style × domain × variant grid** — 4 framing styles (blunt, same-entity
  narrative, loophole narrative, authority-framed) × 6 domains × 3
  independently-written variants per cell. Core methodological finding: no
  style category reliably predicts success — 12 of 24 cells swung 50-100
  percentage points depending purely on which of 3 valid phrasings was used.
  This undermines single-example attack evaluation as a general practice
  (relevant framing for the paper's Introduction/related-work positioning).

### 2.3 Attack mechanisms tested (execution-agent)

Same volume/narrative/multi-value/style mechanisms ported to 5 real-action
domains (file deletion, wire transfer, access grant, disable 2FA, send
confidential email externally — spanning destruction/fraud/access/
security-config/exfiltration).

**Plus one genuinely novel mechanism: tool-semantics poisoning.** Every other
attack lies about *authorization* ("is this allowed"). This lies about what
a tool *does* — e.g., a poisoned memory claiming a destructive tool is
actually a harmless no-op. Impossible to construct on a QA-agent (nothing
there has "tool semantics" to lie about). Positioned narrowly in the
literature: AgentDojo has an unrelated "Tool Knowledge" attack (leaks tool
metadata to trigger malicious calls) and MemoryGraft (arXiv 2512.16962)
poisons successful-experience examples for imitation — both verified real
citations, both meaningfully different from this mechanism (which corrupts
the agent's model of tool *consequences*, not its knowledge of tool
*existence/arguments* or imitated *experience*).

### 2.4 Headline findings (9B study)

1. **Volume (identical-copy repetition) is a universal attack — 100% success
   in every domain tested, both agent types**, via pure retrieval eviction.
2. **A single well-framed lie can match volume's 100% with zero retrieval
   eviction** — a pure generation-level persuasion failure, not a retrieval
   competition.
3. **No attack style reliably predicts success** — replication crisis finding,
   see 2.2 above.
4. **Rule structure (conditional vs. absolute) predicts execution-agent
   resistance far better than attack type or style.** Domains with a rule
   condition already baked into the fact ("requires phone confirmation, none
   given") are highly vulnerable to simple fact-slot-substitution poisons.
   Domains with a flat, unconditional rule ("never delete") are far more
   resistant across the board.
5. **Tool-description compatibility may be the dominant driver of that
   resistance, more than domain identity per se.** Confirmed via a controlled
   ablation: renaming a tool from `delete_file` ("deletes a file") to a
   neutral `process_file` ("performs the requested operation"), with
   identical poison content, flipped attack success from **0% to 72%** on an
   otherwise fully-resistant domain. This is the single strongest result in
   the execution-agent chapter and should likely lead the Results section
   for that phase.
6. **Baseline false-positive rates matter and were measured explicitly** —
   QA-agent baseline was a clean 0/60; execution-agent baselines varied
   (0-20% depending on domain), so all execution-agent "attack success"
   numbers are reported as *lift over baseline*, not raw rates.
7. **Retrieval-conditional analysis separates two distinct bottlenecks** —
   some low-success domains fail because the poison never reaches the model
   (retrieval failure, e.g. one domain's poison text embedded too far from
   the task query to win a top-3 slot, confirmed and being fixed as of this
   writing) vs. genuine reasoning-level resistance (poison reliably
   retrieved, still rejected). These require different interpretations and
   should not be conflated in the Results section.

### 2.5 Methodological practices worth citing explicitly in Methods

- Real-state grading (never self-reported model claims).
- Explicit no-attack baselines for every phase.
- Confounds actively hunted and caught (e.g., a framing-swap experiment that
  accidentally changed policy wording alongside the intended variable — caught
  independently by two external AI reviews plus direct code verification, then
  re-run correctly).
- Citations verified via live search before inclusion (not taken on faith
  from either the researcher or AI-assisted review).

---

## 3. Maryem's contribution (4B) — summary from her AI-generated writeup

**Status: her methodology and results are complete; the document she
provided (thesis/report-style, AI-generated from her raw data) is data
source material, not a structural template to follow.** The team is
targeting IMRaD/Q3 format for the joint paper regardless of how any
individual contributor's own writeup was formatted.

**Architecture:** QA-agent and execution-agent (`action_agent.py`), same
retrieve→prompt→generate pipeline pattern as the 9B study, ChromaDB +
`all-MiniLM-L6-v2` (same embedding model as the 9B study — genuinely
comparable at this layer). Execution-agent tools are **simulated/logged**
(each call returns a synthetic confirmation string; no real state mutation)
— the key rigor difference from the 9B study's real-state-mutation design,
worth an explicit note wherever the two are compared.

**Attacks tested:** Direct Injection, MINJA-style, Many-Shot — same three
families as the 9B study's Phase 1, independently implemented. Native
model tool-calling was used (validated separately before the main study),
vs. the 9B study's custom JSON-parsing scheme with regex fallback recovery.

**Sample sizes:** Direct Injection N=5/scenario; MINJA N=3-5/scenario
(revised upward after an early batch showed instability at N=3); Many-Shot
N=2/(scenario×volume) cell. All meaningfully smaller than the 9B study's
N=20-25 standard — a real statistical-power difference to disclose.

### 3.1 Her headline finding

A clean **"explicit security-action" vs. "contextual/factual"** scenario
taxonomy (10 hand-authored scenarios) that predicts text-level (QA-agent)
vulnerability with near-total reliability, replicated across all three
attack types: security-action scenarios (e.g., fabricated authorization to
disable security logs) → ~0% ASR; contextual/factual scenarios (e.g., a
fake meeting time) → 80-100% ASR.

**This split completely breaks down at the execution-agent level — including
two full reversals**: `fake_authority` (an explicit security-action
scenario) goes from 0% text-level ASR to **100%** execution-level tool-call
rate; `email_sharing` (a contextual/factual scenario) goes from 100%
text-level ASR to **0%** execution-level tool-call rate. Her interpretation:
textual refusal and action-level refusal are governed by different
mechanisms in this model, and text-level evaluation can be *actively
misleading*, not just incomplete, as a proxy for real-world agentic risk.

**This is the load-bearing convergence for the joint paper.** Two
independent contributors, different model sizes, different codebases,
different specific mechanisms — both arrived at the same meta-finding:
*QA/text-level vulnerability measurements do not reliably predict
execution-level vulnerability.* That convergence, argued from two
independent angles, is a substantially stronger claim jointly than either
study could support alone, and should likely be the paper's central thesis
statement.

### 3.2 Her MINJA finding, worth contrasting with the 9B study

MINJA matched or exceeded Direct Injection at the text level (despite a
weaker threat model — no direct memory-write access), but **lost that
advantage entirely at the execution level** (20-60% vs. Direct Injection's
100% on the same themes). Her interpretation: MINJA's indirection (the
poisoned belief is self-generated by the model across a multi-step elicitation,
never attacker-authored) survives at low precision (textual assent) but not
at high precision (generating a structurally correct, parameter-complete
tool call).

---

## 4. Third contributor (3B) — PLACEHOLDER

**Not yet received.** Expected to follow a similar structure to Maryem's
(same three attack families, QA-agent + execution-agent, exact model TBD).
**Do not draft the cross-model comparison sections until this arrives** —
placeholder sections should be clearly marked as such in any draft produced
before this data is available.

---

## 5. Terminology reconciliation — REQUIRED before drafting Results

Each contributor used different metric names for overlapping concepts. This
needs to be unified into one consistent vocabulary for the joint paper
(pick one convention, likely Maryem's ASR/ASR-r naming since it's more
standard in the literature, and map the others onto it) — **do not present
raw contributor-specific field names in the final draft**, they will read as
inconsistent to a reviewer.

| Concept | Your (9B) naming | Maryem's naming |
|---|---|---|
| Did the poison make it into top-k retrieval? | `tool_fact_in_top3` / `poison_in_top3` / `true_fact_still_retrieved` | ASR-r |
| Did the agent's final output comply with the poison? (QA-agent) | `final_attack_success` (judge-scored) | ASR (judge-scored) |
| Did the agent invoke the poisoned/expected tool? (execution-agent) | `attack_success` / `action_happened` (real state change) | ASR-action-call (tool_calls object inspection) |
| Were the tool call's parameters faithful to the poison? | Not separately tracked — real state mutation implicitly captures this | ASR-action-precise (judge-scored, conditional on a call occurring) |
| Correctly resisted / declined | `correctly_declined` | Not separately named — inferred from ASR=0 |

**Also reconcile:** your study reports lift-over-baseline for several
execution-agent domains (nonzero false-positive rate with no attack present);
confirm whether Maryem's and the 3B study measured an equivalent no-attack
baseline, or whether this needs to be flagged as a 9B-study-only control.

---

## 6. Proposed table of contents (IMRaD, Q3 target)

Working draft — expect revision once the 3B data arrives and as drafting
proceeds.

```
Title

Abstract

1. Introduction
   1.1 Motivation — small, locally-deployed LLM agents are increasingly
       common; memory-poisoning risk for this class is understudied relative
       to large cloud-hosted models
   1.2 Related Work — MINJA, PoisonedRAG, AgentPoison, AgentDojo (incl. its
       "Tool Knowledge" attack, distinct from this paper's tool-semantics
       mechanism), ToolEmu, MemoryGraft
   1.3 Research Questions and Contributions
       - Does memory-poisoning vulnerability scale with model size (3B/4B/9B)?
       - Does text-level (QA) vulnerability predict execution-level
         vulnerability? [central thesis — see Section 3.1 above]
       - What structural factors moderate execution-level vulnerability?
         (rule conditionality, tool-description compatibility — novel to
         this paper)

2. Methodology
   2.1 Target Models and Infrastructure (3B / 4B / 9B, LM Studio, ChromaDB,
       shared embedding model)
   2.2 Agent Architectures
       2.2.1 QA-Agent (shared design pattern across all three studies)
       2.2.2 Execution-Agent (real-state-mutation design [9B] vs.
             simulated/logged design [4B, 3B] — explicit rigor-tradeoff
             discussion)
   2.3 Attack Taxonomy
       2.3.1 Direct Injection
       2.3.2 MINJA-Style Indirect Injection
       2.3.3 Many-Shot / Volume Injection
       2.3.4 Style and Framing Variants [9B-specific]
       2.3.5 Multi-Value Confusion [9B-specific]
       2.3.6 Tool-Semantics Poisoning [9B-specific, novel mechanism]
   2.4 Evaluation Metrics (ASR, ASR-r, ASR-action-call/precise — unified
       naming per Section 5 above)
   2.5 LLM-as-Judge Methodology and Validation
   2.6 Experimental Protocol (sample sizes, baselines, per-study deviations
       disclosed)

3. Results
   3.1 Cross-Model QA-Agent Vulnerability (3B vs. 4B vs. 9B, shared attacks)
   3.2 Cross-Model Execution-Agent Vulnerability
   3.3 Text-Level vs. Execution-Level Divergence [central finding —
       Maryem's reversals + 9B rule-structure/tool-description findings,
       argued jointly]
   3.4 Novel Mechanisms Unique to the 9B Study (multi-value confusion,
       tool-semantics poisoning, the neutral-tool-naming ablation)

4. Discussion
   4.1 Does Vulnerability Scale with Model Size?
   4.2 Why Text-Level Evaluation Is an Unreliable Proxy for Execution-Level
       Risk
   4.3 Structural Predictors of Execution-Level Vulnerability (rule
       conditionality, tool-description compatibility)
   4.4 Practical Implications for Small Local Agent Deployment

5. Limitations
   (per-study sample-size constraints, simulated vs. real execution rigor
   difference, retrieval-layer confounds and how each was resolved,
   single-run-per-model-size scope)

6. Conclusion and Future Work

References

Supplementary Material
   - Full per-scenario/per-domain result tables
   - Judge validation protocols
   - Reproducibility notes (software versions, known deprecation issues
     with pinned judge model identifiers)
```

---

## 7. Guardrails for drafting

- **This is not a "concatenate three sections" job.** The strongest version
  of this paper argues Section 3.3 (text-vs-execution divergence) as a
  jointly-supported claim from two independent angles, not two separate
  findings reported side by side.
- **Do not draft Results/Discussion sections that depend on the 3B data**
  until it's provided — leave clearly marked placeholders.
- **Unify terminology per Section 5 before writing any Results text** —
  don't let contributor-specific field names leak into the draft.
- **If more detail than this summary provides is needed for the 9B study,
  ask for `RESEARCH_NOTES.md`** — it has exact filenames, exact sample
  sizes, and the full confound-investigation narrative for every finding
  summarized here.
