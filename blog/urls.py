from django.urls import path

from blog import views
from blog.apps import BlogConfig


app_name = BlogConfig.name

urlpatterns = [
    path('', views.PublicationListView.as_view(), name='publication_list'),
    path('info/', views.SmallPublicationListView.as_view(), name='info_list'),
    path('create/', views.PublicationCreateView.as_view(), name='publication_create'),
    path('<int:pk>/', views.PublicationDetailView.as_view(), name='publication_detail'),
    path('<int:pk>/update/', views.PublicationUpdateView.as_view(), name='publication_update'),
    path('<int:pk>/delete/', views.PublicationDeleteView.as_view(), name='publication_delete'),
    path('photo/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
]