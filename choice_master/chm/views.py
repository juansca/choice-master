from django.shortcuts import render
from django.shortcuts import redirect
from allauth.account.views import login

from chm.forms import XMLFileForm


def index(request):
    """
        If the user is authenticated redirect to login, otherwise display index
    """
    if not request.user.is_authenticated:
        return redirect(login)
    return render(request, 'index.html')

"""
def upload(request):
    context = {'topics': Topic.objects.all(), 'subjects': Subject.objects.all()}
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('upload'))
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()
    return render(request, 'upload.html', context)
"""


def upload(request):
    context = {'questions_added': [], 'questions_errors': []}
    if request.method == 'POST':
        form = XMLFileForm(request.POST, request.FILES)
        if form.is_valid():
            for question in f(request.FILES['XMLfile']):
                if not_repeated(question):
                    ## salvar en la bbdd
                    context['questions_added'].append(question)
                else:
                    context['questions_errors'].append(question)

    else:
        form = XMLFileForm()

    context['form'] = form
    # Load documents for the list page
    return render(request, 'upload.html', context)

### JUANSCA Y TRUCCO: linkear acá
def f(*args):
    return '42'

### JUANSCA Y TRUCCO: linkear acá
def not_repeated(*args):
    return True