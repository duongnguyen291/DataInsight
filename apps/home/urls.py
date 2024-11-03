#apps/home/urls.py
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    path('uploads/',views.upload_file,name='upload_file'),
    path('process/<int:file_id>/', views.process_data, name='process_data'),
    path('visualize/<int:file_id>/', views.visualize_data, name='visualize_data'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
