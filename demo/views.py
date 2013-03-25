from django.http import HttpResponse, HttpResponseRedirect
from django_tlsauth.views import tlsauth

def unauth(request):
    return HttpResponseRedirect('/')

@tlsauth(unauth=unauth, groups=['helloworldophobians'])
def hello(request):
    return HttpResponse("hello world")
