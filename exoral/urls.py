from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'exoral'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('testate', views.TestatList.as_view(), name='testat-list'),
    path('testat/<int:testat_id>', views.TestatDetail.as_view(), name='testat-detail'),
    path('testat/<int:testat_id>/edit', views.TestatEdit.as_view(), name='testat-edit'),
    path('fragen/<int:testat_id>/<int:pruefer_id>', views.FrageList.as_view(), name='frage-list'),
    path('upvote/<int:frage_id>', views.FrageUpvote.as_view(), name='upvote-frage'),
    path('downvote/<int:frage_id>', views.FrageDownvote.as_view(), name='downvote-frage'),
    path('neuefrage/<int:testat_id>/<int:pruefer_id>', views.FrageCreate.as_view(), name='frage-create'),
    path('frage/<int:frage_id>/edit', views.FrageEdit.as_view(), name='frage-edit'),
    path('frage/<int:frage_id>/delete', views.FrageDelete.as_view(), name='frage-delete'),
    path('dozenten', views.DozentList.as_view(), name='dozent-list'),
    path('dozent/<int:dozent_id>', views.DozentDetail.as_view(), name='dozent-detail'),
    path('dozent/<int:dozent_id>/edit', views.DozentEdit.as_view(), name='dozent-edit'),
    path('faecher', views.FachList.as_view(), name='fach-list'),
    path('fach/<int:fach_id>/edit', views.FachEdit.as_view(), name='fach-edit'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
