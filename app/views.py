from django.shortcuts import render
from .models import Skills, Project

def home(request):
    projects = Project.objects.all()
    skills = Skills.objects.all()
    return render(request, 'home.html', {'projects': projects, 'skills': skills})
