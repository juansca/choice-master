"""
Custom tags for app chm
"""

from django import template

from chm.models import Quiz
from chm.models import QuestionOnQuiz

register = template.Library()


STATUS = {
    QuestionOnQuiz.STATUS.right: 'right',
    QuestionOnQuiz.STATUS.wrong: 'wrong',
    QuestionOnQuiz.STATUS.not_answered: 'not answered',
    Quiz.STATUS.aborted: 'aborted',
    Quiz.STATUS.in_progress: 'in progress',
    Quiz.STATUS.finished: 'finished',
}

GLYPHICON = {
    QuestionOnQuiz.STATUS.right: 'glyphicon-ok',
    QuestionOnQuiz.STATUS.wrong: 'glyphicon-remove',
    QuestionOnQuiz.STATUS.not_answered: 'glyphicon-ban-circle',
}


@register.filter(name='humanize_status')
def humanize_status(status):
    """Provides a more human representation of
    a quiz or question state"""
    return STATUS.get(status, status)


@register.filter(name='glyphicon')
def glyphicon(question_on_quiz):
    """Provides bootsrap gliphicon according to
    this question on quiz state
    """
    return GLYPHICON.get(question_on_quiz.state, 'glyphicon-question-sign')
