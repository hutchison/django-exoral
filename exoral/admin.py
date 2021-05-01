from django.contrib import admin
from .models import (
    Fach,
    Dozent,
    Testat,
    Frage,
)

class FachAdmin(admin.ModelAdmin):
    model = Fach
    list_display = ('name', 'admin_list_dozent')

admin.site.register(Fach, FachAdmin)

class DozentAdmin(admin.ModelAdmin):
    model = Dozent
    list_display = ('full_name', 'aktiv', 'fach')
    search_fields = ['vorname', 'nachname', 'fach__name']


admin.site.register(Dozent, DozentAdmin)


class TestatAdmin(admin.ModelAdmin):
    model = Testat
    list_display = (
        'name',
        'active',
        'admin_list_fach',
        'admin_list_studienabschnitt',
        'admin_list_studiengang',
    )
    filter_horizontal = ('fach', 'studiengang', 'studienabschnitt')
    search_fields = ['name']


admin.site.register(Testat, TestatAdmin)


class FrageAdmin(admin.ModelAdmin):
    model = Frage
    list_display = ('__str__', 'testat', 'pruefer', 'punkte', 'datum')
    filter_horizontal = ('abgestimmte_benutzer',)
    search_fields = [
        'text',
        'testat__name',
        'pruefer__nachname',
        'pruefer__fach__name',
    ]


admin.site.register(Frage, FrageAdmin)
