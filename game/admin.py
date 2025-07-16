from django.contrib import admin
from .models import Word, UserStatus, BattleRoom, BattleInvitation, BattleQuestion

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'type', 'level', 'language')
    list_filter = ('type', 'level', 'language')
    search_fields = ('word', 'translation')

@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_score', 'battles_won', 'battles_lost', 'last_activity')
    list_filter = ('status',)

@admin.register(BattleRoom)
class BattleRoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'player1', 'player2', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(BattleInvitation)
class BattleInvitationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(BattleQuestion)
class BattleQuestionAdmin(admin.ModelAdmin):
    list_display = ('battle', 'question_number', 'correct_answer', 'asked_at')
    list_filter = ('question_number',)

