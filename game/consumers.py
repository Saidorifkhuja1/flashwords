import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import models
from user.models import User
from .models import UserStatus, BattleRoom, BattleQuestion, BattleInvitation, Word
from django.utils import timezone
from datetime import timedelta
import random
import logging

logger = logging.getLogger(__name__)


class BattleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # DEBUG: Ma'lumotlarni tekshirish
        print(f"User: {self.user}")
        print(f"Is anonymous: {self.user.is_anonymous}")
        print(f"Session: {self.scope.get('session', {})}")
        print(f"Headers: {dict(self.scope.get('headers', []))}")

        # VAQTINCHALIK: Barcha ulanishlarni qabul qilish
        await self.accept()

        if self.user.is_anonymous:
            await self.send_error('Tizimga kirish talab qilinadi')
            return

        # Foydalanuvchi autentifikatsiya qilingan bo'lsa
        self.user_group_name = f"user_{self.user.id}"
        self.battle_room = None

        # Join user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Set user status to online
        await self.update_user_status('online')

        # Send initial status
        await self.send_status_update()

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and not self.user.is_anonymous:
            # Leave user group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

            # Set user status to offline
            await self.update_user_status('offline')

            # Leave battle room if in one
            await self.leave_battle_room()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'set_ready':
                await self.handle_set_ready(data)
            elif action == 'start_battle':
                await self.handle_start_battle(data)
            elif action == 'accept_invitation':
                await self.handle_accept_invitation(data)
            elif action == 'reject_invitation':
                await self.handle_reject_invitation(data)
            elif action == 'submit_answer':
                await self.handle_submit_answer(data)
            elif action == 'get_leaderboard':
                await self.send_leaderboard()
            elif action == 'cancel_search':
                await self.handle_cancel_search()
            else:
                await self.send_error('Unknown action')
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON data')
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send_error('Internal server error')

    async def handle_set_ready(self, data):
        """User sets status to ready for battle"""
        await self.update_user_status('ready')
        await self.send_status_update()

    async def handle_start_battle(self, data):
        """User starts looking for battle with specific word type"""
        word_type = data.get('word_type')
        if not word_type:
            await self.send_error('Word type is required')
            return

        # Check if user is already in battle
        user_status = await self.get_user_status()
        if user_status.status == 'in_battle':
            await self.send_error('You are already in a battle')
            return

        # Set user status to searching
        await self.update_user_status('searching')

        # Find random online user
        target_user = await self.find_random_online_user()
        if not target_user:
            await self.send_message({
                'type': 'searching',
                'message': 'Looking for opponent...'
            })
            return

        # Send invitation to target user
        invitation = await self.create_invitation(target_user, word_type)
        await self.send_invitation_to_user(target_user, invitation)

        await self.send_message({
            'type': 'invitation_sent',
            'to_user': target_user.username,
            'word_type': word_type,
            'invitation_id': invitation.id
        })

    async def handle_accept_invitation(self, data):
        """User accepts battle invitation"""
        invitation_id = data.get('invitation_id')
        if not invitation_id:
            await self.send_error('Invitation ID is required')
            return

        invitation = await self.get_invitation(invitation_id)
        if not invitation or invitation.status != 'pending':
            await self.send_error('Invalid or expired invitation')
            return

        # Check if invitation is for this user
        if invitation.to_user != self.user:
            await self.send_error('This invitation is not for you')
            return

        # Update invitation status
        await self.update_invitation_status(invitation, 'accepted')

        # Create battle room
        battle_room = await self.create_battle_room(invitation)
        self.battle_room = battle_room

        # Update both users status to in_battle
        await self.update_user_status('in_battle')
        await self.update_other_user_status(invitation.from_user, 'in_battle')

        # Notify sender that invitation was accepted
        await self.send_message_to_user(invitation.from_user, {
            'type': 'invitation_accepted',
            'by_user': self.user.username,
            'room_id': str(battle_room.room_id)
        })

        # Start battle
        await self.start_battle(battle_room)

    async def handle_reject_invitation(self, data):
        """User rejects battle invitation"""
        invitation_id = data.get('invitation_id')
        if not invitation_id:
            await self.send_error('Invitation ID is required')
            return

        invitation = await self.get_invitation(invitation_id)
        if not invitation or invitation.status != 'pending':
            await self.send_error('Invalid or expired invitation')
            return

        # Check if invitation is for this user
        if invitation.to_user != self.user:
            await self.send_error('This invitation is not for you')
            return

        # Update invitation status
        await self.update_invitation_status(invitation, 'rejected')

        # Set sender back to ready
        await self.update_other_user_status(invitation.from_user, 'ready')

        # Notify sender
        await self.send_message_to_user(invitation.from_user, {
            'type': 'invitation_rejected',
            'by_user': self.user.username
        })

        await self.send_message({
            'type': 'invitation_rejected_sent',
            'to_user': invitation.from_user.username
        })

    async def handle_submit_answer(self, data):
        """User submits answer to battle question"""
        room_id = data.get('room_id')
        answer = data.get('answer', '').strip()

        if not room_id or not answer:
            await self.send_error('Room ID and answer are required')
            return

        battle_room = await self.get_battle_room(room_id)
        if not battle_room or battle_room.status != 'active':
            await self.send_error('Invalid or inactive battle room')
            return

        # Check if user is in this battle
        if self.user not in [battle_room.player1, battle_room.player2]:
            await self.send_error('You are not in this battle')
            return

        # Get current question
        current_question = await self.get_current_question(battle_room)
        if not current_question:
            await self.send_error('No active question')
            return

        # Check if user already answered
        if self.user == battle_room.player1 and current_question.player1_answer:
            await self.send_error('You already answered this question')
            return
        elif self.user == battle_room.player2 and current_question.player2_answer:
            await self.send_error('You already answered this question')
            return

        # Submit answer
        await self.submit_answer(current_question, answer)

        # Notify both players about the answer
        await self.send_message_to_battle_room(battle_room, {
            'type': 'answer_submitted',
            'player': self.user.username,
            'question_number': current_question.question_number
        })

    async def handle_cancel_search(self):
        """User cancels battle search"""
        await self.update_user_status('online')
        await self.send_message({
            'type': 'search_cancelled'
        })

    async def start_battle(self, battle_room):
        """Start the battle and send first question"""
        # Update battle room status
        await self.update_battle_room_status(battle_room, 'active')

        # Send battle started message to both players
        await self.send_message_to_battle_room(battle_room, {
            'type': 'battle_started',
            'room_id': str(battle_room.room_id),
            'player1': battle_room.player1.username,
            'player2': battle_room.player2.username,
            'word_type': battle_room.word_type,
            'total_questions': 15
        })

        # Start question loop
        await self.start_question_loop(battle_room)

    async def start_question_loop(self, battle_room):
        """Start the 15-question loop"""
        try:
            for question_num in range(1, 16):  # 15 questions
                # Check if battle is still active
                battle_room = await self.get_battle_room(battle_room.room_id)
                if not battle_room or battle_room.status != 'active':
                    break

                # Get random word from specified type
                word = await self.get_random_word(battle_room.word_type)
                if not word:
                    logger.warning(f"No words found for type: {battle_room.word_type}")
                    continue

                # Create question
                question = await self.create_question(battle_room, word, question_num)

                # Send question to both players
                await self.send_question_to_battle_room(battle_room, question)

                # Wait 10 seconds for answers
                await asyncio.sleep(10)

                # Process answers and update scores
                await self.process_question_answers(question)

                # Send results to both players
                await self.send_question_results(battle_room, question)

                # Short break before next question
                if question_num < 15:  # No break after last question
                    await asyncio.sleep(2)

            # Battle finished
            await self.finish_battle(battle_room)
        except Exception as e:
            logger.error(f"Error in question loop: {str(e)}")
            await self.finish_battle(battle_room)

    async def finish_battle(self, battle_room):
        """Finish the battle and update user scores"""
        try:
            # Update battle room status
            await self.update_battle_room_status(battle_room, 'finished')

            # Determine winner
            winner = await self.determine_winner(battle_room)

            # Update user scores and stats
            await self.update_battle_results(battle_room, winner)

            # Send battle results
            await self.send_battle_results(battle_room, winner)

            # Set both users back to online
            await self.update_user_status('online')
            await self.update_other_user_status(
                battle_room.player1 if self.user == battle_room.player2 else battle_room.player2,
                'online'
            )
        except Exception as e:
            logger.error(f"Error finishing battle: {str(e)}")

    # Database helper methods
    @database_sync_to_async
    def update_user_status(self, status):
        user_status, created = UserStatus.objects.get_or_create(user=self.user)
        user_status.status = status
        user_status.last_activity = timezone.now()
        user_status.save()
        return user_status

    @database_sync_to_async
    def update_other_user_status(self, user, status):
        user_status, created = UserStatus.objects.get_or_create(user=user)
        user_status.status = status
        user_status.last_activity = timezone.now()
        user_status.save()
        return user_status

    @database_sync_to_async
    def find_random_online_user(self):
        # Find users that are online or ready (not in battle or searching)
        online_users = UserStatus.objects.filter(
            status__in=['online', 'ready']
        ).exclude(user=self.user)

        if online_users.exists():
            return random.choice(online_users).user
        return None

    @database_sync_to_async
    def create_invitation(self, to_user, word_type):
        return BattleInvitation.objects.create(
            from_user=self.user,
            to_user=to_user,
            word_type=word_type
        )

    @database_sync_to_async
    def get_invitation(self, invitation_id):
        try:
            return BattleInvitation.objects.get(id=invitation_id)
        except BattleInvitation.DoesNotExist:
            return None

    @database_sync_to_async
    def update_invitation_status(self, invitation, status):
        invitation.status = status
        invitation.responded_at = timezone.now()
        invitation.save()
        return invitation

    @database_sync_to_async
    def create_battle_room(self, invitation):
        return BattleRoom.objects.create(
            player1=invitation.from_user,
            player2=invitation.to_user,
            word_type=invitation.word_type
        )

    @database_sync_to_async
    def get_battle_room(self, room_id):
        try:
            return BattleRoom.objects.get(room_id=room_id)
        except BattleRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def update_battle_room_status(self, battle_room, status):
        battle_room.status = status
        if status == 'active':
            battle_room.started_at = timezone.now()
        elif status == 'finished':
            battle_room.finished_at = timezone.now()
        battle_room.save()
        return battle_room

    @database_sync_to_async
    def get_random_word(self, word_type):
        words = Word.objects.filter(type=word_type)
        if words.exists():
            return random.choice(words)
        return None

    @database_sync_to_async
    def create_question(self, battle_room, word, question_number):
        return BattleQuestion.objects.create(
            battle=battle_room,
            word=word,
            question_number=question_number,
            correct_answer=word.translation
        )

    @database_sync_to_async
    def get_current_question(self, battle_room):
        return BattleQuestion.objects.filter(
            battle=battle_room
        ).order_by('-question_number').first()

    @database_sync_to_async
    def submit_answer(self, question, answer):
        if self.user == question.battle.player1:
            question.player1_answer = answer
            question.player1_answer_time = timezone.now()
        else:
            question.player2_answer = answer
            question.player2_answer_time = timezone.now()
        question.save()
        return question

    @database_sync_to_async
    def process_question_answers(self, question):
        # Check answers and determine winner
        player1_correct = (question.player1_answer and
                         question.player1_answer.lower().strip() == question.correct_answer.lower().strip())
        player2_correct = (question.player2_answer and
                         question.player2_answer.lower().strip() == question.correct_answer.lower().strip())

        if player1_correct and player2_correct:
            # Both correct, first one wins
            if question.player1_answer_time and question.player2_answer_time:
                if question.player1_answer_time <= question.player2_answer_time:
                    question.winner = question.battle.player1
                    question.battle.player1_score += 1
                else:
                    question.winner = question.battle.player2
                    question.battle.player2_score += 1
            elif question.player1_answer_time:
                question.winner = question.battle.player1
                question.battle.player1_score += 1
            elif question.player2_answer_time:
                question.winner = question.battle.player2
                question.battle.player2_score += 1
        elif player1_correct:
            question.winner = question.battle.player1
            question.battle.player1_score += 1
        elif player2_correct:
            question.winner = question.battle.player2
            question.battle.player2_score += 1

        question.save()
        question.battle.save()
        return question

    @database_sync_to_async
    def determine_winner(self, battle_room):
        if battle_room.player1_score > battle_room.player2_score:
            battle_room.winner = battle_room.player1
        elif battle_room.player2_score > battle_room.player1_score:
            battle_room.winner = battle_room.player2
        # If tied, no winner
        battle_room.save()
        return battle_room.winner

    @database_sync_to_async
    def update_battle_results(self, battle_room, winner):
        # Update player1 stats
        status1, created = UserStatus.objects.get_or_create(user=battle_room.player1)
        status1.total_score += battle_room.player1_score
        if winner == battle_room.player1:
            status1.battles_won += 1
        elif winner == battle_room.player2:
            status1.battles_lost += 1
        status1.save()

        # Update player2 stats
        status2, created = UserStatus.objects.get_or_create(user=battle_room.player2)
        status2.total_score += battle_room.player2_score
        if winner == battle_room.player2:
            status2.battles_won += 1
        elif winner == battle_room.player1:
            status2.battles_lost += 1
        status2.save()

    @database_sync_to_async
    def get_leaderboard(self):
        return list(UserStatus.objects.order_by('-total_score')[:10].values(
            'user__username', 'total_score', 'battles_won', 'battles_lost'
        ))

    @database_sync_to_async
    def leave_battle_room(self):
        # Find active battle room and mark as finished
        active_battles = BattleRoom.objects.filter(
            status='active'
        ).filter(
            models.Q(player1=self.user) | models.Q(player2=self.user)
        )

        for battle in active_battles:
            battle.status = 'finished'
            battle.finished_at = timezone.now()
            battle.save()

    # Message sending methods
    async def send_status_update(self):
        status = await self.get_user_status()
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': status.status,
            'total_score': status.total_score,
            'battles_won': status.battles_won,
            'battles_lost': status.battles_lost
        }))

    async def send_message(self, message):
        await self.send(text_data=json.dumps(message))

    async def send_error(self, error_message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message
        }))

    async def send_invitation_to_user(self, user, invitation):
        await self.channel_layer.group_send(
            f"user_{user.id}",
            {
                'type': 'battle_invitation',
                'invitation_id': invitation.id,
                'from_user': self.user.username,
                'word_type': invitation.word_type,
                'created_at': invitation.created_at.isoformat()
            }
        )

    async def send_message_to_user(self, user, message):
        await self.channel_layer.group_send(
            f"user_{user.id}",
            message
        )

    async def send_message_to_battle_room(self, battle_room, message):
        await self.channel_layer.group_send(
            f"user_{battle_room.player1.id}",
            message
        )
        await self.channel_layer.group_send(
            f"user_{battle_room.player2.id}",
            message
        )

    async def send_question_to_battle_room(self, battle_room, question):
        message = {
            'type': 'battle_question',
            'question_number': question.question_number,
            'word': question.word.word,
            'language': question.word.language,
            'image': question.word.image.url if question.word.image else None,
            'transcript': question.word.transcript,
            'time_limit': 10,
            'total_questions': 15
        }
        await self.send_message_to_battle_room(battle_room, message)

    async def send_question_results(self, battle_room, question):
        message = {
            'type': 'question_result',
            'question_number': question.question_number,
            'correct_answer': question.correct_answer,
            'winner': question.winner.username if question.winner else None,
            'player1_answer': question.player1_answer,
            'player2_answer': question.player2_answer,
            'player1_score': battle_room.player1_score,
            'player2_score': battle_room.player2_score,
            'player1_username': battle_room.player1.username,
            'player2_username': battle_room.player2.username
        }
        await self.send_message_to_battle_room(battle_room, message)

    async def send_battle_results(self, battle_room, winner):
        message = {
            'type': 'battle_finished',
            'winner': winner.username if winner else None,
            'final_scores': {
                'player1': {
                    'username': battle_room.player1.username,
                    'score': battle_room.player1_score
                },
                'player2': {
                    'username': battle_room.player2.username,
                    'score': battle_room.player2_score
                }
            },
            'room_id': str(battle_room.room_id)
        }
        await self.send_message_to_battle_room(battle_room, message)

    async def send_leaderboard(self):
        leaderboard = await self.get_leaderboard()
        await self.send(text_data=json.dumps({
            'type': 'leaderboard',
            'data': leaderboard
        }))

    # Channel layer message handlers
    async def battle_invitation(self, event):
        await self.send(text_data=json.dumps(event))

    async def battle_question(self, event):
        await self.send(text_data=json.dumps(event))

    async def question_result(self, event):
        await self.send(text_data=json.dumps(event))

    async def battle_finished(self, event):
        await self.send(text_data=json.dumps(event))

    async def invitation_rejected(self, event):
        await self.send(text_data=json.dumps(event))

    async def invitation_accepted(self, event):
        await self.send(text_data=json.dumps(event))

    async def answer_submitted(self, event):
        await self.send(text_data=json.dumps(event))

    # Helper methods
    @database_sync_to_async
    def get_user_status(self):
        status, created = UserStatus.objects.get_or_create(user=self.user)
        return status

    def get_opponent_username(self, battle_room):
        if self.user == battle_room.player1:
            return battle_room.player2.username
        return battle_room.player1.username


