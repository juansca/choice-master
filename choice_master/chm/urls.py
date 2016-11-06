from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from chm import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'quiz/new/$', views.new_quiz, name='new_quiz'),
    url(r'quiz/duplicates/$', views.duplicate_question,
        name='duplicate_question'),
    url(r'quiz/(?P<id>\d+)/results/$', views.quiz_results,
        name='quiz_results'),
    url(r'quiz/corrected/$', views.correct_quiz, name='correct_quiz'),
    url(r'question/(?P<id>\d+)/flag/$', views.flag_question, name='flag'),
    url(r'question/answer/$', views.answer_question, name='answer_question'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
