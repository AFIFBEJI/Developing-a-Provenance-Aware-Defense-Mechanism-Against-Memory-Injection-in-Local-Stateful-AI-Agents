## TL;DR

Large literature shows quantization both mitigates and introduces security risks: some studies find lower-precision models resist certain fault-injection jailbreaks while others show quantization can enable or preserve malicious behaviors. Multi-agent work documents rapid manipulated-knowledge spread and proposes provenance and topology-based defenses.

----

## Quantization vulnerabilities

This section summarizes empirical studies that directly evaluate how post-training quantization or low-precision deployments affect adversarial robustness, jailbreak susceptibility, or parameter-manipulation attacks. The table below lists papers that measure models and quantization levels and reports their main vulnerability findings and stated limitations.

| Paper | Models tested | Quantization levels studied | Key findings about vulnerability | Open gaps noted by authors |
|---|---:|---|---|---|
| Exploiting LLM Quantization [1] | Multiple LLMs across three attack scenarios (vulnerable code gen, content injection, over-refusal) | Generic PTQ regimes (framework-agnostic analysis) | Quantization can be exploited so a full‑precision model looks benign while its quantized version behaves maliciously after careful construction of constraints and projected optimization [1]. | Practical prevalence on public hubs and defenses for supply‑chain scenarios need more evaluation [1]. |
| On Jailbreaking Quantized Models [2] | Llama-3.2-3B, Phi-4-mini, Llama-3-8B | FP16 baseline; weight-only quantization FP8, INT8, INT4 | Attack success rates (ASR) differ by precision: FP16 attacks reach >80% ASR under small budgets, while FP8 and INT8 show lower ASRs (below ~20% and ~50% respectively at 25 perturbations); INT4 is highly vulnerable in some settings; transferability varies by scheme [2]. | How attack budget, architecture, and quant pipelines interact across more models and deployed toolchains remains underexplored [2]. |
| Quantization-based Jailbreaking Analysis [3] | Llama3-8B-Instruct | 23 quantization levels (detailed per-bit experiments) | Lower-bit quantization degrades reasoning and increases Attack Success Rate; 4-bit appears a practical sweet spot for this model but language/tense differences produce large ASR variance (e.g., Korean +25.5pp, past tense +39.3pp) [3]. | Results are model- and dataset-limited; broader multilingual and task coverage needed [3]. |
| HarmLevelBench on Vicuna 13B [4] | Vicuna-13B-v1.5 | AWQ and GPTQ (common LLM quantizers) | Quantization changes alignment trade-offs: it can improve robustness for some transfer attacks yet increase susceptibility to direct jailbreaking depending on method and prompt complexity [4]. | Mechanisms behind differing transfer vs direct effects require deeper study across quantizers. |
| Model Compression vs Adversarial Robustness [5] | Three code LMs (various sizes) | Pruning, quantization, distillation (compressed variants) | Compressed models often keep nominal accuracy but show significantly reduced robustness under adversarial attacks in code tasks [5]. | Needs new compression methods that preserve adversarial robustness for software tasks [5]. |
| The Impact of Quantization on NLP Robustness [6] | BERT, DistilBERT | Quantized variants (details in paper) | On text-classification benchmarks, quantization increased adversarial accuracy on average (~18.7%) compared to non-quantized baselines in their experiments [6]. | Findings are limited to classifiers and specific attacks; transferability to LLMs and jailbreak scenarios is uncertain [6]. |

Key synthesis points
- Quantization effects are inconsistent: some works report increased robustness under certain attack types and budgets, while others report increased jailbreak or fault‑injection susceptibility depending on bitwidth, attack method, and model family [2] [4] [5] [6].  
- Attack transferability can be asymmetric: jailbreaks on full‑precision models may transfer to some quantized formats but not others, and adversaries can craft full‑precision models that become malicious only after quantization [2] [1].  
- Mitigation approaches that combine quantization-aware fine‑tuning or low‑rank adaptation can recover both accuracy and robustness in specific cybersecurity QA tasks [7] [8].

----

## Multi-agent propagation

This section covers studies that analyze security, trust propagation, and how poisoned or manipulated content spreads through communities of LLM-based agents. The table below compares representative empirical and systems contributions.

