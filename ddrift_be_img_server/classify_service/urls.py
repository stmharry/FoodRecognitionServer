from django.conf.urls import patterns, url

from classify_service import views

urlpatterns = patterns('',
    url(r'^$', views.ClassifyService.as_view()),
)
