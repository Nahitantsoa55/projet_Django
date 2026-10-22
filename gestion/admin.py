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
from .services import notifier_reaffectation_rapport


admin.site.site_header = "Rapports"
admin.site.site_title = "Rapports"


@admin.register(VoyageEtude)
class VoyageEtudeAdmin(admin.ModelAdmin):
    list_display = ("theme", "date", "lieu")


@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ("nom", "voyage", "encadrant", "createur", "date_creation")
    readonly_fields = ("createur",)

    def save_model(self, request, obj, form, change):
        ancien_encadrant_id = None
        if change:
            ancien_encadrant_id = Groupe.objects.only("encadrant_id").get(
                pk=obj.pk
            ).encadrant_id
        super().save_model(request, obj, form, change)
        if change:
            notifier_reaffectation_rapport(obj, ancien_encadrant_id)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "encadrant":
            kwargs["queryset"] = Encadrant.objects.filter(user__is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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


admin.site.register(Etudiant)
admin.site.register(PV)


@admin.action(description="Valider les comptes encadrants sélectionnés")
def valider_encadrants(modeladmin, request, queryset):
    for encadrant in queryset.select_related("user"):
        if not encadrant.user.is_active:
            encadrant.user.is_active = True
            encadrant.user.save(update_fields=["is_active"])


@admin.register(Encadrant)
class EncadrantAdmin(admin.ModelAdmin):
    list_display = ("user", "compte_actif")
    actions = (valider_encadrants,)

    @admin.display(boolean=True, description="Compte validé")
    def compte_actif(self, obj):
        return obj.user.is_active
