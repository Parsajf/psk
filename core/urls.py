from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('projects/<str:slug>/', views.project_detail, name='project_detail'),
    path('blog/', views.blog, name='blog'),
    path('blog/<str:slug>/', views.article_detail, name='article_detail'),
    path('about/', views.about, name='about'),
    path('consultation/', views.consultation, name='consultation'),
    path('index.html', RedirectView.as_view(pattern_name='home', permanent=True)),
    path('projects.html', RedirectView.as_view(pattern_name='projects', permanent=True)),
    path('blog.html', RedirectView.as_view(pattern_name='blog', permanent=True)),
    path('about.html', RedirectView.as_view(pattern_name='about', permanent=True)),
    path('project-single.html', RedirectView.as_view(url='/projects/chenar-villa/', permanent=False)),
    path('blog-single.html', RedirectView.as_view(url='/blog/house-in-dialogue-with-land/', permanent=False)),
]
