from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Document, Feedback, Message, Notification, Stage, Tache


def notifier(utilisateur, contenu):
    """Crée une notification (si la personne existe)."""
    if utilisateur is not None:
        Notification.objects.create(utilisateur=utilisateur, contenu=contenu[:255])


@receiver(post_save, sender=Stage)
def stage_cree(sender, instance, created, **kwargs):
    if created:
        notifier(instance.stagiaire, f"Nouveau stage : {instance.sujet}")


@receiver(post_save, sender=Tache)
def tache_creee(sender, instance, created, **kwargs):
    if created:
        notifier(instance.stage.stagiaire, f"Nouvelle tâche : {instance.titre}")


@receiver(post_save, sender=Document)
def document_depose(sender, instance, created, **kwargs):
    if created:
        notifier(
            instance.stagiaire.encadrant,
            f"{instance.stagiaire.username} a déposé : {instance.nom}",
        )


@receiver(post_save, sender=Feedback)
def feedback_donne(sender, instance, created, **kwargs):
    if created:
        notifier(
            instance.document.stagiaire,
            f"Nouveau feedback de {instance.encadrant.username} sur {instance.document.nom}",
        )


@receiver(post_save, sender=Message)
def message_recu(sender, instance, created, **kwargs):
    if created:
        notifier(instance.destinataire, f"Nouveau message de {instance.expediteur.username}")