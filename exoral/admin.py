from django.contrib import admin
from .models import (
    Fach,
    Dozent,
    Testat,
    Frage,
)

admin.site.register(Fach)

class DozentAdmin(admin.ModelAdmin):
    model = Dozent
    list_display = ('full_name', 'aktiv', 'fach')


admin.site.register(Dozent, DozentAdmin)


class TestatAdmin(admin.ModelAdmin):
    model = Testat
    filter_horizontal = ('fach', 'studiengang', 'studienabschnitt')


admin.site.register(Testat, TestatAdmin)


class FrageAdmin(admin.ModelAdmin):
    model = Frage
    list_display = ('__str__', 'testat', 'pruefer', 'punkte', 'datum')
    filter_horizontal = ('abgestimmte_benutzer',)


admin.site.register(Frage, FrageAdmin)
