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
from django.shortcuts import render,get_object_or_404
import pandas as pd
from .models import UploadedFile
from .module.process_data import ProcessData
from .module.visualize_data import VisualizeData
from .module.get_insight import get_insight
import boto3
import os
from dotenv import load_dotenv
from plotly.offline import plot
import json
import io
import plotly.express as px
load_dotenv()
minio_url = os.getenv('MINIOURL')
minio_access_key = os.getenv('MINIO_ACESS_KEY')
minio_secret_key = os.getenv('MINIO_SECRET_KEY')
s3 = boto3.client(
    's3',
    endpoint_url=minio_url,
    aws_access_key_id=minio_access_key,
    aws_secret_access_key=minio_secret_key
)

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
def upload_files(request):
    if request.method == 'POST':
        prompt=request.POST.get("prompt","")
        uploadName=request.POST.get("name","")
        print(uploadName)
        files = request.FILES.getlist("files[]")
        if len(files)==0:
            return JsonResponse({
                'status': 'error',
                'message': 'No file uploaded'
            }, status=400)

        try:
            # Kiểm tra định dạng và kích thước file
            combined_data = []
            uploaded_file = UploadedFile.objects.create(
                file=[],  # Store the MinIO file key in the database
                uploadName=uploadName,
            )
            for file in files:
                if file.size > 10 * 1024 * 1024:  # Giới hạn 10MB 
                    return JsonResponse({
                        'status': 'error',
                        'message': 'File size too large.'
                    }, status=400)

                if not file.name.endswith(('.csv', '.xlsx', '.xls')):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Unsupported file format. Please upload a .csv or .xlsx file.'
                    }, status=400)            
            # Lưu file vào minIO
            # Đọc file với pandas, thêm `header=None` nếu không có tiêu đề cột                    
                file.seek(0)  
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file, header=0)  # Thay đổi header=0 hoặc header=None tùy theo dữ liệu của bạn
                else:
                    df = pd.read_excel(file)            
                # Nếu file trống, trả về lỗi
                if df.empty:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Uploaded file is empty.'
                    }, status=400)
                minio_key = f"uploads/{file.name}"
                file.seek(0)
                s3.upload_fileobj(file, "datainsight", minio_key)
                uploaded_file.file.append(minio_key)
                metadata = {
                'columns': list(df.columns),
                'num_rows': len(df),
                'file_name': file.name
                }
                combined_data.append({
                    'df':df,
                    'metadata':metadata,
                })
            #Process data
            combined_metadata = "\n".join(
            json.dumps(item['metadata']) for item in combined_data
            )
            uploaded_file.metadata=combined_metadata
            processor = ProcessData(combined_data)
            df_processed = processor.process_data_df()
            data_summary = processor.get_summary_data()
            #visualize processed data
            visualizer = VisualizeData(df_processed)
            visualize_result=visualizer.visualize_data_df(metadata,prompt)
            plot_path = [{"plotDiv":item["plot"].to_json(),"description":item["description"]} for item in visualize_result]
            for i in range(len(visualize_result)):
                plot_path[i]["context"]=get_insight(json.loads(visualize_result[i]["plot"].to_json()),visualize_result[i]["description"])[0]
                plot_path[i]["insight"]=get_insight(json.loads(visualize_result[i]["plot"].to_json()),visualize_result[i]["description"])[1]
            uploaded_file.processed = True
            uploaded_file.validated = True
            uploaded_file.plotImages+=plot_path
            uploaded_file.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Data processed and visualized successfully.',
                'data_summary': data_summary,
                'plot_path': plot_path,
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
        file_path=uploaded_file.file.path
        visualizer=VisualizeData.load_data(file_path)
        plot_path=visualizer.visualize_data_df(uploaded_file.metadata,"")
        return JsonResponse({
            'status': 'success',
            'plot_path': plot_path
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
@login_required(login_url="/login/")
def get_uploads(request):
    try:
        uploaded_files=UploadedFile.objects.all().values('file','uploadName', 'processed', 'validated', 'created_at', 'updated_at','id','plotImages')
        files_list = list(uploaded_files)
        return JsonResponse({
            'status':"success",
            'files':files_list
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
@login_required(login_url="/login/")
def get_details(request, file_id):
    try:
        # Fetch the uploaded file details
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        file_data = {
            "id":uploaded_file.id,
            "file": uploaded_file.file,
            "uploadName":uploaded_file.uploadName,
            "processed": uploaded_file.processed,
            "validated": uploaded_file.validated,
            "created_at": uploaded_file.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": uploaded_file.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "plotImages": uploaded_file.plotImages,
        }
        # Pass the file details to the template
        return render(request, 'home/file_detail.html', {
            'fileData': file_data
        })

    except Exception as e:
        # Handle exceptions and show an error page or message
        return render(request, 'error.html', {
            'message': str(e)
        }, status=500)
def get_plots_details(request, file_id):
    try:
        # Fetch the uploaded file details
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        # Pass the file details to the template
        return JsonResponse({
            'status': 'success',
            'plot_path': uploaded_file.plotImages,
            'id':uploaded_file.id,
        })
    except Exception as e:
        # Handle exceptions and show an error page or message
        return render(request, 'error.html', {
            'message': str(e)
        }, status=500)
def get_file_from_minio(file_key):
    """
    Retrieve a file from the MinIO bucket.

    :param file_key: The key (name) of the file in the bucket.
    :return: File content as bytes.
    """
    try:
        response = s3.get_object(Bucket='datainsight', Key=file_key)
        return response['Body'].read()
    except Exception as e:
        raise Exception(f"Error retrieving file: {str(e)}")

def reprompt(request):
    try:
        body = json.loads(request.body)
        prompt = body.get("prompt")
        file_id = body.get("id")
        combined_data = []
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        file_keys=uploaded_file.file
        for file_key in file_keys:
            file_content=get_file_from_minio(file_key)
            if(file_key.endswith('.csv')):
                file=io.StringIO(file_content.decode('utf-8'))
            elif file_key.endswith(('.xlsx','.xls')):
                file=io.BytesIO(file_content)
            if file_key.endswith('.csv'):
                df = pd.read_csv(file, header=0)  
            else:
                df = pd.read_excel(file)
                metadata = {
                'columns': list(df.columns),
                'num_rows': len(df),
                }
                combined_data.append({
                    'df':df,
                    'metadata':metadata,
                })
        combined_metadata = "\n".join(
        json.dumps(item['metadata']) for item in combined_data
        )
        uploaded_file.metadata=combined_metadata
        #visualize processed data
        processor = ProcessData(combined_data)
        df_processed = processor.process_data_df()
        visualizer = VisualizeData(df_processed)
        visualize_result=visualizer.visualize_data_df(combined_metadata,prompt)
        plot_path = [{"plotDiv":item["plot"].to_json(),"description":item["description"]} for item in visualize_result]
        for i in range(len(visualize_result)):
            plot_path[i]["context"]=get_insight(json.loads(visualize_result[i]["plot"].to_json()),visualize_result[i]["description"])[0]
            plot_path[i]["insight"]=get_insight(json.loads(visualize_result[i]["plot"].to_json()),visualize_result[i]["description"])[1]
        uploaded_file.processed = True
        uploaded_file.validated = True
        uploaded_file.plotImages=plot_path
        uploaded_file.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Data processed and visualized successfully.',
            'plot_path': plot_path
        })


    except Exception as e:
        return render(request, 'error.html', {
            'message': str(e)
        }, status=500)
def add_insight(request):
    try:
        body = json.loads(request.body)
        prompt = body.get("prompt")
        file_id = body.get("id")
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        combined_data = []
        file_keys=uploaded_file.file
        for file_key in file_keys:
            file_content=get_file_from_minio(file_key)
            if(file_key.endswith('.csv')):
                file=io.StringIO(file_content.decode('utf-8'))
            elif file_key.endswith(('.xlsx','.xls')):
                file=io.BytesIO(file_content)
            if file_key.endswith('.csv'):
                df = pd.read_csv(file, header=0)  
            else:
                df = pd.read_excel(file)
            metadata = {
                'columns': list(df.columns),
                'num_rows': len(df),
                }
            combined_data.append({
                'df':df,
                'metadata':metadata,
            })
        combined_metadata = "\n".join(
        json.dumps(item['metadata']) for item in combined_data
        )
        uploaded_file.metadata=combined_metadata
        processor = ProcessData(combined_data)
        df_processed = processor.process_data_df()
        #visualize processed data
        visualizer = VisualizeData(df_processed)
        visualize_result=visualizer.visualize_data_df(combined_metadata,prompt)
        plot_path = [{"plotDiv":item["plot"].to_json(),"description":item["description"]} for item in visualize_result]
        for i in range(len(visualize_result)):
            plot_path[i]["context"]=get_insight(json.loads(visualize_result[i]["plot"].to_json()),visualize_result[i]["description"])[0]
            plot_path[i]["insight"]=get_insight(json.loads(visualize_result[i]["plot"].to_json()),visualize_result[i]["description"])[1]
        uploaded_file.processed = True
        uploaded_file.validated = True
        uploaded_file.plotImages+=plot_path
        uploaded_file.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Data processed and visualized successfully.',
            'plot_path': uploaded_file.plotImages
        })


    except Exception as e:
        return render(request, 'error.html', {
            'message': str(e)
        }, status=500)
def delete_insight(request):
    try:
        body=json.loads(request.body)
        file_id=body.get("id")
        print(file_id)
        delete_index=body.get("delete_index")
        uploaded_file=get_object_or_404(UploadedFile,id=file_id)
        del uploaded_file.plotImages[delete_index]
        uploaded_file.save()
        return JsonResponse({
            'status':'success',
            'message':'Delete insight successfully'
        })
    except Exception as e:
        return render(request, 'error.html', {
            'message': str(e)
        }, status=500)