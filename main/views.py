from django.shortcuts import render
from .models import *


def home(request):
    return render(request=request,
                  template_name='home.html',
                  context={
                      'toilet_papers': ToiletPaper.objects.all()
                  })
