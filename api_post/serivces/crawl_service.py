import re

import requests
from bs4 import BeautifulSoup
from django.db import transaction
from base.service import BaseService
from bs4.element import Tag
from api_post.models import Keyword, Post, Contents, Source
from api_post.service import PostService, ContentService, KeywordService
from .utils import Util, Data_Process
# from keras import models
# from keras.layers import TFSMLayer
import pickle
import core
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

root_url_dantri = "https://dantri.com.vn/tin-moi-nhat.htm"
root_url_vietnamnet = "https://vietnamnet.vn"

def remove_space(string):
    string = string.replace("\xa0", " ").strip()
    string = string.replace("\r\n", "").strip()
    return string


# model_file = r"D:\web_read_newspaper\newspaper_api\api_post\serivces\AI\models\model_test1"
# encoder_file = r"D:\web_read_newspaper\newspaper_api\api_post\serivces\AI\encoder.pkl"
model_file = os.path.join(core.settings.BASE_DIR, './api_post/serivces/AI/models/model_test1')
encoder_file = os.path.join(core.settings.BASE_DIR, './api_post/serivces/AI/encoder.pkl')
# model = models.load_(model_file, call_endpoint='serving_default')

with open(encoder_file, 'rb') as f:
    encoder = pickle.load(f)


