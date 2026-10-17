from django.urls import path

from . import views

urlpatterns = [
    path("", views.intro, name="intro"),
    path("start/", views.start, name="start"),
    path("stage/<int:number>/", views.stage, name="stage"),
    path("freedom/", views.freedom, name="freedom"),
    path("reset/", views.reset, name="reset"),
]
