#apps/home/views.py
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
import pandas as pd
from .models import UploadedFile
import os

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        
        if not file:
            return JsonResponse({
                'status': 'error',
                'message': 'No file uploaded'
            }, status=400)

        try:
            # Lưu file vào database
            uploaded_file = UploadedFile.objects.create(file=file)
            # Xử lý file
            # if file.name.endswith('.csv'):
            #     df = pd.read_csv(file)
            # elif file.name.endswith(('.xls', '.xlsx')):
            #     df = pd.read_excel(file)
            if file.name.endswith(('.csv','.xls', '.xlsx')):
                df = pd.read_csv(file)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Unsupported file format. Please upload a .csv or .xlsx file.'
                }, status=400)

            # Đánh dấu file đã được xử lý
            uploaded_file.processed = True
            uploaded_file.save()

            # Tạo bản tóm tắt dữ liệu
            data_summary = df.describe().to_html(classes='table table-striped')
            
            return JsonResponse({
                'status': 'success',
                'data_summary': data_summary
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)