
from django.contrib import admin
from .models import Quiz

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'uid')
    readonly_fields = ('uid',)
    search_fields = ('title', 'user__username', 'uid')
    list_filter = ('user',)
