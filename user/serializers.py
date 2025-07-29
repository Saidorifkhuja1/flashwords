from rest_framework import serializers
from .models import User

class SendVerificationCodeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)
    last_name = serializers.CharField(max_length=250)
    phone_number = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=4, write_only=True)
    role = serializers.ChoiceField(choices=User.ROlE_CHOICES, default='student', required=False)

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'uid', 'username', 'phone_number', 'name','bio','notification_token', 'last_name', 'email',
            'avatar', 'mini_avatar', 'role', 'status'
        ]



class UserUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    mini_avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'name', 'last_name', 'email','notification_token',
            'avatar', 'mini_avatar', 'role', 'status'
        ]
        read_only_fields = ['phone_number']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



# class UserUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             'name', 'last_name', 'email',
#             'avatar', 'mini_avatar', 'role', 'status'
#         ]
#         read_only_fields = ['phone_number']
#
#     def update(self, instance, validated_data):
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance

class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("The new password cannot be the same as the old password.")
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(min_length=6)



class UserSerializerSearch(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uid', 'name', 'bio','notification_token',  'last_name', 'mini_avatar', 'username', 'avatar', 'email', 'role']