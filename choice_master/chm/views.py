from django.shortcuts import render

def index(request):
    context = {'request': request}
    return render(request, 'index.html')
