#apps/home/models.py
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    metadata = models.JSONField(null=True, blank=True)  # Lưu metadata của file
    processed = models.BooleanField(default=False)
    validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    plotImages=models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.file.name

