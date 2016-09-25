from django.conf.urls import url

from classify_service import views

urlpatterns = [
    url(r'^$', views.ContentClassifyService.as_view()),  # backward-compatible
    url(r'^content', views.ContentClassifyService.as_view()),
    url(r'^food', views.FoodClassifyService.as_view()),
]
