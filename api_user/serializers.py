from rest_framework import serializers
from api_user.models import User, Account

class AccountSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%H:%M:%S %d-%m-%Y")
    last_login = serializers.DateTimeField(format="%H:%M:%S %d-%m-%Y")

    class Meta:
        model = Account
        fields = ['id', 'email', 'date_joined', 'last_login']


class UserSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'role', 'avatar', 'address',
                  'phone', 'birthday', 'account']

        extra_kwargs = {
            'full_name': {'required': False},
            'avatar': {'required': False},
            'phone': {'required': False},
            'birthday': {'required': False},
        }


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'role', 'avatar']


class UserShortWithEmailSerializer(UserShortSerializer):
    email = serializers.EmailField(source='account.email')

    class Meta:
        model = User
        fields = ['id', 'full_name', 'role','phone','birthday', 'address','avatar', 'email']
