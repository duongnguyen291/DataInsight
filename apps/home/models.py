#apps/home/models.py
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    metadata = models.JSONField(null=True, blank=True)  # Stores file metadata
    processed = models.BooleanField(default=False)
    validated = models.BooleanField(default=False)
    plotImages = models.CharField(max_length=255, null=True, blank=True)  # ✅ Add this field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name
