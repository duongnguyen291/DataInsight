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
from .module.process_data import ProcessData
from .module.visualize_data import VisualizeData

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
            # Kiểm tra định dạng và kích thước file
            if file.size > 10 * 1024 * 1024:  # Giới hạn 10MB chẳng hạn
                return JsonResponse({
                    'status': 'error',
                    'message': 'File size too large.'
                }, status=400)

            if not file.name.endswith(('.csv', '.xlsx', '.xls')):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Unsupported file format. Please upload a .csv or .xlsx file.'
                }, status=400)

            # Lưu file vào database
            uploaded_file = UploadedFile.objects.create(file=file)

            # Đọc file với pandas, thêm `header=None` nếu không có tiêu đề cột
            if file.name.endswith('.csv'):
                file.seek(0)  
                df = pd.read_csv(file, header=0)  # Thay đổi header=0 hoặc header=None tùy theo dữ liệu của bạn
            else:
                df = pd.read_excel(file)

            # Nếu file trống, trả về lỗi
            if df.empty:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Uploaded file is empty.'
                }, status=400)

            # Lưu metadata
            metadata = {
                'columns': list(df.columns),
                'num_rows': len(df),
                'file_name': file.name
            }
            uploaded_file.metadata = metadata
            uploaded_file.save()
            #Process data
            processor = ProcessData(df)
            df_processed = processor.process_data_df(metadata)
            data_summary = processor.get_summary_data()
            #visualize processed data
            visualizer = VisualizeData(df_processed)
            plot_path = visualizer.visualize_data_df(metadata)
            print("Plot path:",plot_path)
            uploaded_file.processed = True
            uploaded_file.validated = True
            uploaded_file.plotImages.append(plot_path)
            uploaded_file.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Data processed and visualized successfully.',
                'data_summary': data_summary,
                'plot_path': plot_path
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


@login_required(login_url="/login/")
def process_data(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
        if not uploaded_file.processed:
            # Load file từ database
            file_path = uploaded_file.file.path
            # Tạo instance của ProcessData với dữ liệu đã load
            processor = ProcessData.load_data(file_path)
            # Xử lý dữ liệu bằng phương thức process_data_df
            df = processor.process_data_df(uploaded_file.metadata)
            # Tạo bản tóm tắt dữ liệu sau khi xử lý
            data_summary = processor.get_summary_data()
            # Update trạng thái xử lý
            uploaded_file.processed = True
            uploaded_file.validated = True
            uploaded_file.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Data processed successfully.',
                'data_summary': data_summary
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'File already processed.'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required(login_url="/login/")
def visualize_data(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
        
        if not uploaded_file.validated:
            return JsonResponse({
                'status': 'error',
                'message': 'Data not validated for visualization.'
            })
        file_path=upload_file.file.path
        visualizer=VisualizeData.load_data(file_path)
        plot_path=visualizer.visualize_data_df(uploaded_file.metadata)
        return JsonResponse({
            'status': 'success',
            'plot_path': plot_path
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
