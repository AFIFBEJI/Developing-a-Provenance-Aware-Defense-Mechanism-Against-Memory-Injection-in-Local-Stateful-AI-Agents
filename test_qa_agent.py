from src.qa_agent import QAAgent

if __name__ == "__main__":
    agent = QAAgent(memory_collection="test_qa_agent")

    agent.remember("mem_001", "L'utilisateur s'appelle Maryouma et étudie la cybersécurité.")
    agent.remember("mem_002", "L'utilisateur préfère recevoir des explications en français.")

    result = agent.answer("Comment je m'appelle et qu'est-ce que j'étudie ?")

    print("--- Souvenirs récupérés ---")
    for m in result["retrieved_memories"]:
        print(" -", m)
    print("\n--- Réponse du modèle ---")
    print(result["response"])