import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Tag
# from base.utils import Util

root_url_vietnamnet= "https://vietnamnet.vn"
root_url_vietnamnet_tinnong = "https://vietnamnet.vn/tin-moi-nong"

def remove_space(string):
  string = string.replace("\xa0", " ").strip()
  string = string.replace("\r\n", "").strip()
  return string

page = requests.get(root_url_vietnamnet_tinnong)
soup = BeautifulSoup(page.content, 'html.parser')
cards = soup.select('[class*="horizontalPost"][class*="version-news"]')[0:20]
thumbnails = soup.select('picture img')
arr_news = []
for idx, item in enumerate(cards):
  try:
      link = root_url_vietnamnet + item.find("a").get("href")
      page_detail = requests.get(link)
      soup_detail = BeautifulSoup(page_detail.content, "html.parser")
      news = {
          "source": link,
          "title":
            remove_space(soup_detail.select('[class*="content-detail-title"]')[0].text)
          ,
          "excerpt": remove_space(soup_detail.select('[class*="content-detail-sapo"]')[0].text),
          "thumbnail": thumbnails[idx].get("data-srcset") or thumbnails[idx].get("src"),
          "content": [],
          "keyword": list(
              map(
                  lambda x: remove_space(x.text),
                  soup_detail.select('[class*="tag-cotnent"] a'),
              )
          ),
          "created_at": remove_space(soup_detail.select('[class*="bread-crumb-detail__time"]')[0].text)
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
                  paragraph["text"] = remove_space(child.text)
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
              paragraph["text"] = remove_space(child.text)
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
      print(len(arr_news))
  except:
      continue
  
with open("./data-vietnamnet.json", "w", encoding='utf-8', newline='') as jsonfile:
    for news in arr_news:
        json_object = json.dumps(news, ensure_ascii=False, indent=4)
        jsonfile.write(json_object)
