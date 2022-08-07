from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'exoral'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('downvote/<int:frage_id>', views.FrageDownvote.as_view(), name='downvote-frage'),
    path('dozent/<int:dozent_id>', views.DozentDetail.as_view(), name='dozent-detail'),
    path('dozent/<int:dozent_id>/edit', views.DozentEdit.as_view(), name='dozent-edit'),
    path('dozent/create', views.DozentCreate.as_view(), name='dozent-create'),
    path('dozenten', views.DozentList.as_view(), name='dozent-list'),
    path('fach/<int:fach_id>/edit', views.FachEdit.as_view(), name='fach-edit'),
    path('fach/create', views.FachCreate.as_view(), name='fach-create'),
    path('faecher', views.FachList.as_view(), name='fach-list'),
    path('frage/<int:frage_id>/delete', views.FrageDelete.as_view(), name='frage-delete'),
    path('frage/<int:frage_id>/edit', views.FrageEdit.as_view(), name='frage-edit'),
    path('frage/<int:testat_id>/<int:pruefer_id>/create', views.FrageCreate.as_view(), name='frage-create'),
    path('fragen/<int:testat_id>/<int:pruefer_id>', views.FrageList.as_view(), name='frage-list'),
    path('testat/<int:testat_id>', views.TestatDetail.as_view(), name='testat-detail'),
    path('testat/<int:testat_id>/edit', views.TestatEdit.as_view(), name='testat-edit'),
    path('testat/create', views.TestatCreate.as_view(), name='testat-create'),
    path('testate', views.TestatList.as_view(), name='testat-list'),
    path('upvote/<int:frage_id>', views.FrageUpvote.as_view(), name='upvote-frage'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
