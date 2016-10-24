"""
Views for app chm
"""
from django.shortcuts import render
from django.shortcuts import redirect
from allauth.account.views import login
from django.core.exceptions import PermissionDenied

from chm.forms import XMLFileForm


def index(request):
    """ If the user is authenticated redirect to login,
    otherwise display index page.
    """
    if not request.user.is_authenticated:
        return redirect(login)
    return render(request, 'index.html')


def upload(request):
    if not request.user.is_staff:
        raise PermissionDenied

    context = {'questions_added': [], 'questions_errors': []}
    if request.method == 'POST':
        form = XMLFileForm(request.POST, request.FILES)
        if form.is_valid():
            for question in f(request.FILES['XMLfile']):
                if not_repeated(question):
                    # salvar en la bbdd
                    context['questions_added'].append(question)
                else:
                    context['questions_errors'].append(question)

    else:
        form = XMLFileForm()

    context['form'] = form
    # Load documents for the list page
    return render(request, 'upload.html', context)


# JUANSCA Y TRUCCO: linkear acá
def f(*args):
    return '42'


# JUANSCA Y TRUCCO: linkear acá
def not_repeated(*args):
    return True
