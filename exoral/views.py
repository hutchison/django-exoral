from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from .models import (
    Dozent,
    Frage,
    Testat,
)

from fsmedhro_core.models import (
    FachschaftUser,
    Studienabschnitt,
    Studiengang,
)


class Home(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        name = user.username
        if user.first_name:
            name = user.first_name

        context = {
            'name': name,
        }

        try:
            fs_user = FachschaftUser.objects.get(user=request.user)
            studiengang = fs_user.studiengang
            studienabschnitt = fs_user.studienabschnitt
        except (FachschaftUser.DoesNotExist, Studiengang.DoesNotExist,
                Studienabschnitt.DoesNotExist):
            return render(request, 'exoral/profil_unvollstaendig.html', context)

        testate = Testat.objects.filter(
            studiengang=studiengang,
            studienabschnitt=studienabschnitt,
        )

        context.update(
            {
                'studiengang': studiengang,
                'studienabschnitt': studienabschnitt,
                'testate': testate,
            }
        )

        return render(request, 'exoral/home.html', context)


class TestatDetail(LoginRequiredMixin, DetailView):
    model = Testat
    pk_url_kwarg = 'testat_id'


class FrageList(LoginRequiredMixin, ListView):
    model = Frage
    context_object_name = 'fragen'

    def dispatch(self, request, *args, **kwargs):
        self.testat = get_object_or_404(Testat, pk=self.kwargs['testat_id'])
        self.pruefer = get_object_or_404(Dozent, pk=self.kwargs['pruefer_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        fragen = Frage.objects.filter(
            testat=self.testat,
            pruefer=self.pruefer,
        ).prefetch_related(
            'abgestimmte_benutzer'
        ).order_by(
            '-punkte', '-datum'
        )
        user = self.request.user

        for frage in fragen:
            frage.abgestimmt = user in frage.abgestimmte_benutzer.all()

        return fragen

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'testat': self.testat, 'pruefer': self.pruefer})
        return context


class UpvoteFrage(LoginRequiredMixin, View):
    def get(self, request, frage_id):
        frage = get_object_or_404(Frage, pk=frage_id)
        frage.upvote(request.user)
        return redirect(
            'exoral:frage-list',
            testat_id=frage.testat.id,
            pruefer_id=frage.pruefer.id,
        )


class DownvoteFrage(LoginRequiredMixin, View):
    def get(self, request, frage_id):
        frage = get_object_or_404(Frage, pk=frage_id)
        frage.downvote(request.user)
        return redirect(
            'exoral:frage-list',
            testat_id=frage.testat.id,
            pruefer_id=frage.pruefer.id,
        )


class CreateFrage(LoginRequiredMixin, View):
    model = Frage
    fields = ['datum', 'text', 'antwort']
    template_name = 'exoral/frage_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.testat = get_object_or_404(Testat, pk=self.kwargs['testat_id'])
        self.pruefer = get_object_or_404(Dozent, pk=self.kwargs['pruefer_id'])
        if self.pruefer.fach not in self.testat.fach.all():
            error = (
                'Prüfer und Testat passen nicht zusammen. '
                'Das Fach des Prüfers muss in den Fächern des Testats '
                'enthalten sein.'
            )
            return render(request, 'exoral/error.html', {'error': error})
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'testat': self.testat,
            'pruefer': self.pruefer,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        datum = request.POST.get('datum')
        text = request.POST.get('text').strip()
        antwort = request.POST.get('antwort')

        frage = Frage(
            datum=datum,
            text=text,
            antwort=antwort,
            pruefer=self.pruefer,
            testat=self.testat,
        )
        frage.save()

        frage.abgestimmte_benutzer.add(request.user)

        return redirect(
            'exoral:frage-list',
            testat_id=self.testat.pk,
            pruefer_id=self.pruefer.pk,
        )
