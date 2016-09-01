from django.conf.urls import patterns, url

from classify_service import views

urlpatterns = patterns('',
  url(r'^6', views.ClassifyService_6.as_view()),
  url(r'^36', views.ClassifyService_36.as_view()),
)
