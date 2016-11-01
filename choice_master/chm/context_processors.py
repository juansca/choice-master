from .models import Question

def flagged_questions(request):
    context = {}
    if request.user.is_staff:
        nfq = Question.objects.filter(flags__isnull=False).count()
        context['n_flagged_questions'] = nfq
    return context
