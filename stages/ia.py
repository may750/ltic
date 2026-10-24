import json
import re

from django.conf import settings
from django.db import transaction
from openai import OpenAI
from pypdf import PdfReader

from .models import SuggestionProjet


class ProfilIncomplet(Exception):
    """Le stagiaire n'a rien rempli que l'IA puisse utiliser."""


class IAError(Exception):
    """Un problème avec le service d'IA (message lisible pour l'utilisateur)."""


CONSIGNE = """Tu es un conseiller de stage bienveillant et précis, dans une plateforme universitaire.
À partir du profil d'un stagiaire, propose exactement 3 projets de stage réalistes, concrets et réalisables en quelques semaines ou quelques mois.

Règles :
- Les projets doivent correspondre à sa spécialité, ses compétences et ses centres d'intérêt, tout en lui permettant d'apprendre au moins une nouvelle compétence.
- Varie la difficulté : un projet accessible, un projet intermédiaire, un projet ambitieux.
- N'invente aucune information sur la personne.
- Réponds en français.
- Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte avant ou après, de cette forme :
{"suggestions": [{"titre": "...", "description": "2 à 3 phrases", "competences_cibles": ["...", "..."], "score": 85, "explication": "1 à 2 phrases : pourquoi ce projet convient à ce profil"}]}
Le score est un entier de 0 à 100 : l'adéquation entre le projet et le profil."""

MOTIF_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MOTIF_LIEN = re.compile(r"(https?://|www\.)\S+")
MOTIF_TEL = re.compile(r"(?<!\d)\+?\d[\d ().-]{6,}\d(?!\d)")
MOTIF_ANNEES = re.compile(r"\s*(19|20)\d{2}\s*[-–/]\s*(19|20)\d{2}\s*")


def _masquer_telephone(correspondance):
    texte = correspondance.group(0)
    chiffres = re.sub(r"\D", "", texte)
    if len(chiffres) >= 8 and not MOTIF_ANNEES.fullmatch(texte):
        return "[téléphone]"
    return texte


def anonymiser(texte, utilisateur):
    """Masque les données personnelles avant l'envoi à l'IA."""
    texte = MOTIF_EMAIL.sub("[e-mail]", texte)
    texte = MOTIF_LIEN.sub("[lien]", texte)
    texte = MOTIF_TEL.sub(_masquer_telephone, texte)
    for mot in (utilisateur.first_name, utilisateur.last_name, utilisateur.username):
        if mot and len(mot) > 2:
            texte = re.sub(re.escape(mot), "[nom]", texte, flags=re.IGNORECASE)
    return texte


def lire_cv(utilisateur):
    """Extrait le texte des 3 premières pages du CV, anonymisé et raccourci."""
    if not utilisateur.cv:
        return ""
    try:
        lecteur = PdfReader(utilisateur.cv.path)
        texte = " ".join((page.extract_text() or "") for page in lecteur.pages[:3])
    except Exception:
        return ""
    texte = re.sub(r"\s+", " ", texte).strip()
    return anonymiser(texte, utilisateur)[:3000]


def construire_profil(utilisateur):
    lignes = []
    if utilisateur.specialite:
        lignes.append(f"Spécialité : {utilisateur.specialite}")
    if utilisateur.competences:
        lignes.append(f"Compétences : {utilisateur.competences}")
    if utilisateur.centres_interet:
        lignes.append(f"Centres d'intérêt : {utilisateur.centres_interet}")
    cv = lire_cv(utilisateur)
    if cv:
        lignes.append(f"Extrait du CV : {cv}")
    return "\n".join(lignes)


def appeler_ia(profil):
    if not (settings.AI_API_KEY and settings.AI_BASE_URL and settings.AI_MODEL):
        raise IAError("L'IA n'est pas configurée sur le serveur.")
    client = OpenAI(
        api_key=settings.AI_API_KEY,
        base_url=settings.AI_BASE_URL,
        timeout=45,
        max_retries=1,
    )
    try:
        reponse = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": CONSIGNE},
                {"role": "user", "content": profil},
            ],
            temperature=0.7,
            max_tokens=3000,
        )
    except Exception as erreur:
        raise IAError("Le service d'IA ne répond pas pour le moment. Réessayez dans un instant.") from erreur
    return reponse.choices[0].message.content or ""


def extraire_json(texte):
    texte = re.sub(r"```(?:json)?", "", texte)
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut == -1 or fin == -1:
        raise IAError("La réponse de l'IA est illisible. Réessayez.")
    try:
        donnees = json.loads(texte[debut : fin + 1])
    except json.JSONDecodeError as erreur:
        raise IAError("La réponse de l'IA est illisible. Réessayez.") from erreur
    if not isinstance(donnees, dict):
        raise IAError("La réponse de l'IA est illisible. Réessayez.")
    return donnees


def nettoyer(donnees):
    """Vérifie et nettoie les suggestions reçues de l'IA."""
    resultats = []
    liste = donnees.get("suggestions", [])
    if not isinstance(liste, list):
        liste = []
    for element in liste[:3]:
        if not isinstance(element, dict):
            continue
        titre = str(element.get("titre", "")).strip()[:200]
        description = str(element.get("description", "")).strip()
        if not titre or not description:
            continue
        competences = element.get("competences_cibles", [])
        if isinstance(competences, list):
            competences = ", ".join(str(c).strip() for c in competences)
        try:
            score = max(0.0, min(100.0, float(element.get("score", 0))))
        except (TypeError, ValueError):
            score = 0.0
        resultats.append(
            {
                "titre": titre,
                "description": description,
                "competences_cibles": str(competences)[:300],
                "score": score,
                "explication": str(element.get("explication", "")).strip(),
            }
        )
    if not resultats:
        raise IAError("L'IA n'a pas proposé de projet exploitable. Réessayez.")
    return resultats


def generer_suggestions(utilisateur):
    """Génère 3 projets pour ce stagiaire et remplace les anciennes suggestions."""
    profil = construire_profil(utilisateur)
    if not profil:
        raise ProfilIncomplet("Complétez votre profil (spécialité, compétences ou CV) avant de générer des suggestions.")
    resultats = nettoyer(extraire_json(appeler_ia(profil)))
    with transaction.atomic():
        SuggestionProjet.objects.filter(stagiaire=utilisateur).delete()
        return [SuggestionProjet.objects.create(stagiaire=utilisateur, **r) for r in resultats]