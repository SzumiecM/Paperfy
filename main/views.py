from django.shortcuts import render, redirect
from django.template.defaultfilters import register

from .models import *


def home(request):
    return render(request=request,
                  template_name='home.html',
                  context={
                      'toilet_papers': ToiletPaper.objects.all()
                  })


def product(request, product_id=None):
    if request.method == 'POST':
        if not request.session.get('cart'):
            request.session['cart'] = {}

        product_id, product_amount = request.POST.get('product_id'), int(request.POST.get('product_amount'))

        if product_amount > 0:
            if product_id in request.session.get('cart').keys():
                request.session['cart'][product_id] = request.session.get('cart').get(product_id) + product_amount
            else:
                request.session['cart'][product_id] = product_amount

            return redirect('checkout')

    return render(request=request,
                  template_name='product.html',
                  context={
                      'product': ToiletPaper.objects.get(id=product_id)
                  })


def checkout(request):
    products_in_cart = request.session.get('cart')
    products_from_base = ToiletPaper.objects.filter(id__in=products_in_cart.keys())

    total_to_pay = 0

    for product in products_from_base:
        total_to_pay += product.price * products_in_cart.get(str(product.id))

    return render(request=request,
                  template_name='checkout.html',
                  context={
                      'products_in_cart': products_in_cart,
                      'products_from_base': products_from_base,
                      'total_to_pay': total_to_pay
                  })


@register.filter(name='lookup')
def lookup(value, arg):
    return value.get(str(arg))
