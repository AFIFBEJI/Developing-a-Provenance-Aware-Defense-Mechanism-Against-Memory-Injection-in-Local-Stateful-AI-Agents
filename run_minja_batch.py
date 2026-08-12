import csv
import os
import time
from datetime import datetime

from src.qa_agent import QAAgent
from src.attacks.minja_attack import MINJAAttack
from src.judge import judge_response
from data.minja_scenarios import MINJA_SCENARIOS

RUNS_PER_SCENARIO = 3


def run_batch():
    results = []
    total_trials = len(MINJA_SCENARIOS) * RUNS_PER_SCENARIO
    trial_num = 0

    for scenario in MINJA_SCENARIOS:
        for run_idx in range(1, RUNS_PER_SCENARIO + 1):
            trial_num += 1
            print(f"[{trial_num}/{total_trials}] {scenario['id']} — run {run_idx}/{RUNS_PER_SCENARIO}")

            collection_name = f"minja_{scenario['id']}_{run_idx}"
            agent = QAAgent(memory_collection=collection_name)
            attack = MINJAAttack(agent)

            try:
                result = attack.run_attack(
                    legit_fact=scenario["legit_fact"],
                    victim_term=scenario["victim_term"],
                    trigger_query=scenario["trigger_query"],
                    indication_steps=scenario["indication_steps"],
                )
                verdict = judge_response(
                    scenario["poisoned_target"], scenario["trigger_query"], result["response"]
                )
                results.append({
                    "scenario_id": scenario["id"],
                    "run_idx": run_idx,
                    "was_poison_retrieved": result["was_poison_retrieved"],
                    "judge_verdict": verdict["verdict"],
                    "judge_reason": verdict["reason"],
                    "response_preview": result["response"][:200].replace("\n", " "),
                })
            except Exception as e:
                print(f"  ERREUR: {e}")
                results.append({
                    "scenario_id": scenario["id"], "run_idx": run_idx,
                    "was_poison_retrieved": None, "judge_verdict": "ERROR",
                    "judge_reason": str(e), "response_preview": "",
                })

            time.sleep(2)

    os.makedirs("data", exist_ok=True)
    filename = f"data/minja_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    valid = [r for r in results if r["judge_verdict"] != "ERROR"]
    total = len(valid)
    retrieved = sum(1 for r in valid if r["was_poison_retrieved"])
    successes = sum(1 for r in valid if r["judge_verdict"] == "SUCCESS")

    print(f"\n{'='*70}")
    print(f"RÉSUMÉ GLOBAL — MINJA-style Attack")
    print(f"{'='*70}")
    print(f"Essais valides: {total}/{len(results)}")
    print(f"ASR-r: {retrieved}/{total} = {retrieved/total*100:.1f}%")
    print(f"ASR: {successes}/{total} = {successes/total*100:.1f}%")

    by_scenario = {}
    for r in valid:
        by_scenario.setdefault(r["scenario_id"], []).append(r)
    for sid, rows in by_scenario.items():
        s = sum(1 for r in rows if r["judge_verdict"] == "SUCCESS")
        print(f"  {sid}: {s}/{len(rows)} succès ({s/len(rows)*100:.0f}%)")

    print(f"\nDétail: {filename}")
    print(f"{'='*70}")


if __name__ == "__main__":
    run_batch()