| Paper | Multi-agent system or setup | Attack or propagation focus | Key empirical findings | Proposed defenses or mechanisms |
|---|---:|---|---|---|
| Flooding spread of manipulated knowledge [9] | LLM-based multi-agent communities and RAG setups | Persuasiveness Injection + Manipulated Knowledge Injection | Manipulated content can propagate among agents and persist through retrieval‑augmented memories without degrading base capabilities; spreadable counterfactual/toxic knowledge observed in experiments [9]. | Prompt-based verification and supervisory agents reduced spread success rates in experiments [9]. |
| Tipping the Dominos (TOMA) [10] | Three MAS architectures: Magentic-One, LangManus, OWL across five topologies | Topology-aware multi-hop contamination | Multi-hop optimized propagation yields 40–78% attack success across evaluated architectures; topology-aware defenses (topology trust) blocked ~94.8% of adaptive attacks in prototype tests [10]. | Topology trust and topology-aware monitoring recommended; deployment overhead and integration into real systems require more study [10]. |
| BlockA2A trust framework [11] | Enterprise agent ecosystems and Google A2A protocol prototype | Authentication, message integrity, Byzantine agents | Decentralized identifiers, blockchain-anchored ledgers, and a Defense Orchestration Engine reduced prompt/communication-based attack impacts with sub-second overhead in prototypes [11]. | Practical scalability, governance, and cross-domain policy composition need further validation [11]. |
| Layered attack surface survey for LLM agents [12] | Survey across multi-agent pipelines | Multi-agent propagation and trust erosion | A compromised sub-agent or shared memory can propagate malicious content; recommends provenance attestation and fine-grained memory controls [12]. | Calls for standardized provenance and attestation mechanisms across agentic stacks [12]. |

Synthesis and implications
- Manipulated knowledge spreads effectively in LLM agent communities and can survive RAG pipelines unless agents critically verify retrieved content [9].  
- System topology strongly influences spread efficiency; defenses that leverage topology or supervisory roles can substantially reduce propagation in simulation experiments [10] [9].  
- Practical deployments need authenticated message provenance, runtime trust frameworks, and system-level orchestration to contain cross-agent contamination [11] [12].

----

## Provenance and lineage

This section identifies papers that explicitly address provenance tracking, memory attribution, or lineage in AI/ML agent systems and summarizes their scope and suggestions. The table lists works that treat provenance, memory integrity, or lineage mechanisms.

| Paper | Focus on provenance or memory | Main contribution regarding lineage or attribution |
|---|---:|---|
| Layered attack surface survey [12] | Mentions provenance attestation for shared memory | Recommends cryptographic provenance attestation and finer-grained memory controls to limit cross-agent contamination [12]. |
| Survey on long-term memory security [13] | Memory provenance failure analogies | Frames provenance failure in LLM memory systems and recommends research toward mnemonic sovereignty and auditability [13]. |
| Memory poisoning and secure MAS [14] | Provenance structures for databases and memory | Proposes provenance-aware frameworks and mitigation strategies to detect/contain memory poisoning in agent pipelines [14]. |
| Toward Trustworthy Agentic AI [15] | Registry-style provenance concepts | Suggests provenance registries to track trust over agent courses of action and to constrain unsafe content generation [15]. |
| BlockA2A trust framework [11] | Blockchain-anchored immutable auditability | Uses DIDs and ledger anchoring to enable immutable provenance records and accountable agent interactions [11]. |
| Security considerations for MAS [16] | Notes provenance issues in multi-agent chat interfaces | Highlights that obscured provenance increases risk and suggests provenance-aware system design [16]. |

Takeaways
- Multiple recent works advocate cryptographic attestation, immutable ledgers, provenance registries, and fine-grained memory controls as building blocks for attribution and lineage in agentic systems [12] [13] [14] [11] [15] [16].  
- Empirical evaluation of provenance mechanisms at scale, integration with RAG and heterogeneous toolchains, and standardization of provenance metadata remain open research problems across these papers.

----

## Open gaps and recommended next steps

This section synthesizes recurring limitations across the quantization and multi-agent literature and points to areas needing more evidence or engineering work. The opening ties these gaps to findings above and to practical deployment concerns.

Key unresolved issues
- Conflicting empirical outcomes on quantization and robustness across tasks and models make generalization difficult; some classifier studies report robustness gains from quantization while LLM/jailbreak and code-model studies report increased vulnerability or nuanced trade-offs [6] [5] [4] [2].  
- Supply-chain and deployment realities are underexamined: attacks that exploit quantization constraints (e.g., making full‑precision models benign while quantized artifacts are malicious) require end‑to‑end studies across model hubs, toolchains, and consumer quantizers [1].  
- Multi-agent defenses need rigorous standardization: topology-aware or ledger-based solutions show promise in controlled experiments, but real-world integration, governance, and performance trade-offs are still open [10] [11] [9].  
- Provenance mechanisms are recommended repeatedly, but empirical benchmarks, interoperable provenance metadata formats, and secure, low-overhead attestations for RAG and shared memory are not yet mature [12] [13] [14].

Actionable research directions supported by the literature
- Conduct cross-model, cross-quantizer benchmarks that report attack transferability, bit‑flip budgets, and language/task diversity to resolve contradictory quantization findings [2] [3] [4].  
- Prototype supply-chain defenses that validate quantized artifacts before deployment, including tools to detect full‑precision-to-quantized malicious mappings [1].  
- Build and evaluate provenance/attestation prototypes in realistic multi-agent stacks (RAG, shared memory, toolchains), measuring overhead and detection efficacy [11] [12] [9].  
- Advance quantization-aware robustness training (e.g., QLoRA/QLoRA-style fine-tuning) and certify worst‑case behavior under common quantization pipelines [7] [8].
