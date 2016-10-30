from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from chm import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'quiz/new/$', views.new_quiz, name='new_quiz'),
    url(r'quiz/timer/$', views.timer, name='timer'),
    url(r'quiz/results/$', views.quiz_results, name='quiz_results'),
    url(r'question/(?P<id>\d+)/flag/$', views.flag_question, name='flag'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
