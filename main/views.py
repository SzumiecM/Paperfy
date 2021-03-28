import os
import re

import cv2
from django.contrib import messages
from django.core import mail
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.defaultfilters import register

from .models import *


def home(request):
    return render(request=request,
                  template_name='product_list.html',
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
                  template_name='product_descr.html',
                  context={
                      'product': ToiletPaper.objects.get(id=product_id)
                  })


def checkout(request):
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            del request.session['cart'][request.POST.get('delete_id')]
        elif 'change_id' in request.POST:
            request.session['cart'][request.POST.get('change_id')] = int(request.POST.get('product_amount'))
        elif 'order_stuff' in request.POST:
            validate_order(request, request.POST)
            order_stuff(request.POST)

    products_in_cart = request.session.get('cart')

    if products_in_cart:
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
    else:
        return redirect('/')


def validate_order(request, form):
    validated = True

    if not 2 < len(form['first_name']) < 20 or not 2 < len(form['last_name']) < 20:
        messages.info(request, 'Are u sure it is your real name?')
        validated = False
    if not re.fullmatch(r'^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$', form['email']):
        messages.info(request, 'Invalid email')
        validated = False

    if validated:
        return True
    else:
        return False


def order_stuff(form):
    email = EmailMessage(
        'Topic',
        'Thanks for purchasing our toilet paper',
        'paperfy@protonmail.com',
        [form.get('email')]
    )

    dir_path = os.path.dirname(os.path.realpath(__file__))
    img_path = os.path.join(dir_path, 'static', 'img', '1.jpg')

    img = cv2.imread(img_path)
    # cv2.imshow('', img)

    # email.attach('dupa.jpg', img, 'image/jpg')
    # email.attach_file(img_path)
    email.send(fail_silently=False)
    # with mail.get_connection() as connection:
    #     mail.EmailMessage(
    #         'Topic', 'Thanks for purchasing our toilet paper', 'mysterymaninwhitevan@example.com', [form.get('email')],
    #         connection=connection,
    #     ).send()



@register.filter(name='lookup')
def lookup(value, arg):
    return value.get(str(arg))
