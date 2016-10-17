from django.shortcuts import render
from django.shortcuts import redirect
from allauth.account.views import login

def index(request):
    context = {'request': request}
    if not request.user.is_authenticated:
        return redirect(login)
    return render(request, 'index.html')
