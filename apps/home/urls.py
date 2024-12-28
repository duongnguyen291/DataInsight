#apps/home/urls.py
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from pathlib import Path
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from apps.home import views
from django.conf import settings

urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    path('uploads/',views.upload_files,name='upload_file'),
    path('process/<int:file_id>/', views.process_data, name='process_data'),
    path('visualize/<int:file_id>/', views.visualize_data, name='visualize_data'),
    path('getUploads/',views.get_uploads,name="get_uploads"),
    path('getDetails/<int:file_id>/',views.get_details,name="get_detail"),
    path('getPlots/<int:file_id>/',views.get_plots_details,name="get_plot"),
    path('reprompt/',views.reprompt,name="regenerate_plots"),
    path('add_insight/',views.add_insight,name="add_insight"),
    path('delete_insight/',views.delete_insight,name="delete_insight"),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),
]
