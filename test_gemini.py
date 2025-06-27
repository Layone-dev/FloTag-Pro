import os
from dotenv import load_dotenv

load_dotenv()

print("=== Test des clés API ===")
print(f"GEMINI_API_KEY présente : {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}")
print(f"OPENAI_API_KEY présente : {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
print(f"Longueur clé Gemini : {len(os.getenv('GEMINI_API_KEY', ''))}")
