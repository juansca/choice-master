"""
Views for app chm
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chm.models import Question, QuestionOnQuiz
from chm.forms import QuizForm

def correct_quiz(request):
    """ Verify user answers"""

    quiz_id = request.POST('quiz_id')
    quiz = Quiz.objects.get(pk=quiz_id)
    for answer in request.POST('answer'):
        qoq = QuestionOnQuiz.objects.get(question=answer['question_id'], quiz_id=quiz_id)
        question_ans = Answer.objects.get(question=answer['question_id']).values('pk')
        ans_ids = []
        for ids in question_ans:
            ans_ids.append(ids['pk'])

        if answer['answer_id'] == ans_ids:
            qoq.STATUS = 'right'
        else if ans_ids ==[]:
            qoq.STATUS = 'not answered'
        else:
        qoq.STATUS = 'wrong'
        qoq.save()

    return render(request, 'quiz_results.html', {'quiz': quiz})



from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from chm import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'quizz/new/$', views.new_quiz, name='new_quiz'),
    url(r'correct/answer$', views.correct_quiz, name='correct_quiz')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
