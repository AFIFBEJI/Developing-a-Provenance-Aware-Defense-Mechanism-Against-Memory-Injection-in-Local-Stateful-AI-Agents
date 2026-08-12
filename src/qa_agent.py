from src.llm_client import ask_model
from src.memory_store import MemoryStore

class QAAgent:
    def __init__(self, memory_collection: str = "agent_memory", k: int = 3):
        self.memory = MemoryStore(collection_name=memory_collection)
        self.k = k

    def _build_prompt(self, query: str, retrieved_memories: list[str]) -> str:
        if retrieved_memories:
            context = "\n".join(f"- {m}" for m in retrieved_memories)
            return (
                f"Voici des souvenirs pertinents de nos échanges précédents:\n{context}\n\n"
                f"Question actuelle: {query}\n"
                f"Réponds en tenant compte de ces souvenirs si pertinent."
            )
        return query

    def answer(self, query: str) -> dict:
        """Exécute un cycle complet: retrieve -> prompt -> generate."""
        retrieved = self.memory.retrieve_top_k(query, k=self.k)
        prompt = self._build_prompt(query, retrieved)
        response = ask_model(prompt)
        return {
            "query": query,
            "retrieved_memories": retrieved,
            "prompt_sent": prompt,
            "response": response,
        }

    def remember(self, memory_id: str, text: str, metadata: dict = None):
        """Écrit un nouveau souvenir (utilisé aussi par les attaques pour injecter du poison)."""
        self.memory.add_memory(memory_id, text, metadata)