from rest_framework import serializers
from api_user.models import User, Account
from api_user.constants import Roles

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'avatar', 'address', 'role', 'phone', 'birthday', 'password']
        extra_kwargs = {
            'avatar': {'required': False},
            'phone': {'required': False},
            'role': {'required': False},
            'birthday': {'required': False},
        }

    def create(self, validated_data):
        context = self.context.get('view')
        account = dict({
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email')
        })
        account = Account.objects.create_user(**account)
        validated_data.update({
            'account': account,
        })
        if context and context.action in ['admin']:
            validated_data.update({
              'role': Roles.ADMIN.value,
            })
        return User.objects.create(**validated_data)
    