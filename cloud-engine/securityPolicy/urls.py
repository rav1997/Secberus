from django.conf.urls import url
from .views import ListPolicy, ListRules

urlpatterns = [
    url(r'^list/$', ListPolicy.as_view()),
    url(r'^rules/$', ListRules.as_view()),
]
