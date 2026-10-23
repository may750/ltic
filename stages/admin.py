from django.contrib import admin

from .models import Document, Feedback, Message, Notification, Stage, SuggestionProjet, Tache

admin.site.register(Stage)
admin.site.register(Tache)
admin.site.register(Document)
admin.site.register(Feedback)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(SuggestionProjet)
# Register your models here.
