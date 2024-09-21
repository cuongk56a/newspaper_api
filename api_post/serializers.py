from rest_framework import serializers
from rest_framework.fields import UUIDField
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.text import slugify
from .models import Post, Category, Source, Contents, Keyword
from .constants import TIME_STRINGS
from .service import PostService
from api_user.serializers import UserShortSerializer
from api_user.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description']
        extra_kwargs = {
            'description': {'required': False},
        }

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contents
        fields = ['id', 'title', 'paragraph', 'image', 'description_img', 'index']
        extra_kwargs = {
            'paragraph': {'required': False},
        }

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['id', 'keyword']

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'title', 'domain']
        extra_kwargs = {
            'domain': {'required': False},
        }

class SourceShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'title']

class PublishDateField(serializers.Field):
    def to_representation(self, value):
        time = timesince(value, timezone.now(), time_strings=TIME_STRINGS)
        time = time.split(",")  # Split the string at the comma
        time = time[0].strip() + " trước"
        return time

class PostShortSerializer(serializers.ModelSerializer):
    category = CategorySerializer(required=True)
    source = SourceSerializer(required=True)
    keywords = KeywordSerializer(many=True, required=False)
    # publish_date = PublishDateField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "thumbnail",
            "category",
            "source",
            "likes",
            "summary",
            "publish_date",
            "status",
            "likes",
            "views",
            "keywords",
        ]

class PostSerializer(serializers.ModelSerializer):
    category_ids = serializers.PrimaryKeyRelatedField(required=True, write_only=True, many=False,
                                                        queryset=Category.objects.all(),
                                                        pk_field=UUIDField(format='hex'),
                                                        source='category')
    source_id = serializers.PrimaryKeyRelatedField(required=False, write_only=True,
                                                        queryset=Source.objects.all(),
                                                        pk_field=UUIDField(format='hex'),
                                                        source='source')
    source = SourceSerializer(required=False)
    category = CategorySerializer(read_only=True, required=False)
    contents = ContentSerializer(many=True, required=False)
    keywords = KeywordSerializer(many=True, required=False)
    # publish_date = PublishDateField(required=False)
    user = UserShortSerializer(required=False)
    user_id = serializers.PrimaryKeyRelatedField(required=False, write_only=True,
                                                 queryset=User.objects.all(),
                                                 pk_field=UUIDField(format='hex'),
                                                 source='user')

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "thumbnail",
            "category_ids",
            "source_id",
            "category",
            "source",
            "likes",
            "summary",
            "author",
            "publish_date",
            "status",
            "likes",
            "contents",
            "keywords",
            "views",
            "user",
            "user_id",
            "description"
        ]
        extra_kwargs = {
            'thumbnail': {'required': False},
            'source': {'required': False},
            'summary': {'required': False},
            'status': {'required': False},
            'publish_date': {'required': False},
            'description': {'required': False},
        }

    def to_internal_value(self, data):
        context = self.context.get('view')
        if context and context.action in ['create', 'update']:
            keywords = data.getlist('keywords') if "keywords" in data else []
            keywords_data = [{'keyword': keyword} for keyword in keywords]
            data = data.dict()
            data.pop('keywords') if "keywords" in data else data
            if context.action == 'create':
                avatar = context.request.FILES.get('thumbnail')
                avatar_link = PostService.upload_avatar(avatar)
                data.update({'thumbnail': avatar_link})
            data.update({'keywords': keywords_data})
            data.update({'user_id': context.request.user.user.id})
        data_res = super().to_internal_value(data)
        return data_res

    def create(self, validated_data):
        return PostService.create_post(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('keywords') if "keywords" in validated_data else []
        if 'title' in validated_data:
            instance.slug = slugify(f"{instance.title[0:30]} {instance.id.hex[:5]}")
            data_res = super().update(instance, validated_data)
            return data_res
        return super().update(instance, validated_data)


