from rest_framework import serializers
from tes_app.models import User, FriendRequest, UserActivity

class RegisterSerialization(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    address = serializers.CharField(required=True)
    pin_code = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class LoginSerialization(serializers.Serializer):
    email = serializers.CharField(required = True)
    password = serializers.CharField(required = True)

class LogOutSerializer(serializers.Serializer):
    pass

class UpdateProfileImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)

class UserSerial(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'name', 'address', 'pin_code', 'city', 'country', 'image']

class CreateUserSerial(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    address = serializers.CharField(required=True)
    pin_code = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)

class ChangePasswordSerial(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

class Forgetpasswordserial(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)
    redirecturl = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["email", "redirecturl"]

class ResetPasswordSeriel(serializers.Serializer):
    token=serializers.CharField(max_length=500)
    new_password = serializers.CharField(max_length=30, min_length=4)
    confirm_password = serializers.CharField(max_length=20, min_length=4)

class AssignRoleSerialization(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50)

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'

class ModeSerial(serializers.Serializer):
    receiver = serializers.IntegerField()

class AcceptSerial(serializers.Serializer):
    status = serializers.CharField()

class PendingFriendRequestSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender_username', 'created_at']
    
class UserActivitySerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    target_username = serializers.CharField(source='target_user.username', read_only=True)

    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'action', 'action_display', 'target_username', 'created_at']