from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import *

class BattleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.battle_uid = self.scope['url_route']['kwargs']['battle_uid']
        self.room_group_name = f'battle_{self.battle_uid}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send(json.dumps({'type': 'connect', 'message': 'connected'}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['action'] == 'submit_answer':
            result = await self.save_answer(data['user_uid'], data['question_uid'], data['answer'])
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'answer_feedback',
                'user_uid': data['user_uid'],
                'question_uid': data['question_uid'],
                'is_correct': result
            })

    async def answer_feedback(self, event):
        await self.send(json.dumps(event))

    @database_sync_to_async
    def save_answer(self, user_uid, question_uid, answer):
        user = User.objects.get(uid=user_uid)
        question = BattleQuestion.objects.get(uid=question_uid)
        is_correct = answer.strip().lower() == question.word.eng.lower()
        BattleAnswer.objects.create(question=question, user=user, answer=answer, is_correct=is_correct)
        return is_correct