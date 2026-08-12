from src.memory_store import MemoryStore

if __name__ == "__main__":
    store = MemoryStore(collection_name="test_memory")

    store.add_memory("mem_001", "L'utilisateur préfère les réponses en français.")
    store.add_memory("mem_002", "L'utilisateur travaille sur un projet de cybersécurité.")
    store.add_memory("mem_003", "La météo à Tunis est ensoleillée aujourd'hui.")

    print("Nombre de souvenirs stockés:", store.count())

    results = store.retrieve_top_k("Sur quel projet est-ce que je travaille ?", k=2)
    print("Souvenirs les plus pertinents:")
    for r in results:
        print(" -", r)