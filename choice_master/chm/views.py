"""
Views for app chm
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from allauth.account.views import login
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse

from chm.models import Question, QuestionOnQuiz, Flag, Quiz, Answer, Topic
from chm.forms import QuizForm, FlagForm
import json


def index(request):
    """
    If the user is authenticated redirect to login, otherwise display index
    page.
    """

    if not request.user.is_authenticated:
        return redirect(login)
    return render(request, 'index.html')


@login_required
def new_quiz(request):
    """ User wants to start an exam. """

    if request.method == 'POST':
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.make_quiz()
            context = {
                'finish_message': _('You have finished the test'),
                'seconds': quiz.seconds_per_question,
                'quiz': quiz.to_json()
            }
            return render(request, 'quiz.html', context)
    else:
        form = QuizForm()

    return render(request, 'new_quiz.html', {'form': form})


@login_required
def correct_quiz(request):
    """ Verify user answers """

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

        return redirect(reverse('quiz_results', kwargs={'id': quiz.id}))
    else:
        return redirect(login)


@login_required
def quiz_results(request, id):
    """Show results obtained in quiz"""
    quiz = get_object_or_404(Quiz, id=id)
    if quiz.user != request.user:
        raise PermissionDenied
    return render(request, 'quiz_results.html', {'quiz': quiz})


@login_required
def duplicate_question(request):
    """
        Given a duplicate question proivded by a POST request
        return a json object containing a new question that is not
        contained in neither the quiz questions.
    """
    if request.method == 'POST':
        data = json.loads(request.POST['data'])

        quiz = get_object_or_404(Quiz, pk=data['quiz_id'])
        question = get_object_or_404(Question, pk=data['question_id'])
        duplicate = get_object_or_404(Question, pk=data['duplicate_id'])
        topic = get_object_or_404(Topic, pk=data['topic_id'])
        qoq = get_object_or_404(QuestionOnQuiz,
                                quiz=quiz,
                                question=question)

        questions_on_quiz = QuestionOnQuiz.objects.filter(quiz=quiz
                                                          ).values('question')
        new_question = Question.objects.filter(
            topic=topic
        ).exclude(
            pk__in=questions_on_quiz
        ).exclude(
            pk=question.pk
        ).exclude(
            pk=duplicate.pk
        ).first()

        flag = Flag.objects.create(
            question=question,
            user=request.user,
            description=_("USER FLAGED THIS QUESTION AS A"
                          "DUPLICATE OF THIS OTHER ONE: ") + duplicate.text
                        )

        flag.save()

        if new_question is None:
            return JsonResponse({'ok': False})

        qoq.question = new_question
        qoq.save(force_update=True)
        return JsonResponse({'ok': True, 'question': new_question.to_json()})


@login_required
def flag_question(request, id):
    """
    Flag the question with id=id
    :param request: POST
    :param id: the id to be a flagged question.
    """
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

@login_required
def answer_question(request):

    if request.method == 'POST':
        qoq = get_object_or_404(QuestionOnQuiz, quiz_id = request.POST['quiz_id'], question_id = request.POST['question_id'])	
        user_answers_set = set(json.loads(request.POST['answer_id']))
          
        correct_answers = Answer.objects.filter(
            question=qoq.question,
            is_correct=True
        ).values('pk')

        correct_answers_set = set(correct_answers)
        if user_answers_set == correct_answers_set:
            qoq.state = QuestionOnQuiz.STATUS.right
        elif not answer['answer_id']:
            # user didn't choose any answer
            qoq.state = QuestionOnQuiz.STATUS.not_answered
        else:
            qoq.state = QuestionOnQuiz.STATUS.wrong
            qoq.save()      
        return JsonResponse({'success': "True"})

    else: 
        return JsonResponse({'success': "False"})