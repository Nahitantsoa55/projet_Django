from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import (
    Encadrant,
    Etudiant,
    Evaluation,
    Groupe,
    Notification,
    PV,
    Rapport,
    VoyageEtude,
)


@admin.register(VoyageEtude)
class VoyageEtudeAdmin(admin.ModelAdmin):
    list_display = ("theme", "date", "lieu")


@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ("nom", "voyage", "encadrant", "date_creation")


@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ("groupe", "statut", "date_depot", "date_consultation")
    list_filter = ("statut",)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("rapport", "encadrant", "note", "date")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("destinataire", "message", "lue", "date")


admin.site.register(Encadrant)
admin.site.register(Etudiant)
admin.site.register(PV)
