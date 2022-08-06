from django.urls import path

from . import views

app_name = 'exoral'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('testat/<int:testat_id>', views.TestatDetail.as_view(), name='testat-detail'),
    path('fragen/<int:testat_id>/<int:pruefer_id>', views.FrageList.as_view(), name='frage-list'),
    path('upvote/<int:frage_id>', views.UpvoteFrage.as_view(), name='upvote-frage'),
    path('downvote/<int:frage_id>', views.DownvoteFrage.as_view(), name='downvote-frage'),
    path('neuefrage/<int:testat_id>/<int:pruefer_id>', views.CreateFrage.as_view(), name='frage-create'),
    path('frage/<int:frage_id>/edit', views.EditFrage.as_view(), name='frage-edit'),
    path('frage/<int:frage_id>/delete', views.FrageDelete.as_view(), name='frage-delete'),
    path('dozenten', views.DozentList.as_view(), name='dozent-list'),
    path('dozent/<int:dozent_id>', views.DozentDetail.as_view(), name='dozent-detail'),
]
