from .models import Question


def flagged_questions(request):
    """
    Add the flagged questions to the context if user is staff
    :param request: The request
    :type request: HttpRequest
    :return: The context
    :rtype: dict[string, T]
    """
    context = {}
    if request.user.is_staff:
        nfq = Question.objects.filter(flags__isnull=False).count()
        context['n_flagged_questions'] = nfq
    return context
