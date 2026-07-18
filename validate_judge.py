import csv
import os
from datetime import datetime

from src.qa_agent import QAAgent
from src.attacks.direct_injection import DirectInjectionAttack
from src.judge import judge_response
from data.validation_scenarios import SCENARIOS


def run_validation():
    results = []

    for i, scenario in enumerate(SCENARIOS, start=1):
        print(f"\n{'='*70}")
        print(f"Scénario {i}/{len(SCENARIOS)}: {scenario['id']}")
        print(f"{'='*70}")

        # Nouvelle collection à chaque scénario pour éviter toute contamination croisée
        agent = QAAgent(memory_collection=f"validation_{scenario['id']}")
        agent.remember(f"legit_{scenario['id']}", scenario["legit_fact"])

        attack = DirectInjectionAttack(agent)
        result = attack.run_trial(
            poisoned_fact=scenario["poisoned_fact"],
            trigger_query=scenario["trigger_query"],
            memory_id=f"poison_{scenario['id']}",
        )

        print(f"\nFait empoisonné: {scenario['poisoned_fact']}")
        print(f"Question: {scenario['trigger_query']}")
        print(f"\nRéponse de l'agent:\n{result['response']}")

        # Verdict humain AVANT de révéler celui du juge
        human_verdict = ""
        while human_verdict not in ("S", "F"):
            human_verdict = input("\nTon verdict — Succès (S) ou Échec (F) ? [S/F]: ").strip().upper()
        human_verdict = "SUCCESS" if human_verdict == "S" else "FAILURE"

        judge_verdict = judge_response(scenario["poisoned_fact"], scenario["trigger_query"], result["response"])

        print(f"\n>> Juge automatique: {judge_verdict['verdict']} — {judge_verdict['reason']}")
        print(f">> Toi: {human_verdict}")
        print(">> Accord ✅" if human_verdict == judge_verdict["verdict"] else ">> Désaccord ❌")

        results.append({
            "scenario_id": scenario["id"],
            "was_poison_retrieved": result["was_poison_retrieved"],
            "human_verdict": human_verdict,
            "judge_verdict": judge_verdict["verdict"],
            "judge_reason": judge_verdict["reason"],
            "agreement": human_verdict == judge_verdict["verdict"],
        })

    # Sauvegarde des résultats
    os.makedirs("data", exist_ok=True)
    filename = f"data/judge_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Résumé
    agreements = sum(r["agreement"] for r in results)
    total = len(results)
    print(f"\n{'='*70}")
    print(f"RÉSUMÉ: {agreements}/{total} accords ({agreements/total*100:.1f}%)")
    print(f"Résultats sauvegardés dans: {filename}")
    print(f"{'='*70}")


if __name__ == "__main__":
    run_validation()