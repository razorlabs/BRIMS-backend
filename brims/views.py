from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.contrib.auth import logout

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def logout_view(request):
    logout(request)
    return redirect('http://10.10.10.190:3000/lims/login')
