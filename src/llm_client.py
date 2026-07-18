import time
from openai import OpenAI, APITimeoutError, APIConnectionError
from src.config import LM_STUDIO_BASE_URL, LM_STUDIO_API_KEY, MODEL_NAME

# Timeout généreux (en secondes) — le GPU peut être lent sous charge répétée
client = OpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    timeout=180.0,
)

def ask_model(prompt: str, model: str = MODEL_NAME, max_retries: int = 3) -> str:
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except (APITimeoutError, APIConnectionError) as e:
            last_error = e
            wait = 5 * attempt
            print(f"    [retry {attempt}/{max_retries}] timeout/connexion, pause {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Échec après {max_retries} tentatives: {last_error}")