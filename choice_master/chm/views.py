"""
Views for app chm
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from allauth.account.views import login
from django.core.exceptions import PermissionDenied

from chm.models import Question, QuestionOnQuiz, Flag, Quiz, Answer
from chm.forms import QuizForm, FlagForm
import json


def index(request):
    """
    If the user is authenticated redirect to login, otherwise display index
    page.
    """

    if not request.user.is_authenticated:
        return redirect(login)
    else:
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


@login_required
def correct_quiz(request):
    """ Verify user answers"""

    if request.method == 'POST':
        data = json.loads(request.POST['json'])
        quiz_id = data['quiz_id']

        # fail with 404 if quiz doesn't exist
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        # fail with 403 if user didn't take this quiz
        if request.user != quiz.user:
            raise PermissionDenied

        for answer in data['answers']:
            question = get_object_or_404(Question, pk=answer['question_id'])
            qoq = get_object_or_404(
                QuestionOnQuiz,
                question=question,
                quiz=quiz
            )
            correct_answers = Answer.objects.filter(
                question=question,
                is_correct=True
            ).values('pk')

            correct_answers_ids = list()
            for answ in correct_answers:
                correct_answers_ids.append(str(answ['pk']))
            if answer['answer_id'] == correct_answers_ids:
                qoq.state = QuestionOnQuiz.STATUS.right
            elif not answer['answer_id']:
                # user didn't choose any answer
                qoq.state = QuestionOnQuiz.STATUS.not_answered
            else:
                qoq.state = QuestionOnQuiz.STATUS.wrong
            qoq.save()

        return render(request, 'quiz_results.html', {'quiz': quiz})
    else:
        return redirect(login)


def timer(request):
    seconds = request.GET.get('seconds', 10)
    return render(request, 'timer.html', {'seconds': seconds})


def flag_question(request, id):
    question = get_object_or_404(Question, id=id)
    context = {'question': question}
    if request.method == 'POST':
        form = FlagForm(request.POST)
        if form.is_valid():
            flag = Flag.objects.create(
                question=question,
                user=request.user,
                description=form.cleaned_data['description'],
            )
            context['flag'] = flag
    else:
        form = FlagForm()

    context['form'] = form
    return render(request, 'flag.html', context)
