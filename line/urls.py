from django.conf.urls import url
from django.views.generic import TemplateView
from app.views import *

urlpatterns = [
    url(r'^$', CallbackView.as_view()),
    url(r'^favicon.ico$', TemplateView.as_view(template_name='favicon.ico')),
]
