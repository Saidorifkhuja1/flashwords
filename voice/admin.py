from django.contrib import admin
from .models import Voice

@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    list_display = ['title']

