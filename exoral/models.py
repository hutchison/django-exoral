from django.db import models
from django.conf import settings
from datetime import date

from fsmedhro_core.models import Studienabschnitt, Studiengang


class Fach(models.Model):
    """
    Ein Fach besteht nur aus dem Namen des Fachs, z.B. Anatomie, Biochemie,
    Physiologie.
    """

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Fach"
        verbose_name_plural = "Fächer"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Dozent(models.Model):
    """
    Nachname, Fach und aktiv sind zwingend erforderlich. Titel und Vorname sind
    optional.

    Ein Dozent ist immer genau einem Fach zugeordnet.
    """

    titel = models.CharField(max_length=30, blank=True)
    vorname = models.CharField(max_length=60, blank=True)
    nachname = models.CharField(max_length=100)
    aktiv = models.BooleanField(default=True)

    fach = models.ForeignKey(Fach, on_delete=models.CASCADE, blank=True)

    class Meta:
        verbose_name = "Dozent"
        verbose_name_plural = "Dozenten"
        ordering = ("nachname",)

    def full_name(self):
        """
        [Titel] [Vorname] [Nachname]
        """
        r = self.nachname

        if self.vorname:
            r = f"{self.vorname} {r}"
        if self.titel:
            r = f"{self.titel} {r}"

        return r

    full_name.short_description = "Name"

    def __str__(self):
        return self.full_name()


class Testat(models.Model):
    """
    Ein Testat hat einen Namen und ist aktiv oder nicht.

    Ein Testat kann verschiedenen Studiengängen zugeordnet werden (z.B. Human-
    und Zahnmedizin).
    Ein Testat kann verschiedenen Studienabschnitten zugeordnet werden (z.B. BP
    Chirurgie im 9. und 10. Semester).
    Ein Testat kann verschiedenen Fächern zugeordnet werden (z.B. das Physikum
    den Fächern Anatomie, Biochemie und Physiologie).
    """

    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)

    fach = models.ManyToManyField(Fach)
    studiengang = models.ManyToManyField(Studiengang)
    studienabschnitt = models.ManyToManyField(Studienabschnitt)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Testat"
        verbose_name_plural = "Testate"
        ordering = ("name",)


class Frage(models.Model):
    datum = models.DateField(default=date.today, verbose_name="Prüfungsdatum")
    text = models.TextField()
    antwort = models.TextField(blank=True)
    punkte = models.PositiveIntegerField(default=1)

    pruefer = models.ForeignKey(
        Dozent,
        on_delete=models.CASCADE,
        verbose_name="PrüferIn",
    )
    testat = models.ForeignKey(
        Testat,
        on_delete=models.CASCADE,
        verbose_name="Testat/Prüfung",
    )
    abgestimmte_benutzer = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
    )

    def __str__(self):
        return self.text[:20].strip()

    class Meta:
        verbose_name = "Frage"
        verbose_name_plural = "Fragen"

    def upvote(self, user):
        if user not in self.abgestimmte_benutzer.all():
            self.abgestimmte_benutzer.add(user)
            self.punkte = models.F("punkte") + 1
            self.save()

    def downvote(self, user):
        if user in self.abgestimmte_benutzer.all():
            self.abgestimmte_benutzer.remove(user)
            self.punkte = models.F("punkte") - 1
            self.save()
