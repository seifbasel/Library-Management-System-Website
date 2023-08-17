from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
<<<<<<< HEAD
    return render(request, "students/index.html")
=======
    return render(request, "students/index.html")
>>>>>>> 8b81203d696840807a3dc62c4b58d709ce93df85
