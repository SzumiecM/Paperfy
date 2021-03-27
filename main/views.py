from django.shortcuts import render, redirect
from .models import *


def home(request):
    return render(request=request,
                  template_name='home.html',
                  context={
                      'toilet_papers': ToiletPaper.objects.all()
                  })


def product(request, product_id=None):
    # if request.method == 'POST':
    #     request.session['selected_product'] = request.POST.get('product_id')

    return render(request=request,
                  template_name='product.html',
                  context={
                      'product': ToiletPaper.objects.get(id=product_id)
                  })

