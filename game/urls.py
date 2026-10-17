from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about, name="about"),
    path("lead/", views.facilitator, name="facilitator"),
    path("lead/answers/", views.answers, name="answers"),
    path("play/", views.intro, name="intro"),
    path("start/", views.start, name="start"),
    path("stage/<int:number>/", views.stage, name="stage"),
    path("freedom/", views.freedom, name="freedom"),
    path("reset/", views.reset, name="reset"),
    path("backdrop/", views.backdrop, name="backdrop"),
    path("story/", views.story, name="story"),
    path("debrief/", views.debrief, name="debrief"),
]
