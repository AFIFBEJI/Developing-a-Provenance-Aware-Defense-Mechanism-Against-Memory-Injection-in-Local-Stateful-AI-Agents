# MemGuard

**Developing a Provenance-Aware Defense Mechanism Against Episodic Memory Injection in Local Stateful AI Agents**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)]()
[![Ollama](https://img.shields.io/badge/runtime-Ollama-black.svg)](https://ollama.com/)
[![SQLite](https://img.shields.io/badge/memory-SQLite%20FTS5-003B57.svg)](https://www.sqlite.org/fts5.html)
[![Security](https://img.shields.io/badge/focus-AI%20Agent%20Security-critical.svg)]()
[![Reproducibility](https://img.shields.io/badge/reproducible-yes-brightgreen.svg)]()

> A research project investigating whether a local, stateful AI agent can be defended against poisoned long-term memories using provenance tagging and structural isolation, without breaking its ability to serve legitimate requests.

---

## Table of Contents

- [Overview](#overview)
- [Project Personnel](#project-personnel)
- [Motivation](#motivation)
- [Threat Model](#threat-model)
- [Research Gaps Addressed](#research-gaps-addressed)
- [Objectives](#objectives)
- [Methodology](#methodology)
- [Expected Results](#expected-results)
- [Evaluation Metrics](#evaluation-metrics)
- [Repository Structure](#repository-structure)
- [Deliverables](#deliverables)
- [Risks and Limitations](#risks-and-limitations)
- [Data and Code Availability](#data-and-code-availability)
- [References](#references)
- [Status](#status)

---

## Overview

MemGuard investigates a specific attack surface in stateful AI agents: **episodic memory poisoning**, where an adversary plants latent instructions in an agent's long-term memory store that remain dormant until retrieved into a future context and executed as if trusted. The project builds a local agent on **Ollama** and **SQLite FTS5**, simulates poisoning attacks against it, and develops a lightweight Python middleware that tags memory provenance at write time and structurally isolates untrusted memories at read time.

The end goal is not just a working proof-of-concept exploit, but a measurable, reproducible defense: one that meaningfully reduces attack success without materially degrading the agent's ability to do its job.

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

AI agents are increasingly built to persist state across sessions, summarizing interactions into long-term memory rather than starting fresh each time. This is useful, but it introduces a durable attack vector: unlike a single poisoned prompt, a poisoned memory can sit dormant and be retrieved into a context the agent will treat as its own trusted history. Current runtime guardrails are largely designed to catch malicious input as it arrives, not malicious content the system already wrote into its own memory and now considers "known." Securing this specific retrieval pipeline is a precondition for deploying long-lived autonomous agents safely.

## Threat Model

The project assumes a local, single-agent deployment where:

- The attacker can influence content that eventually gets written to the agent's episodic memory (e.g., through a tool call, a document ingested by the agent, or a prior conversation turn).
- The attacker cannot directly access or modify the SQLite database file itself — the attack surface is the agent's normal write path, not raw file tampering.
- The defense must operate without an internet connection or paid API access, consistent with the project's zero-cost, fully local design.

## Research Gaps Addressed

| Gap | Current State of Practice | This Project |
|---|---|---|
| **Provenance at the memory layer** | Guardrails filter incoming prompts, not stored memory | Cryptographic tagging of every memory write records where it came from |
| **Trust re-evaluation at retrieval** | Retrieved memories are treated as trusted context by default | Structural boundary wrapping marks retrieved memories as untrusted historical data, not instructions |
| **Quantified defense efficacy** | Largely qualitative or anecdotal discussion of memory attacks | Explicit ASR/BTSR benchmark comparing undefended vs. defended agents |
| **Fully local reproducibility** | Many agent security studies rely on hosted/proprietary LLMs | Entire pipeline runs on Ollama + SQLite, at zero API cost |

## Objectives

- Design a stateful local AI agent utilizing **Ollama** and **SQLite FTS5** as its episodic memory.
- Simulate and quantify memory poisoning attacks using a controlled, custom benchmark.
- Develop a Python-based middleware that implements **cryptographic provenance tagging** during memory writes and **structural isolation** for retrieved memories.
- Evaluate the defense mechanism's efficacy by measuring the **Attack Success Rate (ASR)** and the **Benign Task Success Rate (BTSR)**.
- Produce a comprehensive manuscript suitable for submission to a reputable journal.

## Methodology

**Phase 1 — Baseline Agent Setup**
Build a local stateful agent using Ollama (e.g., Llama-3-8B-Instruct) with SQLite FTS5 as its episodic memory store, capable of writing to and reading from memory across sessions.

**Phase 2 — Attack Benchmark Construction**
Construct a benchmark of 50 benign memory interactions and 50 poisoned memory interactions, drawing on established prompt-injection taxonomies (e.g., OWASP ASI06) to design realistic latent-instruction payloads.

**Phase 3 — Baseline Evaluation**
Run the benchmark against the undefended agent and record the Attack Success Rate (ASR) — how often a poisoned memory is retrieved and executed as an instruction.

**Phase 4 — Provenance-Tagging Middleware**
Implement a write-path middleware that cryptographically tags each memory entry with metadata identifying its provenance (source, timestamp, trust level).

**Phase 5 — Structural Boundary Wrapping**
Implement a read-path middleware that wraps retrieved memories in explicit structural boundaries (e.g., XML/JSON delimiters), signaling to the LLM that this content is untrusted historical data rather than executable instruction.

```text
Baseline retrieval:   [raw poisoned memory text injected directly into context]
Defended retrieval:   <untrusted_memory source="user_upload" trust="unverified">
                         [poisoned memory text, isolated as passive data]
                       </untrusted_memory>
```

**Phase 6 — Defended Evaluation**
Re-run the full benchmark on the defended agent, recording both ASR (should drop) and Benign Task Success Rate (BTSR — should remain high), to assess whether the defense neutralizes attacks without breaking legitimate use.

## Expected Results

| Configuration | Purpose | Expected Outcome |
|---|---|---|
| Undefended agent | Establish attack baseline | High ASR on poisoned memories |
| Provenance tagging only | Isolate contribution of write-side defense | Partial ASR reduction |
| Structural wrapping only | Isolate contribution of read-side defense | Partial ASR reduction |
| Full middleware (tagging + wrapping) | Main contribution | Substantial ASR reduction with minimal BTSR loss |

These are **directional expectations**, not observed results. The actual magnitude of ASR reduction and any BTSR trade-off will depend on model instruction-following behavior and boundary format design, both of which are treated as open empirical questions rather than assumptions.

## Evaluation Metrics

- **Attack Success Rate (ASR)** — proportion of poisoned memories that are retrieved and executed as instructions
- **Benign Task Success Rate (BTSR)** — proportion of legitimate memory retrievals that still function correctly under the defense
- ASR vs. BTSR trade-off curve across boundary format variants (Markdown vs. XML vs. JSON)
- Qualitative failure analysis of cases where the defense under- or over-blocks

## Repository Structure

```
memguard/
├── agent/
│   ├── ollama_client.py       # Wrapper for local LLM inference
│   ├── memory_store.py        # SQLite FTS5 read/write interface
│   └── stateful_agent.py      # Core agent loop
├── attacks/
│   ├── benchmark_generator.py # Builds the 50 benign / 50 poisoned dataset
│   └── payloads/               # Injection payload templates (OWASP ASI06-informed)
├── middleware/
│   ├── provenance_tagging.py  # Write-path cryptographic tagging
│   └── boundary_wrapping.py   # Read-path structural isolation
├── evaluation/
│   ├── run_baseline.py
│   ├── run_defended.py
│   └── metrics.py             # ASR / BTSR computation
├── reports/
│   └── figures/
├── requirements.txt
├── README.md
└── LICENSE
```

## Deliverables

- Documented and reproducible local testing pipeline (Ollama + SQLite).
- Benchmark dataset consisting of 50 benign interactions and 50 poisoned injections.
- Open-source Python middleware featuring provenance tagging and boundary wrapping.
- Experimental report including ASR/BTSR data tables (baseline vs. defended system).
- Scientific manuscript draft (Methodology, Results, and Discussion sections).
- Public GitHub repository complete with a README and reproduction instructions.

## Risks and Limitations

- **Boundary format sensitivity** is the primary practical risk — the LLM's willingness to respect structural boundaries may vary by model and prompt phrasing. Mitigated by testing multiple formats (Markdown, XML, JSON) rather than committing to one upfront.
- **Benchmark realism** is bounded by the custom nature of the poisoned dataset; results reflect performance against the specific attack patterns modeled, not an exhaustive attack surface.
- **Single-model evaluation risk:** initial results are based on one instruction-tuned local model; generalization across model families is a natural extension, not a claim made by this phase.
- **Security caveat:** this project is a research prototype demonstrating a defense concept, not a hardened production security control, and should not be treated as a complete solution for deployed agent systems.

## Data and Code Availability

All attack payload design draws on publicly available taxonomies (e.g., OWASP ASI06) at zero cost. All code, benchmark data, and middleware will be released in this repository to support full reproducibility.

## References

- OWASP Agentic AI Security Initiative — [ASI06: Memory & Context Manipulation](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Ollama](https://ollama.com/)
- [SQLite FTS5](https://www.sqlite.org/fts5.html)

## Status

This repository is in active development. Baseline agent construction and benchmark generation (Phases 1–2) are the current focus; middleware and defended evaluation will be added incrementally as milestones are completed.

---

<sub>Maintained as part of an academic research internship. Contributions, issues, and methodological critique are welcome via GitHub Issues.</sub>
