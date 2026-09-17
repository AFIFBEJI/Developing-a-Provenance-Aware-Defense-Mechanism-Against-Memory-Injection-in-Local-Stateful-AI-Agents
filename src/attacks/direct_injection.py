from src.memory.memory_store import add_memory

def inject_direct(memory_id: str, poisoned_fact: str):
    """Plant an obviously-worded false fact, tagged as attacker-sourced for tracking."""
    add_memory(memory_id, poisoned_fact, {"source": "attacker_direct_injection"})