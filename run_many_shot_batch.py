import csv
import os
import time
from datetime import datetime

from src.qa_agent import QAAgent
from src.attacks.many_shot_attack import ManyShotAttack
from src.judge import judge_response
from data.many_shot_scenarios import MANY_SHOT_SCENARIOS, SHOT_LEVELS

RUNS_PER_CELL = 2  # répétitions par combinaison (thème x nombre de shots)


def run_batch():
    results = []
    total = len(MANY_SHOT_SCENARIOS) * len(SHOT_LEVELS) * RUNS_PER_CELL
    trial_num = 0

    for scenario in MANY_SHOT_SCENARIOS:
        for n_shots in SHOT_LEVELS:
            for run_idx in range(1, RUNS_PER_CELL + 1):
                trial_num += 1
                print(f"[{trial_num}/{total}] {scenario['id']} — {n_shots} shots — run {run_idx}/{RUNS_PER_CELL}")

                collection_name = f"manyshot_{scenario['id']}_{n_shots}_{run_idx}"
                agent = QAAgent(memory_collection=collection_name)
                attack = ManyShotAttack(agent)

                try:
                    result = attack.run_trial(
                        legit_fact=scenario["legit_fact"],
                        poisoned_fact=scenario["poisoned_fact"],
                        trigger_query=scenario["trigger_query"],
                        n_shots=n_shots,
                    )
                    verdict = judge_response(scenario["poisoned_fact"], scenario["trigger_query"], result["response"])

                    results.append({
                        "scenario_id": scenario["id"],
                        "n_shots": n_shots,
                        "run_idx": run_idx,
                        "poisoned_in_topk": result["poisoned_in_topk"],
                        "topk_size": result["topk_size"],
                        "was_poison_retrieved": result["was_poison_retrieved"],
                        "judge_verdict": verdict["verdict"],
                        "judge_reason": verdict["reason"],
                    })
                except Exception as e:
                    print(f"  ERREUR: {e}")
                    results.append({
                        "scenario_id": scenario["id"], "n_shots": n_shots, "run_idx": run_idx,
                        "poisoned_in_topk": None, "topk_size": None, "was_poison_retrieved": None,
                        "judge_verdict": "ERROR", "judge_reason": str(e),
                    })

                time.sleep(2)

    os.makedirs("data", exist_ok=True)
    filename = f"data/many_shot_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n{'='*70}")
    print("RÉSUMÉ GLOBAL — Many-Shot Memory Jailbreak")
    print(f"{'='*70}")
    valid = [r for r in results if r["judge_verdict"] != "ERROR"]

    for scenario in MANY_SHOT_SCENARIOS:
        print(f"\n{scenario['id']}:")
        for n_shots in SHOT_LEVELS:
            rows = [r for r in valid if r["scenario_id"] == scenario["id"] and r["n_shots"] == n_shots]
            if not rows:
                continue
            successes = sum(1 for r in rows if r["judge_verdict"] == "SUCCESS")
            avg_poisoned_topk = sum(r["poisoned_in_topk"] for r in rows) / len(rows)
            print(f"  {n_shots} shots: ASR = {successes}/{len(rows)} ({successes/len(rows)*100:.0f}%), "
                  f"submersion moyenne = {avg_poisoned_topk:.1f}/{rows[0]['topk_size']}")

    print(f"\nDétail: {filename}")
    print(f"{'='*70}")


if __name__ == "__main__":
    run_batch()