## TL;DR

Memory poisoning and retrieval/corpus poisoning are now well-documented for both RAG systems and memory-augmented agents; key defenses operate at retrieval, sanitization, or traceback stages, but most work does not evaluate small quantized models, measure resource cost, or fully address multi-agent propagation.

----

## Key papers overview

This section lists the most-cited and methodologically relevant papers on memory or retrieval poisoning and their defenses, and summarizes the items you requested for each paper in a compact comparison table. The table shows only claims traceable to the supplied abstracts; where the abstract does not report a fact the cell lists "insufficient evidence".

| Paper (year) | Attack or defense type | Models evaluated | Evaluation metrics used | Small quantized models tested | Resource cost measured | Multi-agent propagation studied | Key limitations |
|---|---:|---|---:|---:|---:|---:|---|
| Memory Poisoning Attack and Defense on Memory Based LLM-Agents [1] | Memory poisoning attacks (MINJA) and defenses: Input/Output Moderation and Memory Sanitization [1] | GPT-4o-mini, Gemini-2.0-Flash, Llama-3.1-8B-Instruct [1] | Injection success rate; attack success rate; robustness over initial memory, prompt counts, retrieval params [1] | insufficient evidence | insufficient evidence | insufficient evidence | Realistic pre-existing memories reduce effectiveness; sanitization needs careful trust-threshold calibration to avoid overblocking or missed subtle attacks [1] |
| MemoryGraft (preprint) [2] | Persistent memory poisoning via poisoned experience retrieval [2] | insufficient evidence | insufficient evidence | insufficient evidence | insufficient evidence | insufficient evidence | Details on measured robustness and defenses not shown in abstract [2] |
| Zombie Agents (preprint) [3] | Persistent self-reinforcing memory injections (infection + trigger); persistence strategies for sliding-window and RAG memory [3] | evaluated on representative agent setups and tasks (models not specified) [3] | Measured persistence over time and ability to induce unauthorized actions while preserving benign quality [3] | insufficient evidence | insufficient evidence | Not focused on multi-agent propagation; persistence within evolving agent studied [3] | Shows one-time indirect injections can become persistent; points out per-session filtering is insufficient [3] |
| Human-Imperceptible Retrieval Poisoning [4] | Retrieval poisoning via craftable documents that mislead RAG systems [4] | insufficient evidence | Attack success rates reported (88.33% lab; 66.67% real-world) [4] | insufficient evidence | insufficient evidence | insufficient evidence | Preliminary experiments; real-world success lower than lab; scope limited to crafted document attacks [4] |
| PoisonedRAG (title/summary) [5] | Knowledge-corruption attacks on RAG: Naive, Corpus Poisoning, GCG Attack (taxonomy) [5] | insufficient evidence | insufficient evidence | insufficient evidence | insufficient evidence | insufficient evidence | Paper introduces attack taxonomy; detailed experimental coverage not available in snippet [5] |
| RAGPart & RAGMask (defenses) [6] | Retrieval-stage defenses (partitioning and token masking) that operate on retriever level [6] | Four state-of-the-art dense retrievers across two benchmarks (names not given in abstract) [6] | Attack success rate; utility under benign conditions (reduction of ASR while preserving utility) [6] | insufficient evidence | Described as computationally lightweight (no generator changes) [6] | insufficient evidence | Defense effective but has limits under stress tests; interpretable attacks can still challenge defenses [6] |
| RAGuard (defense) [7] | Detection framework: expand retrieval scope + chunk-wise perplexity filtering + similarity filtering [7] | insufficient evidence | Detection / mitigation effectiveness including adaptive attacks [7] | insufficient evidence | insufficient evidence | insufficient evidence | Non-parametric approach; claimed effective vs. strong adaptive attacks but abstract omits resource/latency data [7] |
| RAGForensics (traceback) [8] | Traceback/forensics system to identify poisoned texts responsible for RAG misbehavior [8] | insufficient evidence | Effectiveness at identifying poisoned texts in datasets (iterative retrieval + LLM-guided detection) [8] | insufficient evidence | insufficient evidence | insufficient evidence | First traceback direction; evaluation across multiple datasets but abstract lacks per-model and performance-cost reporting [8] |
| Backdoored Retrievers (corpus/backdoor) [9] | Corpus poisoning and retriever backdoor attacks targeting retriever fine-tuning [9] | insufficient evidence | Attack success rates; backdoor higher ASR but requires retriever fine-tuning [9] | insufficient evidence | insufficient evidence | insufficient evidence | Backdoor attacks more powerful but require victim retriever fine-tuning (more complex adversary setup) [9] |
| Agent Security Bench (ASB) benchmark [10] | Benchmark includes a memory poisoning attack and many prompt-injection/memory scenarios [10] | 13 LLM backbones evaluated in benchmark (names not listed in abstract) [10] | Multiple metrics (8 eval metrics); reports attack success rates (highest average ASR 84.30%) across ~90k cases [10] | insufficient evidence | insufficient evidence | includes agent scenarios (but multi-agent propagation not singled out in abstract) [10] | Large-scale benchmark showing high ASR and limited defense effectiveness in current defenses [10] |

