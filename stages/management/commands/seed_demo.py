import datetime

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from stages.models import Document, Feedback, Message, Stage, Tache
from users.models import User

MOT_DE_PASSE = "Demo2026!"
PREFIXE = "demo_"

TERMINEE = Tache.Etat.TERMINEE
EN_COURS = Tache.Etat.EN_COURS
A_FAIRE = Tache.Etat.A_FAIRE

ENCADRANTS = [
    ("demo_encadrant1", "Nadia", "Développement logiciel"),
    ("demo_encadrant2", "Marwen", "Réseaux et sécurité"),
]

# Chaque stagiaire : profil, stage, tâches (titre, état, échéance en jours), document, feedback
STAGIAIRES = [
    {
        "username": "demo_stagiaire1",
        "prenom": "Lina",
        "encadrant": "demo_encadrant1",
        "specialite": "Génie logiciel",
        "competences": "Python, Django, React, Git",
        "interets": "Développement web, interfaces utilisateur",
        "sujet": "Plateforme web de gestion de stocks",
        "statut": Stage.Statut.EN_COURS,
        "debut": -21,
        "fin": 60,
        "taches": [
            ("Analyser les besoins", TERMINEE, -10),
            ("Concevoir la base de données", TERMINEE, -3),
            ("Développer l'API", EN_COURS, 12),
            ("Rédiger la documentation", A_FAIRE, 40),
        ],
        "document": "Rapport intermédiaire",
        "feedback": "Bon travail. Ajoutez un schéma de la base de données et détaillez les tests.",
    },
    {
        "username": "demo_stagiaire2",
        "prenom": "Omar",
        "encadrant": "demo_encadrant1",
        "specialite": "Science des données",
        "competences": "Python, SQL, pandas",
        "interets": "Analyse de données, visualisation",
        "sujet": "Tableau de bord d'analyse des ventes",
        "statut": Stage.Statut.EN_COURS,
        "debut": -14,
        "fin": 75,
        "taches": [
            ("Nettoyer le jeu de données", TERMINEE, -5),
            ("Créer les premiers graphiques", EN_COURS, 7),
            ("Présenter les résultats", A_FAIRE, 30),
        ],
        "document": "Cahier des charges",
        "feedback": None,
    },
    {
        "username": "demo_stagiaire3",
        "prenom": "Salma",
        "encadrant": "demo_encadrant2",
        "specialite": "Réseaux et télécommunications",
        "competences": "Linux, TCP/IP, Wireshark",
        "interets": "Cybersécurité, supervision réseau",
        "sujet": "Supervision et détection d'incidents réseau",
        "statut": Stage.Statut.EN_COURS,
        "debut": -30,
        "fin": 45,
        "taches": [
            ("Installer l'environnement de test", TERMINEE, -20),
            ("Capturer et analyser le trafic", TERMINEE, -8),
            ("Écrire les règles de détection", EN_COURS, 10),
            ("Rédiger le rapport final", A_FAIRE, 35),
        ],
        "document": "Plan de test réseau",
        "feedback": "Plan clair. Pensez à préciser les critères de réussite de chaque test.",
    },
    {
        "username": "demo_stagiaire4",
        "prenom": "Yassine",
        "encadrant": "demo_encadrant2",
        "specialite": "Systèmes embarqués",
        "competences": "C, Arduino, MQTT",
        "interets": "Objets connectés, électronique",
        "sujet": "Capteurs connectés pour bâtiment intelligent",
        "statut": Stage.Statut.EN_ATTENTE,
        "debut": 7,
        "fin": 90,
        "taches": [
            ("Choisir les capteurs", A_FAIRE, 14),
            ("Monter le prototype", A_FAIRE, 45),
        ],
        "document": None,
        "feedback": None,
    },
]


class Command(BaseCommand):
    help = "Crée (ou remet à zéro) des données de démonstration fictives."

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. On efface seulement les anciens comptes de démonstration
        User.objects.filter(username__startswith=PREFIXE).delete()
        aujourdhui = datetime.date.today()

        # 2. Administrateur
        User.objects.create_user(
            username="demo_admin",
            password=MOT_DE_PASSE,
            first_name="Admin",
            last_name="Demo",
            email="demo_admin@exemple.invalid",
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        # 3. Encadrants
        encadrants = {}
        for username, prenom, service in ENCADRANTS:
            encadrants[username] = User.objects.create_user(
                username=username,
                password=MOT_DE_PASSE,
                first_name=prenom,
                last_name="Demo",
                email=f"{username}@exemple.invalid",
                role=User.Role.ENCADRANT,
                service=service,
            )

        # 4. Stagiaires, avec leur stage, leurs tâches, documents, feedbacks et messages
        for d in STAGIAIRES:
            encadrant = encadrants[d["encadrant"]]
            stagiaire = User.objects.create_user(
                username=d["username"],
                password=MOT_DE_PASSE,
                first_name=d["prenom"],
                last_name="Demo",
                email=f"{d['username']}@exemple.invalid",
                role=User.Role.STAGIAIRE,
                encadrant=encadrant,
                specialite=d["specialite"],
                competences=d["competences"],
                centres_interet=d["interets"],
            )
            stage = Stage.objects.create(
                stagiaire=stagiaire,
                sujet=d["sujet"],
                date_debut=aujourdhui + datetime.timedelta(days=d["debut"]),
                date_fin=aujourdhui + datetime.timedelta(days=d["fin"]),
                statut=d["statut"],
            )
            for titre, etat, jours in d["taches"]:
                Tache.objects.create(
                    stage=stage,
                    titre=titre,
                    etat=etat,
                    echeance=aujourdhui + datetime.timedelta(days=jours),
                )
            if d["document"]:
                document = Document.objects.create(
                    stagiaire=stagiaire,
                    nom=d["document"],
                    fichier=ContentFile(
                        "Document fictif de démonstration.\n".encode("utf-8"),
                        name="document_demo.txt",
                    ),
                )
                if d["feedback"]:
                    Feedback.objects.create(
                        document=document,
                        encadrant=encadrant,
                        commentaire=d["feedback"],
                    )
            Message.objects.create(
                expediteur=encadrant,
                destinataire=stagiaire,
                contenu="Bonjour ! N'hésitez pas à me poser vos questions sur le projet.",
            )
            Message.objects.create(
                expediteur=stagiaire,
                destinataire=encadrant,
                contenu="Merci, je commence par la première tâche.",
            )

        self.stdout.write(self.style.SUCCESS("Données de démonstration créées."))
        self.stdout.write(f"Mot de passe de tous les comptes : {MOT_DE_PASSE}")
        for u in User.objects.filter(username__startswith=PREFIXE).order_by("username"):
            self.stdout.write(f" - {u.username} ({u.role})")