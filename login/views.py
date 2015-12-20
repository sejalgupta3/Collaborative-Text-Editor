from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from login.forms import NameForm,UserForm, UserCreationForm
from django.template import RequestContext
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.http import HttpResponse
from random import randint
from django.shortcuts import redirect

string = []
def index(request, pk=None):
	if pk is None:
            return render(request, 'login/index.html')
	else:
            return render(request, 'login/index.html', {'eid':pk})

def results(request, pk=None):
    if pk is None:
        eid = randint(1,10000)
    else:
        eid = pk
    try:
        username = request.POST['USERNAME']
        password = request.POST['PASSWORD']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                request.session['username'] = username
                post_data = [('username',username),('lineNumber',1),('editorText',""),('textdata',""),]     # a sequence of two element tuples
                result = urllib2.urlopen('http://10.0.0.7:8000/docEditor/editor/', urllib.urlencode(post_data))
                content = result.read()
                return redirect('http://10.0.0.7:8000/docEditor/editor/'+str(eid), username=request.session['username'])

            else:
                form = NameForm(request.POST)
                msg="Error"
                return render(request,'login/index.html',{'form': form})
        else:
        # the authentication system was unable to verify the username and password
            msg="Invalid Credentials.. Pls try again"
            return render(request, 'login/index.html', {'msg': msg})
    except:
        form = NameForm(request.POST)
        msg="Error"
        return redirect('http://10.0.0.7:8000/docEditor/editor/'+str(eid), username=request.session['username'])

def register(request):
    form = NameForm(request.POST)
    return render(request, 'login/register.html', {'form': form})

def registerUser(request):
    username=request.POST.get('username')
    pass1 = request.POST['password']
    email = request.POST.get('email')
    user = User.objects.create_superuser(username=username,email=email,password=pass1)
    user = User.objects.get(username=username)
    user.set_password(pass1)
    user.is_staff = True
    user.save()
    return render(request, "login/index.html")