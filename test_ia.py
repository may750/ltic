import json
import os
import urllib.request

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

cle = os.getenv("AI_API_KEY")
base_url = os.getenv("AI_BASE_URL")
modele = os.getenv("AI_MODEL")

if not cle or not base_url or not modele:
    raise SystemExit("Il manque AI_API_KEY, AI_BASE_URL ou AI_MODEL dans le fichier .env")

client = OpenAI(api_key=cle, base_url=base_url)

print(f"Modèle testé : {modele}")
try:
    reponse = client.chat.completions.create(
        model=modele,
        messages=[{"role": "user", "content": "Dis bonjour en une phrase, en français."}],
        max_tokens=500,
    )
    print("Réponse :", reponse.choices[0].message.content)
except Exception as erreur:
    print("Erreur :", erreur)
    # Si on utilise GitHub Models, on affiche les modèles disponibles
    if "github" in base_url:
        try:
            demande = urllib.request.Request(
                "https://models.github.ai/catalog/models",
                headers={
                    "Authorization": f"Bearer {cle}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            with urllib.request.urlopen(demande) as r:
                print("\nModèles disponibles :")
                for m in json.load(r):
                    print(" -", m["id"])
        except Exception as e2:
            print("Impossible de lister les modèles :", e2)