from src.qa_agent import QAAgent

class DirectInjectionAttack:
    """
    Attaque la plus simple : injecte directement un souvenir malveillant
    dans la mémoire de l'agent, en le faisant passer pour un fait légitime.
    """

    def __init__(self, agent: QAAgent):
        self.agent = agent

    def inject(self, memory_id: str, poisoned_fact: str, disguise_metadata: dict = None):
        """Écrit le souvenir empoisonné comme s'il venait d'une source fiable."""
        metadata = disguise_metadata or {"source": "user", "poisoned": True}
        self.agent.remember(memory_id, poisoned_fact, metadata)

    def run_trial(self, poisoned_fact: str, trigger_query: str, memory_id: str = "poison_001") -> dict:
        """Injecte puis interroge l'agent, retourne tout pour analyse."""
        self.inject(memory_id, poisoned_fact)
        result = self.agent.answer(trigger_query)
        result["poisoned_fact"] = poisoned_fact
        result["was_poison_retrieved"] = poisoned_fact in result["retrieved_memories"]
        return result
    