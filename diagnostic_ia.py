import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()

cle = os.getenv("AI_API_KEY") or ""
base = os.getenv("AI_BASE_URL") or ""
modele = os.getenv("AI_MODEL") or ""

print("Adresse :", repr(base))
print("Modèle  :", repr(modele))
print("Jeton   : commence par", cle[:11], "| longueur", len(cle))

url = base.rstrip("/") + "/chat/completions"
corps = json.dumps(
    {
        "model": modele,
        "messages": [{"role": "user", "content": "Dis bonjour."}],
        "max_tokens": 30,
    }
).encode()

demande = urllib.request.Request(
    url,
    data=corps,
    headers={
        "Authorization": f"Bearer {cle}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
)

try:
    with urllib.request.urlopen(demande, timeout=30) as reponse:
        print("Statut  :", reponse.status)
        print("Type    :", reponse.headers.get("Content-Type"))
        print("Début   :", reponse.read().decode("utf-8", "replace")[:400])
except urllib.error.HTTPError as erreur:
    print("Statut  :", erreur.code)
    print("Début   :", erreur.read().decode("utf-8", "replace")[:400])
except Exception as erreur:
    print("Erreur réseau :", erreur)