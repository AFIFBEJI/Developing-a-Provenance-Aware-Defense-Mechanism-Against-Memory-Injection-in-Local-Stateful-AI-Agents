from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print("Clé trouvée:", "OUI" if key else "NON")
print("Longueur:", len(key) if key else 0)