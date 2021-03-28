import os
import random
import re

import cv2
import numpy
from django.contrib import messages
from django.core import mail
from django.core.mail import EmailMessage, send_mail
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
            if validate_order(request, request.POST):
                custom_image = cv2.imdecode(
                    numpy.fromstring(request.FILES.get('custom_image').read(), numpy.uint8
                                     ), cv2.IMREAD_UNCHANGED) if request.FILES.get('custom_image') else None

                order_stuff(request, request.POST, custom_image)
                request.session['cart'] = None
                messages.info(request, 'Order sent to your email')
                return redirect('/')

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


def order_stuff(request, form, custom_img):
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    template_dir_path = os.path.join(PROJECT_ROOT, 'for_processing/img_for_processing')

    if custom_img is None:
        custom_img_path = random.choice(
                [os.path.join(PROJECT_ROOT, 'for_processing/img_for_processing', x) for x in os.listdir(template_dir_path)])
    else:
        custom_img_path = prepare_image(custom_img)

    products_in_cart = request.session.get('cart')
    products_from_base = ToiletPaper.objects.filter(id__in=products_in_cart.keys())

    total_to_pay = 0
    order = []

    for product in products_from_base:
        amount = products_in_cart.get(str(product.id))
        order.append(f'{product.name}: {amount} --> {product.price * amount} zł')
        total_to_pay += product.price * amount

    nl = '\n'

    email_body = f'''
Thanks for purchasing our toilet paper.

Your order is:{nl}
{nl.join(order)}

Which is {total_to_pay} zł in total to pay. 

You owe us... hihi
    '''

    email = EmailMessage(
        'Your personal paper delivery',
        email_body,
        'milosz.sz.m@gmail.com',
        [form.get('email')]
    )

    if custom_img_path:
        # email.attach('paper.jpg', custom_img_path, 'image/jpg')
        email.attach_file(custom_img_path)

        email.send(fail_silently=False)
        # os.remove(custom_img_path)

    else:
        email.send(fail_silently=False)


@register.filter(name='lookup')
def lookup(value, arg):
    return value.get(str(arg))


def prepare_image(custom_img):
    def add_to_template(template, x_offset, y_offset):
        template[y_offset:y_offset + custom_img.shape[0], x_offset:x_offset + custom_img.shape[1]] = custom_img
        return template

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    template = cv2.imread(os.path.join(PROJECT_ROOT, 'for_processing/template.jpg'))

    custom_img = custom_img[:, :, :3]

    final_img_size = 372
    custom_img = cv2.resize(custom_img, (final_img_size, final_img_size))
    custom_img = cv2.rotate(custom_img, cv2.ROTATE_90_CLOCKWISE)

    x_offset = 286
    y_offset = 212
    for _ in range(2):
        template = add_to_template(template, x_offset, y_offset)
        y_offset += final_img_size

    file_name = os.path.join(
        PROJECT_ROOT, f'for_processing/img_processed/order_{random.randrange(100000000000000, 999999999999999)}.jpg')
    cv2.imwrite(file_name, template)

    return file_name
