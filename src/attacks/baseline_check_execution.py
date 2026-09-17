"""
No-attack baseline for the execution agent -- same 3 scenarios as
volume_arm_execution_real.py, but with NO poison at all, just the true
fact. Necessary before trusting the "correctly_declined=0/10 across all 30
poisoned trials" result: without this, there's no way to tell "poisoning
defeated the agent's judgment" apart from "the decline path never gets
chosen regardless of what's in context."

Usage:
    python baseline_check_execution.py --n_trials 10
"""
import sys
import os
import argparse
import json
import logging
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.memory.memory_store import add_memory, reset_collection
from src.memory.filler_memories import add_filler_memories
from src.agents.execution_agent import decide_and_act
from src.attacks.volume_arm_execution_real import DOMAINS


def setup_logging():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/baseline_check_execution_{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("baseline_exec")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    fh = logging.FileHandler(log_filename, mode="w", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"))
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"Log file: {log_filename}")
    return logger, timestamp


def run_trial(domain_name, trial_num, model, logger):
    domain = DOMAINS[domain_name]
    reset_collection()
    add_filler_memories(add_memory, n_generic=15, n_adjacent=8)
    add_memory("true_fact", domain["true_fact"], {"source": "manual"})
    # NO poison added -- this is the point.

    sandbox = domain["make_sandbox"]()
    sandbox.reset(**domain["seed_kwargs"])

    result = decide_and_act(domain["task"], domain["tools"], sandbox, top_k=3, model=model)
    wrong_action_happened = domain["attack_succeeded"](result["state_before"], result["state_after"])

    logger.info(f"  [{domain_name} | trial {trial_num}] tool_called={result['tool_called']}, "
                f"WRONG_ACTION_WITH_NO_ATTACK={wrong_action_happened}")

    return {
        "domain": domain_name, "trial": trial_num,
        "tool_called": result["tool_called"], "args": result["args"],
        "state_before": result["state_before"], "state_after": result["state_after"],
        "wrong_action_happened": wrong_action_happened,
        "raw_output": result["raw_output"],
    }


def save_results(all_trials, model, filename):
    output = {"experiment": "baseline_check_execution", "model": model, "domains": list(DOMAINS.keys()),
              "trials": all_trials, "timestamp": datetime.now().isoformat()}
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logging.getLogger("baseline_exec").info(f"\nSaved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_trials", type=int, default=10)
    parser.add_argument("--model", type=str, default="qwen/qwen3.5-9b")
    args = parser.parse_args()

    logger, timestamp = setup_logging()
    logger.info("Loading embedding model on first call -- can take up to a minute cold, especially right after clearing disk caches. No output during this is normal, not a hang. Watch CPU usage if genuinely worried.")
    results_filename = f"results/baseline_check_execution_{timestamp}.json"
    all_trials = []

    for domain_name in DOMAINS:
        for i in range(args.n_trials):
            try:
                all_trials.append(run_trial(domain_name, i + 1, args.model, logger))
            except Exception as e:
                logger.error(f"[SKIPPED] {domain_name} trial {i+1}: {e}")
                all_trials.append({"domain": domain_name, "trial": i + 1, "error": str(e), "wrong_action_happened": False})
            save_results(all_trials, args.model, results_filename)

    logger.info(f"\n{'='*70}\nSUMMARY -- does the agent correctly decline with NO attack present?\n{'='*70}")
    by_domain = {}
    for t in all_trials:
        if "error" not in t:
            by_domain.setdefault(t["domain"], []).append(t)
    for d, ts in by_domain.items():
        n = len(ts)
        wrong = sum(1 for t in ts if t["wrong_action_happened"])
        declined = sum(1 for t in ts if t["tool_called"] == "decline")
        logger.info(f"  {d:16s} wrong_action_with_no_attack={wrong}/{n}  declined={declined}/{n}")
    logger.info(f"\nDone. Results: {results_filename}")
