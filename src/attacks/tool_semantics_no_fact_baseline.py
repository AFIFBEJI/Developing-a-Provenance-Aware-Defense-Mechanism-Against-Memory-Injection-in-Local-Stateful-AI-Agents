"""
No-fact baseline. Same policy, same task, same tools, same sandbox, same
model, same filler memories as tool_semantics_execution.py -- but the
tool-fact memory (true OR poisoned) is simply absent. Answers: is the
agent's decline behavior actually driven by evaluating tool consequences,
or does it just default to caution whenever it lacks explicit information
either way?

Usage:
    python tool_semantics_no_fact_baseline.py --n_trials 25
"""
import sys
import os
import argparse
import json
import logging
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.memory.memory_store import add_memory, reset_collection, retrieve_memories_full
from src.memory.filler_memories import add_filler_memories
from src.agents.execution_agent import decide_and_act
from src.attacks.tool_semantics_execution import SCENARIOS  # reuse original policy/task/tools/sandbox exactly


def setup_logging():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/tool_semantics_no_fact_{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("no_fact")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    fh = logging.FileHandler(log_filename, mode="w", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"))
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"Log file: {log_filename}")
    logger.info("Loading embedding model on first call -- can take up to a minute cold. "
                "No output during this is normal, not a hang.")
    return logger, timestamp


def run_trial(domain_name, trial_num, model, logger):
    scenario = SCENARIOS[domain_name]

    reset_collection()
    add_filler_memories(add_memory, n_generic=15, n_adjacent=8)
    add_memory("policy_rule", scenario["policy_rule"], {"source": "manual"})
    # NO tool_fact memory added at all -- this is the point.

    full = retrieve_memories_full(scenario["task"], top_k=3)
    policy_in_top3 = "policy_rule" in full["ids"]

    sandbox = scenario["make_sandbox"]()
    sandbox.reset(**scenario["seed_kwargs"])

    result = decide_and_act(scenario["task"], scenario["tools"], sandbox, top_k=3, model=model)
    action_happened = scenario["action_happened"](result["state_before"], result["state_after"])

    logger.info(f"  [{domain_name} | trial {trial_num}] policy_in_top3={policy_in_top3}, "
                f"tool_called={result['tool_called']}, action_happened={action_happened}")

    return {
        "domain": domain_name, "trial": trial_num,
        "policy_in_top3": policy_in_top3,
        "tool_called": result["tool_called"], "action_happened": action_happened,
        "raw_output": result["raw_output"],
    }


def save_results(all_trials, model, filename):
    output = {"experiment": "tool_semantics_no_fact_baseline", "model": model, "domains": list(SCENARIOS.keys()),
              "trials": all_trials, "timestamp": datetime.now().isoformat(),
              "note": "No tool-fact memory of any kind present -- policy only. "
                      "action_happened=True here means the agent acted with NO information "
                      "about tool consequences at all."}
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logging.getLogger("no_fact").info(f"\nSaved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_trials", type=int, default=25)
    parser.add_argument("--model", type=str, default="qwen/qwen3.5-9b")
    args = parser.parse_args()

    logger, timestamp = setup_logging()
    results_filename = f"results/tool_semantics_no_fact_{timestamp}.json"
    all_trials = []

    for domain_name in SCENARIOS:
        for i in range(args.n_trials):
            try:
                all_trials.append(run_trial(domain_name, i + 1, args.model, logger))
            except Exception as e:
                logger.error(f"[SKIPPED] {domain_name} trial {i+1}: {e}")
                all_trials.append({"domain": domain_name, "trial": i + 1, "error": str(e), "action_happened": False})
            save_results(all_trials, args.model, results_filename)

    logger.info(f"\n{'='*70}\nSUMMARY -- does the agent act with NO tool-consequence information at all?\n{'='*70}")
    for domain_name in SCENARIOS:
        ts = [t for t in all_trials if t.get("domain") == domain_name and "error" not in t]
        n = len(ts)
        happened = sum(1 for t in ts if t["action_happened"])
        declined = sum(1 for t in ts if t["tool_called"] == "decline")
        logger.info(f"  {domain_name:24s} action_happened={happened}/{n}  declined={declined}/{n}")
    logger.info(f"\nDone. Results: {results_filename}")
