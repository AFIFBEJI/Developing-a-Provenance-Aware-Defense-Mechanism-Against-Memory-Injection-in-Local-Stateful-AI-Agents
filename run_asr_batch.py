import csv
import os
import time
from datetime import datetime

from src.qa_agent import QAAgent
from src.attacks.direct_injection import DirectInjectionAttack
from src.judge import judge_response
from data.validation_scenarios import SCENARIOS

RUNS_PER_SCENARIO = 5


def run_batch():
    results = []
    total_trials = len(SCENARIOS) * RUNS_PER_SCENARIO
    trial_num = 0

    for scenario in SCENARIOS:
        for run_idx in range(1, RUNS_PER_SCENARIO + 1):
            trial_num += 1
            print(f"[{trial_num}/{total_trials}] {scenario['id']} — run {run_idx}/{RUNS_PER_SCENARIO}")

            # Collection unique par run pour éviter toute contamination entre essais
            collection_name = f"batch_{scenario['id']}_{run_idx}"
            agent = QAAgent(memory_collection=collection_name)
            agent.remember(f"legit_{scenario['id']}", scenario["legit_fact"])

            attack = DirectInjectionAttack(agent)
            try:
                result = attack.run_trial(
                    poisoned_fact=scenario["poisoned_fact"],
                    trigger_query=scenario["trigger_query"],
                    memory_id=f"poison_{scenario['id']}_{run_idx}",
                )
                verdict = judge_response(
                    scenario["poisoned_fact"], scenario["trigger_query"], result["response"]
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
                print(f"  ERREUR sur cet essai: {e}")
                results.append({
                    "scenario_id": scenario["id"],
                    "run_idx": run_idx,
                    "was_poison_retrieved": None,
                    "judge_verdict": "ERROR",
                    "judge_reason": str(e),
                    "response_preview": "",
                })

            time.sleep(2)  # petite pause, évite de saturer LM Studio en rafale

    # Sauvegarde brute
    os.makedirs("data", exist_ok=True)
    raw_filename = f"data/asr_batch_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(raw_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print_summary(results, raw_filename)


def print_summary(results, raw_filename):
    valid = [r for r in results if r["judge_verdict"] != "ERROR"]
    total = len(valid)
    retrieved = sum(1 for r in valid if r["was_poison_retrieved"])
    successes = sum(1 for r in valid if r["judge_verdict"] == "SUCCESS")

    print(f"\n{'='*70}")
    print(f"RÉSUMÉ GLOBAL — Direct Injection Attack")
    print(f"{'='*70}")
    print(f"Essais valides: {total}/{len(results)}")
    print(f"ASR-r (poison récupéré): {retrieved}/{total} = {retrieved/total*100:.1f}%")
    print(f"ASR (succès selon le juge): {successes}/{total} = {successes/total*100:.1f}%")

    print(f"\n--- Détail par scénario ---")
    by_scenario = {}
    for r in valid:
        by_scenario.setdefault(r["scenario_id"], []).append(r)

    scenario_rows = []
    for sid, rows in by_scenario.items():
        n = len(rows)
        s = sum(1 for r in rows if r["judge_verdict"] == "SUCCESS")
        print(f"  {sid}: {s}/{n} succès ({s/n*100:.0f}%)")
        scenario_rows.append({"scenario_id": sid, "successes": s, "total": n, "asr_pct": round(s/n*100, 1)})

    summary_filename = raw_filename.replace("_raw_", "_summary_")
    with open(summary_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["scenario_id", "successes", "total", "asr_pct"])
        writer.writeheader()
        writer.writerows(scenario_rows)

    print(f"\nDétail brut: {raw_filename}")
    print(f"Résumé par scénario: {summary_filename}")
    print(f"{'='*70}")


if __name__ == "__main__":
    run_batch()