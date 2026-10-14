from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone


class VoyageEtude(models.Model):
    theme = models.CharField(max_length=200)
    date = models.DateField()
    lieu = models.CharField(max_length=200)

    class Meta:
        verbose_name = "voyage d'étude"
        verbose_name_plural = "voyages d'étude"

    def __str__(self):
        return f"{self.theme} ({self.date})"


class Encadrant(models.Model):
    # Nom, prénom, e-mail et mot de passe sont gérés par le User de Django
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profil_encadrant",
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Groupe(models.Model):
    MAX_ETUDIANTS = 4

    nom = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    # Association "concerner" : un groupe appartient à un seul voyage
    voyage = models.ForeignKey(
        VoyageEtude, on_delete=models.CASCADE, related_name="groupes"
    )
    # Association "encadrer" : un groupe a un seul encadrant
    encadrant = models.ForeignKey(
        Encadrant, on_delete=models.PROTECT, related_name="groupes"
    )

    def __str__(self):
        return self.nom

    @property
    def statut_rapport(self):
        """'non déposé' tant qu'aucun rapport n'existe, sinon le statut du rapport."""
        rapport = getattr(self, "rapport", None)
        if rapport is None:
            return "non déposé"
        return rapport.get_statut_display().lower()


class Etudiant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profil_etudiant",
    )
    # Association "appartenir" : un étudiant est dans 0 ou 1 groupe
    groupe = models.ForeignKey(
        Groupe,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="etudiants",
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def clean(self):
        # Un groupe contient 4 étudiants au maximum
        if self.groupe_id:
            autres = self.groupe.etudiants.exclude(pk=self.pk).count()
            if autres >= Groupe.MAX_ETUDIANTS:
                raise ValidationError(
                    f"Un groupe ne peut pas dépasser {Groupe.MAX_ETUDIANTS} étudiants."
                )


class Rapport(models.Model):
    class Statut(models.TextChoices):
        DEPOSE = "depose", "Déposé"
        CONSULTE = "consulte", "Consulté"
        EVALUE = "evalue", "Évalué"

    # Association "déposer" : un groupe a 0 ou 1 rapport à la fois
    groupe = models.OneToOneField(
        Groupe, on_delete=models.CASCADE, related_name="rapport"
    )
    fichier_pdf = models.FileField(
        upload_to="rapports/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    statut = models.CharField(
        max_length=10, choices=Statut.choices, default=Statut.DEPOSE
    )
    date_depot = models.DateTimeField(auto_now_add=True)
    date_consultation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Rapport de {self.groupe}"

    @property
    def peut_etre_remplace(self):
        # Remplacement possible seulement tant que l'encadrant ne l'a pas ouvert
        return self.statut == self.Statut.DEPOSE

    def marquer_consulte(self):
        # À appeler quand l'encadrant ouvre ou télécharge le rapport
        if self.statut == self.Statut.DEPOSE:
            self.statut = self.Statut.CONSULTE
            self.date_consultation = timezone.now()
            self.save(update_fields=["statut", "date_consultation"])


class Evaluation(models.Model):
    # Association "évaluer" : un rapport peut avoir plusieurs évaluations (historique)
    rapport = models.ForeignKey(
        Rapport, on_delete=models.CASCADE, related_name="evaluations"
    )
    # Association "rédiger"
    encadrant = models.ForeignKey(
        Encadrant, on_delete=models.PROTECT, related_name="evaluations"
    )
    note = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    observations = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "évaluation"

    def __str__(self):
        return f"{self.rapport} : {self.note}/20"


class PV(models.Model):
    # Association "générer" : une évaluation génère un PV
    evaluation = models.OneToOneField(
        Evaluation, on_delete=models.CASCADE, related_name="pv"
    )
    fichier_pdf = models.FileField(upload_to="pv/")
    date_generation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "PV"
        verbose_name_plural = "PV"

    def __str__(self):
        return f"PV de {self.evaluation.rapport.groupe}"


class Notification(models.Model):
    # Association "notifier"
    destinataire = models.ForeignKey(
        Encadrant, on_delete=models.CASCADE, related_name="notifications"
    )
    # Association "signaler"
    rapport = models.ForeignKey(
        Rapport, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.CharField(max_length=255)
    lue = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.message


from django.db import models

# Create your models here.
