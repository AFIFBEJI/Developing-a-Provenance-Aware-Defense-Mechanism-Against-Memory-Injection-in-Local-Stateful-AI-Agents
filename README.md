# Memory Poisoning Robustness in Small, Locally-Deployed LLM Agents

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active--development-yellow.svg)]()
[![LM Studio](https://img.shields.io/badge/runtime-LM%20Studio-black.svg)](https://lmstudio.ai/)
[![Vector Store](https://img.shields.io/badge/memory-Chroma%2FFAISS-003B57.svg)]()
[![Security](https://img.shields.io/badge/focus-AI%20Agent%20Security-critical.svg)]()
[![Reproducibility](https://img.shields.io/badge/reproducible-yes-brightgreen.svg)]()

> A research project investigating memory-poisoning vulnerability and defense efficacy across small, locally-deployed LLM agents (3B–8B) on consumer hardware. The project evaluates attack success rates, defense resource costs, and multi-agent propagation under resource constraints that existing literature has not systematically examined.

---

## Table of Contents

- [Overview](#overview)
- [Project Personnel](#project-personnel)
- [Motivation](#motivation)
- [Research Question & Contributions](#research-question--contributions)
- [System Architecture](#system-architecture)
- [Model Selection](#model-selection)
- [Attack Methodology](#attack-methodology)
- [Defense Evaluation](#defense-evaluation)
- [Multi-Agent Extension](#multi-agent-extension)
- [Metrics](#metrics)
- [Local Model Security Auditor (Tool)](#local-model-security-auditor-tool)
- [Timeline / Roadmap](#timeline--roadmap)
- [Related Work](#related-work)
- [Data and Code Availability](#data-and-code-availability)
- [References](#references)
- [Status](#status)

---

## Overview

This project investigates a specific attack surface in stateful AI agents — **episodic memory poisoning** — with a focus on small, locally-deployed models (3B–8B parameters) running on consumer hardware. Unlike prior work, which evaluates primarily on frontier-scale or cloud-hosted models, this project systematically varies model scale and quantization as primary experimental variables, measuring both attack success and defense resource cost (RAM, latency) as first-class metrics.

The project builds a local agent harness using **LM Studio** and a **vector store (Chroma or FAISS)**, simulates published memory-poisoning attacks (AgentPoison, MINJA, and direct injection), and evaluates defense mechanisms under the same resource-constrained conditions. A multi-agent extension examines lateral propagation of poisoned memories across independent agent personas, and a companion tool — the **Local Model Security Auditor** — repackages the evaluation pipeline into a usable application for scoring any local model's hardware fit and security profile.

---

## Project Personnel

* **Supervisor:**
    * **Afif Beji, Eng., M.Sc.**
        * *Role:* Assistant Professor & Project Supervisor
        * *Institution:* ESPRIT, School of Engineering
* **Interns:**
    * **Hamza Hwaneb**
    * **Mariem Heni**
    * **Oumaima Boulila**
        * *Role:* Fourth-Year Engineering Students (NIDS)
        * *Institution:* ESPRIT, School of Engineering

---

## Motivation

AI agents are increasingly built to persist state across sessions, summarizing interactions into long-term memory rather than starting fresh each time. This introduces a durable attack vector: unlike a single poisoned prompt, a poisoned memory can sit dormant and be retrieved into a context the agent treats as its own trusted history. Current runtime guardrails are largely designed to catch malicious input as it arrives, not malicious content the system already wrote into its own memory and now considers "known."

Existing attack and defense papers evaluate almost exclusively on capable or frontier-scale models, with Attack Success Rate (ASR) as the sole reported metric. No existing paper systematically varies model scale or quantization, tests across multiple small local models on real consumer hardware, or reports defense resource cost (RAM, latency) as a first-class metric. This project targets that gap directly.

---

## Research Question & Contributions

> Are small, locally-deployed LLMs more or less vulnerable to memory-poisoning attacks than large cloud models — and does that change with model size? Do existing defenses hold up under resource constraints nobody has tested them against?

**Four contributions:**

1. **Cross-model benchmark** — memory-poisoning attack success across 3–4 small local LLMs (3B–8B), on real consumer hardware, with quantization held constant (Q4_K_M).
2. **Defense evaluation** — testing existing defense mechanisms under resource constraints (RAM, latency) no prior evaluation reports, isolating the defense's cost from the model's own baseline speed.
3. **Multi-agent extension** — examining whether poison spreads laterally between independent agents, and whether defenses that stop single-agent poisoning also stop propagation.
4. **Shippable tool** — the *Local Model Security Auditor*, a usable app that scores a given local model's hardware fit and security profile using the same pipeline built for the paper.

---

## System Architecture

| Layer | Choice | Notes |
|---|---|---|
| Model server | **LM Studio** (local OpenAI-compatible API) | Serves local GGUF models via a standard API endpoint. |
| Agent orchestration | Custom minimal Python harness | Built for full control over memory read/write to inject poison precisely and measure cleanly. Matches the evaluation-harness approach used in MINJA, AgentPoison, and prior EHR-agent papers. |
| Memory store | **Vector store (Chroma or FAISS)** | Required for embedding-space retrieval attacks (e.g., AgentPoison-style optimized trigger phrases). |
| Agent types | **Two core types**: (1) QA/memory-augmented assistant, (2) sandboxed coding/tool-use agent | QA agent: directly comparable to most existing literature. Tool-use agent: sandboxed (Docker/restricted filesystem), with 2–3 fake tools (`send_email`, `run_shell_command`, `read_file`), measuring action-level attack success (execution, not just output). |

---

## Model Selection

3–4 models spanning size and architecture, all runnable via LM Studio on a consumer laptop:

| Model | Size | Rationale |
|---|---|---|
| Llama-3.2-3B-Instruct | ~3B | Small end, common literature baseline |
| Phi-3.5-mini-instruct | ~3.8B | Different training philosophy (synthetic-data-heavy), useful contrast |
| Qwen2.5-7B-Instruct | ~7B | Mid-size, strong instruction-following |
| Hermes-3-Llama-3.1-8B | ~8B | Strong tool-use fine-tuning; relevant for Phase 3 tool-use agent evaluation |

Same quantization level (Q4_K_M) across all four by default. A quantization-level sweep (Q4 vs. Q5 vs. Q8 of the same model) is a low-cost add-on once the harness exists, isolating whether an effect is driven by model size or by quantization specifically.

---

## Attack Methodology

Attacks are adapted from published, code-available work so ASR numbers are directly comparable to prior baselines:

| Attack | Vector | Source |
|---|---|---|
| Direct injection (baseline) | Obviously malicious prompt writes a false memory directly | Built in-house |
| MINJA-style | Multi-turn, indirect; memory poisoned without looking suspicious in isolation | [MINJA](https://arxiv.org/abs/2503.03704) |
| AgentPoison-style | Optimized trigger phrase manipulates embedding-space retrieval | [AgentPoison](https://github.com/AI-secure/AgentPoison) |
| Adaptive attacker | Attacker aware of the defense, crafts poison to evade it | Built in-house, on top of the above |

Task/dataset: adapted from an existing QA-style memory-agent benchmark (EHR-agent, MINJA, or AgentPoison's provided datasets) rather than built from scratch.

An additional custom benign/poisoned benchmark based on the OWASP ASI06 taxonomy is retained as an exploratory fifth attack category if time allows.

---

## Defense Evaluation

The primary defense under evaluation is **Memory Sandbox** (Leong, 2026), which removes the agent's explicit memory-recall tool entirely rather than classifying memory content. This was the only mechanism in a recent large-scale evaluation (5,040 runs across 9 models) to hold up against poisoning attacks, though it has a known bypass on frontier-scale models. Testing whether this bypass requires frontier-scale reasoning — i.e., whether it appears at all on 3B–8B local models — is a genuinely open, falsifiable question tied directly to this project's core research question.

A second, heavier contrast defense (simplified SMSR-style ablation/majority-vote, or a basic embedding-trust check) is implemented alongside Memory Sandbox so the resource-cost comparison has real spread. Both are evaluated across the full model × attack matrix, reporting ASR reduction, bypass rate, and resource cost.

---

## Multi-Agent Extension

Each team member builds and runs a complete, independent multi-agent system on their own laptop using their assigned model. The setup is **not** a distributed system across collaborators' laptops — it is a homogeneous multi-persona system running sequentially on a single machine.

- **Homogeneous agents**: one loaded model instantiated as 2–3 separate personas (e.g., Researcher, Synthesizer, Fact-Checker). Running multiple different models simultaneously is likely not feasible on consumer hardware, which is itself a relevant limitation to report.
- **Independent memories + message-passing**: each persona has its own vector store; personas exchange messages and recommendations as part of the task loop.
- **Turn-based**: agents take turns calling the same model server sequentially.

**New attack surface:** lateral spread / contagion — poison one agent's memory, measure whether it propagates to a clean peer agent through the message-passing channel (directly analogous to lateral movement in a compromised network).

**Defense extension:** test whether Memory Sandbox-style gating, or a simple "don't store unattributed peer claims without corroboration" rule, also blocks propagation, not just single-agent recall.

---

## Metrics

**Attack effectiveness (per model, no defense):**
- Attack Success Rate (ASR)
- Injection Success Rate (ISR)

**Defense effectiveness (per model, with defense):**
- ASR reduction
- False positive rate
- Memory Sandbox bypass rate

**Multi-agent:**
- Propagation Rate (% of poisoned facts reaching a clean peer agent), with and without defense

**Resource cost (tested across ≥2 defenses of contrasting cost):**
- Added latency (ms) and RAM (MB), measured as the delta between undefended and defended runs of the *same* query — isolates the defense's cost from the model's own baseline speed.
- Reported as a percentage of baseline latency (not just an absolute number): a fixed cost matters proportionally more on slow, CPU-only, small-model hardware.
- CPU-only check (GPU forced off in LM Studio).
- 5–10 repetitions per condition, mean ± variance reported.

---

## Local Model Security Auditor (Tool)

A thin app/CLI wrapped around the same pipeline built for the paper. Point it at a model loaded in LM Studio; it runs the test suite and reports back — a repackaging of existing results into something usable.

**Core (build unconditionally):** hardware-fit verdict (RAM / load-time / tokens-per-sec vs. available hardware), per-attack vulnerability breakdown, defense recommendation with cost tradeoff.

**Worth adding:** multi-trial variance reporting, adaptive-attacker toggle.

**Time-permitting:** quantization-level sweep, local run history (JSON/SQLite).

**Out of scope:** general capability/quality benchmarking (different problem, well-covered elsewhere); any agentic/LLM-driven decision-making about *what* to test (test suite stays deterministic and scripted).

---

## Timeline / Roadmap

| Phase | Focus |
|---|---|
| Phase 1 — Foundation | Harness, attack matrix, baseline (undefended) results across all models |
| Phase 2 — Defense evaluation (single agent) | Memory Sandbox + contrast defense, ASR reduction, bypass rate, resource cost |
| Phase 3 — Tool-use agent | Sandboxed tool-use agent, full attack + defense matrix, action-level ASR |
| Phase 4 — Multi-agent extension | Multi-persona scaffold, propagation attacks, defense extension |
| Phase 5 — Tool + writing | Auditor tool, full analysis, paper drafting, review passes, submission |

Checkpoints at the end of Phases 1, 2, and 4 serve as milestone reviews.

---

## Related Work

**Attacks**
- [AgentPoison](https://github.com/AI-secure/AgentPoison) — embedding-space retrieval manipulation
- [MINJA](https://arxiv.org/abs/2503.03704) — multi-turn indirect poisoning
- MemoryGraft, ShadowMerge, OEP — self-evolving agent attacks
- [Zombie Agents](https://arxiv.org) (Yang et al., 2026) — self-reinforcing injection

**Defenses — content-inspection family (cited for distinction, not adopted as primary)**
- Sunil et al. (2026) — trust-scoring defense
- SuperLocalMemory / Bhardwaj — local-first storage with Bayesian trust scoring
- A-MemGuard — memory guardrail system
- SMSR — certified defense via majority voting
- mguard — production memory-security tool
- LiteLMGuard — quantization/jailbreak-focused (different threat model)

**Defenses — architectural/capability family (this project's evaluation lineage)**
- [Leong (2026)](https://arxiv.org/abs/2605.08442) — Memory Sandbox; large-scale evaluation (5,040 runs, 9 models)
- [MemLineage](https://arxiv.org/abs/2605.14421) (Ouyang & Hou, 2026) — cryptographic provenance + lineage tracking
- [TMA-NM](https://arxiv.org/abs/2606.24322) (Louck, 2026) — formally verified defense; argues content/lineage defenses are structurally insufficient against laundering attacks

**Surveys / Benchmarks**
- April 2026 survey on LLM agent memory security — anchor citation
- Agent Security Bench — 13 backbones, no small/quantized-model axis, no resource-cost metric

---

## Data and Code Availability

All attack payload design draws on publicly available taxonomies (e.g., OWASP ASI06) at zero cost. All code, benchmark data, and middleware are released under the [MIT License](LICENSE) in this repository to support full reproducibility. The entire pipeline runs locally on LM Studio + Chroma/FAISS, at zero API cost.

---

## References

- OWASP Agentic AI Security Initiative — [ASI06: Memory & Context Manipulation](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- Leong (2026) — [arXiv:2605.08442](https://arxiv.org/abs/2605.08442)
- MemLineage — Ouyang & Hou (2026) — [arXiv:2605.14421](https://arxiv.org/abs/2605.14421)
- TMA-NM — Louck (2026) — [arXiv:2606.24322](https://arxiv.org/abs/2606.24322)
- MINJA — [arXiv:2503.03704](https://arxiv.org/abs/2503.03704)
- AgentPoison — [github.com/AI-secure/AgentPoison](https://github.com/AI-secure/AgentPoison)
- [LM Studio](https://lmstudio.ai/)
- [Chroma](https://www.trychroma.com/)
- [FAISS](https://github.com/facebookresearch/faiss)

---

## Status

This repository is in active development. Phase 1 (Foundation) is the current focus; subsequent phases will be added incrementally as milestones are completed.

---

<sub>Maintained as part of an academic research internship. Contributions, issues, and methodological critique are welcome via GitHub Issues.</sub>
