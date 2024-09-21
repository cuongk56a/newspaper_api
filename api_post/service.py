from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.utils.text import slugify
from django.db.models.functions import Lower
from base.service import BaseService
from .constants import PostStatus
from .models import Post, Contents, Keyword, PostVector, Source, Category

MONTH_LIST = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10',
              'Tháng 11', 'Tháng 12']

class ContentService(BaseService):
    @classmethod
    def create_list_content(cls, data, news_objs):
        content_data = []
        for _idx, news in enumerate(data):
            contents = news.get("content")
            for content in contents:
                item = {
                    "post": news_objs[_idx],
                    "title": content.get("title"),
                    "paragraph": content.get("paragraph"),
                    "description_img": content.get("description_img"),
                    "image": content.get("image"),
                    "index": content.get("order"),
                }
                content_data.append(Contents(**item))
        return content_data
    
class KeywordService(BaseService):
    @classmethod
    def create_list_keyword(cls, data, news_objs):
        keyword_data = []
        for _idx, news in enumerate(data):
            keywords = news.get("keyword")
            for keyword in keywords:
                item = {"post": news_objs[_idx], "keyword": keyword}
                keyword_data.append(item)
        keyword_objs = (Keyword(**keyword) for keyword in keyword_data)
        return keyword_objs

    @classmethod
    def create_list_keyword_for_post(cls, data, post_id):
        keyword_data = []
        for keyword in data:
            item = {"post_id": post_id, "keyword": keyword.get("keyword")}
            keyword_data.append(item)
        keyword_objs = (Keyword(**keyword) for keyword in keyword_data)
        Keyword.objects.bulk_create(keyword_objs, ignore_conflicts=True)
        return keyword_objs

class PostVectorService(BaseService):
    @classmethod
    def create_list_post_vector(cls, data, news_objs):
        post_data = []
        for _idx, news in enumerate(news_objs):
            item = {"post": news, "vector": data[_idx]}
            post_data.append(item)
        post_vector_objs = (PostVector(**post_vector) for post_vector in post_data)
        return post_vector_objs

class PostService(BaseService):
    def __init__(self):
            self.month = timezone.now().month

    @classmethod
    def create_post(cls, data):
        keyword = data.pop('keywords') if "keywords" in data else []
        post_obj = Post(**data)
        post_obj.slug = slugify(f"{post_obj.title[:30]} {post_obj.id.hex[:5]}")
        post_obj.save()
        KeywordService.create_list_keyword_for_post(keyword, post_obj.id)
        return post_obj
    
    @classmethod
    def create_list_posts(cls, arr_posts, topic):
        category = Category.objects
        in_db_sources = Source.objects.values_list("domain", flat=True)
        source_crawl = list(
            filter(lambda x: x.get("source") not in in_db_sources, arr_posts)
        )
        objs = []
        sources = []
        if source_crawl:
            for index, post in enumerate(source_crawl):
                source = Source(title=post.get("title"), domain=post.get("source"))
                sources.append(source)
                objs.append(Post(
                    title=post.get("title"),
                    thumbnail=post.get("thumbnail"),
                    category=category.filter(title=topic[index]).first(),
                    slug=slugify(post.get('title')[:30]),
                    source=source,
                    summary=post.get("excerpt"),
                    status='PUBLISHED',
                    publish_date=timezone.now
                ))
        return source_crawl, objs, sources
  
    @classmethod
    def get_list_post_by_category(cls, params=None):
        ft = Q(status=PostStatus.PUBLISHED.value)
        ft &= Q(user__isnull=True)
        if params.get('categories'):
            topic_ids = params.get('categories')
            ft &= Q(category__id=topic_ids)
        if params.get('search'):
            search_string = params.get('search')
            ft &= (Q(category__title__icontains=search_string) | Q(
                title_lower__contains=str(search_string).strip().lower()))
        if params.get('start_date') and params.get('end_date'):
            ft &= Q(publish_date__range=[params.get('start_date'), params.get('end_date')])
        posts = Post.objects.annotate(title_lower=Lower('title')).filter(ft).prefetch_related(
                'category', 'user', 'source','keywords').order_by('-publish_date')
        return posts
  
    @classmethod
    def update_status_post(cls, instance):
        posts = Post.objects.filter(id__in=instance)
        post_update = []
        for post in posts:
            post.status = PostStatus.PUBLISHED.value
            post_update.append(post)
        Post.objects.bulk_update(post_update, ["status"])
  
      