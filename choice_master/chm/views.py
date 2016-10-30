"""
Views for app chm
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chm.models import Question, QuestionOnQuiz
from chm.forms import QuizForm


@login_required
def index(request):
    """ If the user is authenticated redirect to login,
    otherwise display index page.
    """
    context = {}
    if request.user.is_staff:
        nfq = Question.objects.filter(flags__isnull=False).count()
        context['n_flagged_questions'] = nfq
    return render(request, 'index.html', context)


@login_required
def new_quiz(request):
    """ User wants to start an exam."""

    if request.method == 'POST':
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.make_quiz()
            return render(request, 'quiz.html', {'quiz': quiz.to_json()})
    else:
        form = QuizForm()

    return render(request, 'new_quiz.html', {'form': form})

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
        elif not ans_ids:
            qoq.STATUS = 'not answered'
        else:
            qoq.STATUS = 'wrong'
        qoq.save()

    return render(request, 'quiz_results.html', {'quiz': quiz})



def timer(request):
    seconds = request.GET.get('seconds', 10)
    return render(request, 'timer.html', {'seconds': seconds})
