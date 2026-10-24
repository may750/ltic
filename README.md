# LTIC : plateforme de gestion des stages

LTIC remplace les papiers, e-mails et fichiers Excel utilisés pour gérer les stagiaires dans une entreprise. Tout est centralisé dans un seul site, avec trois rôles et un accès sécurisé selon le rôle.

## Les trois rôles

| Rôle               | Ce qu'il peut faire                                                                                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Stagiaire**      | voir son stage et ses tâches, changer l'état de ses tâches, déposer ses documents, lire les feedbacks, compléter son profil et obtenir des suggestions de projets par IA |
| **Encadrant**      | suivre ses stagiaires, créer des stages et des tâches, lire leurs documents, écrire des feedbacks                                                                        |
| **Administrateur** | voir tous les utilisateurs, stages et documents, consulter les statistiques globales                                                                                     |

## Fonctionnalités

1. Dossiers centralisés et numériques (documents déposés par les stagiaires)
2. Tableau de bord de suivi des tâches avec avancement
3. Statistiques sur les stages (tâches par état, stages par statut)
4. IA qui propose 3 projets selon la spécialité, les compétences, les centres d'intérêt et le CV
5. Feedback de l'encadrant sur les documents
6. Messagerie interne (conversations entre stagiaire, encadrant et administrateur)
7. Notifications automatiques (nouveau stage, tâche, document, feedback, message)

## Technologies

- **Backend** : Python, Django, Django REST Framework (authentification par token)
- **Base de données** : SQLite (développement)
- **Frontend** : React, construit avec Vite
- **IA** : modèle de langage appelé depuis le serveur via l'API Groq (format compatible OpenAI)

## Architecture

```
Navigateur (React)  --->  API Django REST  --->  Base de données SQLite
                              |
                              +--->  Service d'IA (appelé uniquement côté serveur)
```

La clé de l'IA reste dans le fichier `.env` du serveur. Elle n'est jamais envoyée au navigateur.

## Installation

### 1. Backend

```bash
git clone <adresse-du-depot>
cd ltic
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env        # puis ouvrir .env et remplir AI_API_KEY
python manage.py migrate
python manage.py seed_demo  # crée des données de démonstration fictives
python manage.py runserver
```

### 2. Frontend (dans un second terminal)

```bash
cd ltic/frontend
npm install
npm run dev
```

Ouvrir ensuite http://localhost:5173.

## Comptes de démonstration

Créés par `python manage.py seed_demo` (données entièrement fictives). Mot de passe de tous les comptes : `Demo2026!` (à utiliser seulement en local).

| Compte                                | Rôle           |
| ------------------------------------- | -------------- |
| `demo_admin`                          | Administrateur |
| `demo_encadrant1`, `demo_encadrant2`  | Encadrant      |
| `demo_stagiaire1` à `demo_stagiaire4` | Stagiaire      |

Relancer `python manage.py seed_demo` remet la démonstration à zéro.

## API

| Adresse                                                     | Rôle                                                   |
| ----------------------------------------------------------- | ------------------------------------------------------ |
| `POST /api/auth/login/`                                     | Connexion, renvoie un token                            |
| `GET /api/auth/me/`                                         | Informations de la personne connectée                  |
| `GET, PATCH /api/profil/`                                   | Profil du stagiaire (spécialité, compétences, CV)      |
| `GET /api/stagiaires/`                                      | Stagiaires de l'encadrant (tous pour l'administrateur) |
| `GET /api/utilisateurs/`                                    | Tous les utilisateurs (administrateur)                 |
| `/api/stages/`, `/api/taches/`                              | Stages et tâches                                       |
| `/api/documents/`, `/api/feedbacks/`                        | Documents et feedbacks                                 |
| `/api/contacts/`, `/api/messages/`                          | Messagerie                                             |
| `/api/notifications/`, `POST /api/notifications/tout_lire/` | Notifications                                          |
| `GET, POST /api/suggestions/`                               | Voir ou générer les projets suggérés par l'IA          |

## Sécurité

- **Authentification par token** : chaque demande de l'interface porte le token de l'utilisateur.
- **Contrôle d'accès par rôle côté serveur** : les listes sont filtrées selon l'utilisateur (un stagiaire ne voit que ses données, un encadrant que celles de ses stagiaires). Masquer un bouton dans l'interface ne suffit jamais : c'est Django qui refuse (erreur 403).
- **Propriétaire fixé par le serveur** : l'auteur d'un document, d'un feedback ou d'un message est toujours la personne connectée, jamais une valeur envoyée par le client.
- **Fichiers** : seuls les PDF de 5 Mo maximum sont acceptés pour le CV.
- **Secrets** : la clé de l'IA est dans `.env`, ignoré par Git.
- **Données personnelles et IA** : avant l'envoi à l'IA, les e-mails, téléphones, liens et le nom du compte sont masqués. Ce masquage est approximatif : un nom écrit dans le texte d'un CV, sans correspondre au nom du compte, peut passer. Les données de démonstration sont donc fictives.

## Limites connues et améliorations possibles

- Les services d'IA gratuits conviennent au développement et aux démonstrations, pas à une vraie mise en production. Pour des CV réels, il faudrait un service avec garanties de confidentialité, ou un modèle hébergé en interne.
- Le score des suggestions est une estimation du modèle, pas une mesure exacte.
- Un CV scanné (image dans un PDF) n'est pas lu, faute de reconnaissance de texte (OCR).
- La messagerie et les notifications se rafraîchissent toutes les 5 secondes (pas de temps réel avec WebSocket).
- Avant une mise en ligne : nouvelle `SECRET_KEY`, `DEBUG = False`, `ALLOWED_HOSTS`, base PostgreSQL, HTTPS, suppression des comptes de démonstration.
- Pas encore de tests automatisés ni de création de comptes depuis l'interface (elle passe par l'administration Django).
