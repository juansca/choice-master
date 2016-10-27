from django.shortcuts import render
from django.shortcuts import redirect
from allauth.account.views import login

from chm.models import Question


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