----

## Evaluation practices

This section summarizes how the key papers measure attacks and defenses and what evaluation practices are missing for locally deployed small agents. The reviewed works commonly report attack success and utility tradeoffs but rarely evaluate low-resource deployments.

- **Metrics observed**  
  - **Attack success / injection success rates** are primary metrics in several works, including MINJA reporting injection and attack success measures [1], retrieval-poisoning experiments reporting 88.33% lab and 66.67% real-world success [4], and ASB reporting a highest average attack success rate of 84.30% across many tests [10].  
- **Defense evaluation styles**  
  - **Retrieval-stage defenses** (RAGPart, RAGMask) report reductions in attack success while preserving utility and are designed to be lightweight and retriever-only [6].  
  - **Detection and filtering** approaches (RAGuard) use expanded retrieval and perplexity/similarity filtering to flag poisoned chunks [7].  
  - **Traceback** (RAGForensics) focuses on identifying which corpus texts caused misbehavior via iterative retrieval and LLM-guided detection [8].  
- **Resource- and deployment-focused gaps**  
  - Insufficient evidence that the surveyed papers evaluated or reported performance on small quantized models suitable for local deployment.  
  - Insufficient evidence that papers measured RAM, latency, or end-to-end resource costs for defenses (e.g., per-query latency/ memory overhead).  
  - A few works study persistence and propagation within evolving single agents (Zombie Agents studies persistence across sessions) but most do not experimentally quantify multi-agent infection spread [3] [11].  
- **Multi-agent propagation**  
  - LLM-to-LLM prompt infection is explicitly studied in a multi-agent context by Prompt Infection, which demonstrates self-replicating prompt spread and proposes LLM Tagging mitigation for multi-agent systems [11].  
  - Zombie Agents and MemoryGraft focus on persistence within an evolving agent rather than networked multi-agent propagation [3] [2].

----

## Open research gaps

This section highlights practical open gaps specifically relevant for memory poisoning defenses for small, locally deployed LLM agents. The gaps are synthesized from the coverage and omissions in the papers above.

- Evaluation on small quantized models and edge hardware: most papers provide no evidence of testing 4-bit/8-bit quantized or small ~7B/8B footprints; designing defenses that work under quantization constraints remains open.  
- Measured resource costs and latency tradeoffs: defenses need explicit RAM, CPU, and latency measurements under constrained hardware so practitioners can choose feasible defenses.  
- Lightweight, provably conservative sanitization: trust-threshold and sanitization calibrations are brittle; practical automated calibration methods with bounded false-positive impacts for local agents are needed.  
- Robustness to adaptive attackers at low-resource settings: many defenses are evaluated against static attacks; adaptive attack evaluations especially against sanitization and retrieval-stage defenses on small models are lacking.  
- Persistent infection in offline/self-evolving agents: more work is needed on safe memory-update protocols, auditing, and rollback mechanisms for agents that persist memory locally.  
- Multi-agent infection on local networks: defenses that prevent LLM-to-LLM prompt infections across locally orchestrated agents (e.g., on-device ecosystems) need empirical study and benchmarks.  
- Standardized benchmarks for constrained deployments: current benchmarks (ASB, AgentDojo) focus on capability-scale models and do not provide standardized low-resource scenarios or cost metrics for defense comparison.