class CrawlService(BaseService):

    @classmethod
    def crawl_from_url_dantri(
            cls, url=root_url_dantri
    ):
        page = requests.get(root_url_dantri)
        soup = BeautifulSoup(page.content, 'html.parser')
        cards = soup.select('[class*="article-list article-item"]')[0:20]
        thumbnails = soup.select('[class*="article-thumb"] img')[0:20]
        arr_news = []
        for idx, item in enumerate(cards):
            try:
                link = url + item.find("a").get("href")[0:255]
                page_detail = requests.get(link)
                soup_detail = BeautifulSoup(page_detail.content, "html.parser")
                news = {
                    "source": link[0:255],
                    "category": remove_space(soup_detail.select('a[data-content-piece*="article-breadcrumb-position_1"]')[0].text)[0:255],
                    "title":
                        remove_space(soup_detail.select('[class*="title-page"]')[0].text)[0:255]
                    ,
                    "excerpt": remove_space(soup_detail.select('[class*="singular-sapo"]')[0].text)[0:255],
                    "thumbnail": thumbnails[idx].get("src")[0:255],
                    "content": [],
                    "keyword": list(
                        map(
                            lambda x: remove_space(x.text),
                            soup_detail.select('a[data-content-name*="article-tags"]'),
                        )
                    ),
                }
                contents = soup_detail.select('[class*="singular-content"]')[0]
                i = 0
                below_img = False
                item = {
                    "title": "",
                    "paragraph": [],
                    "description_img": "",
                    "image": "",
                    "order": i,
                }
                for child in contents.children:
                    paragraph = {
                        "text": "",
                        "below_img": False
                    }
                    if isinstance(child, Tag) and type(child.find("strong")) != type(None):
                        if item["paragraph"]:
                            news["content"].append(item)
                            i += 1
                            item = {
                                "title": "",
                                "paragraph": [],
                                "description_img": "",
                                "image": "",
                                "order": i,
                            }
                        item["title"] = remove_space(child.find("strong").text)[0:255]
                        if child.name == "p":
                            paragraph["text"] = remove_space(child.text)[0:255]
                            paragraph["below_img"] = below_img
                            item["paragraph"].append(paragraph)
                    elif isinstance(child, Tag) and child.name == "p":
                        if item["paragraph"] and item["description_img"]:
                            news["content"].append(item)
                            i += 1
                            item = {
                                "title": "",
                                "paragraph": [],
                                "description_img": "",
                                "image": "",
                                "order": i,
                            }
                        paragraph["text"] = remove_space(child.text)[0:255]
                        paragraph["below_img"] = below_img
                        item["paragraph"].append(paragraph)
                    elif isinstance(child, Tag) and child.name == "figure":
                        item["description_img"] = remove_space(child.find("figcaption").text)
                        if type(child.find("img")) != type(None):
                            item["image"] = child.find("img").get("data-src")
                            if item["paragraph"]:
                                item["paragraph"][-1]["below_img"] = True
                            else:
                                news["content"].append(item)
                                i += 1
                                item = {
                                    "title": "",
                                    "paragraph": [],
                                    "description_img": "",
                                    "image": "",
                                    "order": i,
                                }

                if item["paragraph"]:
                    news["content"].append(item)
                    i += 1
                arr_news.append(news)
            except:
                continue
        return arr_news

    @classmethod
    def crawl_from_url_vietnamnet(
            cls, url="https://vietnamnet.vn/tin-moi-nong"
    ):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        cards = soup.select('[class*="horizontalPost"][class*="version-news"]')[0:20]
        thumbnails = soup.select('picture img')
        arr_news = []
        for idx, item in enumerate(cards):
            try:
                link = root_url_vietnamnet + item.find("a").get("href")
                page_detail = requests.get(link)
                soup_detail = BeautifulSoup(page_detail.content, "html.parser")
                news = {
                    "source": link[0:255],
                    "title":
                        remove_space(soup_detail.select('[class*="content-detail-title"]')[0].text)[0:255]
                    ,
                    "category": remove_space(soup_detail.select('div[class*="bread-crumb-detail sm-show-time"] a')[1].text)[0:255],
                    "excerpt": remove_space(soup_detail.select('[class*="content-detail-sapo"]')[0].text)[0:255],
                    "thumbnail": thumbnails[idx].get("data-srcset") or thumbnails[idx].get("src")[0:255],
                    "content": [],
                    "keyword": list(
                        map(
                            lambda x: remove_space(x.text),
                            soup_detail.select('[class*="tag-content"] a'),
                        )
                    ),
                }
                contents = soup_detail.select('[class*="main-content"]')[0]
                i = 0
                below_img = False
                item = {
                    "title": "",
                    "paragraph": [],
                    "description_img": "",
                    "image": "",
                    "order": i,
                }
                for child in contents.children:
                    paragraph = {
                        "text": "",
                        "below_img": False
                    }
                    if isinstance(child, Tag) and type(child.find("strong")) != type(None):
                        if item["paragraph"]:
                            news["content"].append(item)
                            i += 1
                            item = {
                                "title": "",
                                "paragraph": [],
                                "description_img": "",
                                "image": "",
                                "order": i,
                            }
                        item["title"] = remove_space(child.find("strong").text)
                        if child.name == "p":
                            paragraph["text"] = remove_space(child.text)[0:255]
                            paragraph["below_img"] = below_img
                            item["paragraph"].append(paragraph)
                    elif isinstance(child, Tag) and child.name == "p":
                        if item["paragraph"] and item["description_img"]:
                            news["content"].append(item)
                            i += 1
                            item = {
                                "title": "",
                                "paragraph": [],
                                "description_img": "",
                                "image": "",
                                "order": i,
                            }
                        paragraph["text"] = remove_space(child.text)[0:255]
                        paragraph["below_img"] = below_img
                        item["paragraph"].append(paragraph)
                    elif isinstance(child, Tag) and child.name == "figure":
                        item["description_img"] = remove_space(child.find("figcaption").text)
                        if type(child.find("img")) != type(None):
                            item["image"] = child.find("img").get("src")
                            if item["paragraph"]:
                                item["paragraph"][-1]["below_img"] = True
                            else:
                                news["content"].append(item)
                                i += 1
                                item = {
                                    "title": "",
                                    "paragraph": [],
                                    "description_img": "",
                                    "image": "",
                                    "order": i,
                                }
                if item["paragraph"]:
                    news["content"].append(item)
                    i += 1
                arr_news.append(news)
            except:
                continue
        return arr_news

    @classmethod
    def craw_and_save_data_in_db(cls, data):
        # try:
        #     data_class = Data_Process(data)
        #     input_data = data_class.convert_data()
        # except Exception as e:
        #     print("Exception: " + e)
        # scores = model.predict(input_data).argmax(axis=-1)
        # category = encoder.inverse_transform(scores)
        try:
            with transaction.atomic():
                data, news_data, source = PostService.create_list_posts(data)
                Source.objects.bulk_create(
                    source, ignore_conflicts=True
                )

                news_objs = Post.objects.bulk_create(
                    news_data, ignore_conflicts=True
                )
                keyword_data = KeywordService.create_list_keyword(data, news_objs)
                Keyword.objects.bulk_create(keyword_data, ignore_conflicts=True)
                content_data = ContentService.create_list_content(data, news_objs)
                Contents.objects.bulk_create(content_data, ignore_conflicts=True)
        except Exception as e:
            print("Error: ", e)
        return data

def thread_crawl_dantri():
    data_dantri = CrawlService.crawl_from_url_dantri()
    CrawlService.craw_and_save_data_in_db(data_dantri)

def thread_crawl_vietnamnet():
    data_vietnamnet = CrawlService.crawl_from_url_vietnamnet()
    CrawlService.craw_and_save_data_in_db(data_vietnamnet)
