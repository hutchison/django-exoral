from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib import messages

from .models import (
    Dozent,
    Fach,
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

        letzte_fragen = Frage.objects.prefetch_related(
            'pruefer',
            'testat'
        ).order_by('-id')[:20]

        context.update(
            {
                'studiengang': studiengang,
                'studienabschnitt': studienabschnitt,
                'testate': testate,
                'letzte_fragen': letzte_fragen,
            }
        )

        return render(request, 'exoral/home.html', context)


class TestatList(LoginRequiredMixin, ListView):
    queryset = Testat.objects.prefetch_related(
        'fach',
        'studiengang',
        'studienabschnitt',
        'frage_set',
    )
    context_object_name = 'testate'


class TestatDetail(LoginRequiredMixin, DetailView):
    model = Testat
    pk_url_kwarg = 'testat_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faecher = dict()  # Dict[Fach → Dict[Dozent → Int]]
        testat = self.object
        fragen = list(
            Frage.objects.prefetch_related(
                'testat',
                'pruefer',
            ).filter(testat=testat)
        )

        for fach in testat.fach.prefetch_related('dozent_set'):
            faecher[fach] = dict()  # Dict[Dozent → int]
            for dozent in fach.dozent_set.all():
                faecher[fach][dozent] = len(
                    [frage for frage in fragen if frage.pruefer==dozent]
                )

        context['faecher'] = faecher
        return context


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


class FrageEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'exoral.change_frage'

    model = Frage
    fields = ['datum', 'text', 'antwort', 'pruefer', 'testat']
    pk_url_kwarg = 'frage_id'
    template_name_suffix = '_edit'

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Gespeichert!')
        return reverse('exoral:frage-edit', kwargs={'frage_id': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dozenten'] = Dozent.objects.all()
        context['testate'] = Testat.objects.all()
        return context


class FrageDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'exoral.delete_frage'

    model = Frage
    pk_url_kwarg = 'frage_id'

    def get_success_url(self):
        testat = self.object.testat
        pruefer = self.object.pruefer
        messages.add_message(self.request, messages.SUCCESS, 'Gelöscht!')
        return reverse(
            'exoral:frage-list',
            kwargs={'testat_id': testat.id, 'pruefer_id': pruefer.id}
        )


class FrageUpvote(LoginRequiredMixin, View):
    def get(self, request, frage_id):
        frage = get_object_or_404(Frage, pk=frage_id)
        frage.upvote(request.user)
        return redirect(
            'exoral:frage-list',
            testat_id=frage.testat.id,
            pruefer_id=frage.pruefer.id,
        )


class FrageDownvote(LoginRequiredMixin, View):
    def get(self, request, frage_id):
        frage = get_object_or_404(Frage, pk=frage_id)
        frage.downvote(request.user)
        return redirect(
            'exoral:frage-list',
            testat_id=frage.testat.id,
            pruefer_id=frage.pruefer.id,
        )


class FrageCreate(LoginRequiredMixin, View):
    model = Frage
    fields = ['datum', 'text', 'antwort']
    template_name = 'exoral/frage_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.testat = get_object_or_404(Testat, pk=self.kwargs['testat_id'])
        self.pruefer = get_object_or_404(Dozent, pk=self.kwargs['pruefer_id'])
        if self.pruefer.fach not in self.testat.fach.all():
            error = (
                'Prüfer:in und Testat passen nicht zusammen. '
                'Das Fach des:r Prüfers:in muss in den Fächern des Testats '
                'enthalten sein.'
            )
            return render(request, 'exoral/error.html', {'error': error})
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'testat': self.testat,
            'pruefer': self.pruefer,
            'vorhandene_fragen': Frage.objects.filter(
                pruefer=self.pruefer,
                testat=self.testat,
            ),
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


class DozentList(LoginRequiredMixin, ListView):
    queryset = Dozent.objects.prefetch_related('fach')


class DozentDetail(LoginRequiredMixin, DetailView):
    model = Dozent
    pk_url_kwarg = 'dozent_id'


class DozentEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'exoral.change_dozent'

    model = Dozent
    fields = '__all__'
    pk_url_kwarg = 'dozent_id'
    template_name_suffix = '_edit'

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Gespeichert!')
        return reverse('exoral:dozent-detail', kwargs={'dozent_id': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faecher'] = Fach.objects.all()
        return context


class FachList(LoginRequiredMixin, ListView):
    queryset = Fach.objects.prefetch_related('dozent_set', 'testat_set')
