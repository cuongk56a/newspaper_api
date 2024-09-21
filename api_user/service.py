from base.service import BaseService
from api_user.constants import Roles
from api_user.models import Account, User
from itertools import groupby
from base.service import CloudinaryService
from api_post.models import Category
from django.db.models.functions import ExtractMonth
from django.db.models import Count

MONTH_LIST = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10',
              'Tháng 11', 'Tháng 12']

class UserService(BaseService):
    @classmethod
    def create_user(cls, validated_data):
        account = dict({
            # 'username': validated_data.pop('username'),
            'password': validated_data.pop('password'),
            'email': validated_data.pop('email')
        })
        if validated_data.get('role') is Roles.ADMIN.value:
            account = Account.objects.create_superuser(**account)
        elif validated_data.get('role') is Roles.USER.value:
            account = Account.objects.create_staff(**account)
        else:
            account = Account.objects.create_user(**account)
        validated_data.update({'account': account})
        return User.objects.create(**validated_data)

    @classmethod
    def get_all_users(cls):
        profiles = User.objects.filter().order_by('role')
        res_data = []
        for role, profile in groupby(profiles, lambda x: x.role):
            res_data.append((role, [i for i in profile]))
        return res_data

    @classmethod
    def upload_avatar(cls, image):
        upload_data = CloudinaryService.upload_avatar_user_image(image)
        return upload_data.get("url")