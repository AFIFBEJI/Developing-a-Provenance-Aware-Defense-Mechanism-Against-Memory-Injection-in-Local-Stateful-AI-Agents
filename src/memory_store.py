import chromadb

class MemoryStore:
    def __init__(self, collection_name: str = "agent_memory", persist_path: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_memory(self, memory_id: str, text: str, metadata: dict = None):
        """Ajoute un souvenir dans la mémoire de l'agent."""
        # Chroma exige un dict non-vide ou None — jamais {}
        safe_metadata = metadata if metadata else {"source": "unspecified"}
        self.collection.add(
            ids=[memory_id],
            documents=[text],
            metadatas=[safe_metadata],
        )

    def retrieve_top_k(self, query: str, k: int = 3) -> list[str]:
        """Récupère les k souvenirs les plus pertinents pour une requête."""
        results = self.collection.query(query_texts=[query], n_results=k)
        return results["documents"][0] if results["documents"] else []

    def count(self) -> int:
        return self.collection.count()