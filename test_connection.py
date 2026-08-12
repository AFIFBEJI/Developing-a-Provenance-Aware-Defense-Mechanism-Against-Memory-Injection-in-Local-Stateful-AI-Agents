from src.llm_client import client
from src.config import MODEL_NAME

if __name__ == "__main__":
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Réponds juste par: OK"}],
        )
        print("Réponse complète:", response)
    except Exception as e:
        print("ERREUR:", type(e).__name__, "-", e)