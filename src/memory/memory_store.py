import chromadb
from chromadb.utils import embedding_functions
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "chroma_db")

# Pinned explicitly (rather than relying on the implicit default) for
# reproducibility. This IS the same model/function Chroma uses by default
# (ONNX runtime, bundled — no extra dependency like sentence-transformers/
# torch needed), just referenced by name instead of left implicit.
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
_embedding_fn = embedding_functions.DefaultEmbeddingFunction()

COLLECTION_NAME = "agent_memory"

client = chromadb.PersistentClient(path=DB_PATH)
# Chroma defaults to L2 distance; sentence-transformer embeddings (like
# all-MiniLM-L6-v2) are meant to be compared with cosine similarity. Pinning
# this explicitly so ISR "distance" values are interpretable and comparable
# across runs/models, rather than silently depending on Chroma's default.
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_embedding_fn,
    metadata={"hnsw:space": "cosine"},
)


def add_memory(memory_id: str, text: str, metadata: dict = None):
    # upsert instead of add: reruns without an explicit reset_collection() call
    # no longer crash on duplicate ids.
    collection.upsert(
        ids=[memory_id],
        documents=[text],
        metadatas=[metadata if metadata else {"source": "manual"}]
    )


def retrieve_memories(query: str, top_k: int = 3):
    """Back-compat: returns just the memory text, as before.
    Prefer retrieve_memories_full() for anything that needs to compute ISR
    (was the poisoned memory actually retrieved, and at what rank/distance)."""
    return retrieve_memories_full(query, top_k=top_k)["documents"]


def retrieve_memories_full(query: str, top_k: int = 3):
    """Returns ids, documents, metadatas, and distances for the top_k results,
    so callers can check whether a specific memory_id was retrieved and at
    what rank/similarity. This is required for Injection Success Rate (ISR)."""
    results = collection.query(query_texts=[query], n_results=top_k)
    return {
        "ids": results["ids"][0],
        "documents": results["documents"][0],
        "metadatas": results["metadatas"][0],
        "distances": results["distances"][0],
    }


def was_retrieved(memory_id: str, query: str, top_k: int = 3):
    """Convenience for ISR checks: did `memory_id` show up in the top_k
    results for `query`, and if so at what rank (0-indexed) and distance?"""
    full = retrieve_memories_full(query, top_k=top_k)
    if memory_id in full["ids"]:
        rank = full["ids"].index(memory_id)
        return {"retrieved": True, "rank": rank, "distance": full["distances"][rank]}
    return {"retrieved": False, "rank": None, "distance": None}


def reset_collection():
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass  # collection may not exist yet on a fresh DB path
    global collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )


if __name__ == "__main__":
    reset_collection()
    add_memory("mem1", "The user's favorite programming language is Python.")
    add_memory("mem2", "The user is allergic to peanuts.")
    add_memory("mem3", "The user's dog is named Max, a golden retriever.")

    query = "What is the user allergic to?"
    result = retrieve_memories_full(query, top_k=2)
    print(f"Query: {query}")
    print("Retrieved memories:")
    for mem_id, doc, dist in zip(result["ids"], result["documents"], result["distances"]):
        print(f" - [{mem_id}] (distance={dist:.4f}) {doc}")

    print("\nISR check example:")
    print(was_retrieved("mem2", query, top_k=2))