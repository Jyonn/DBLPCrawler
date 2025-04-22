import os
import time
from typing import Dict

import requests
from bs4 import BeautifulSoup

import handler
import utils
from page_crawler import PageCrawler


class AvenueCrawler:
    def __init__(self, index_url, always_update=False):
        self.index_url = index_url  # https://dblp.org/db/conf/aaai/index.html
        self.always_update = always_update

        self.avenue = self.extract_meta()  # Extract conf-aaai
        self.meta_path = os.path.join(self.avenue, 'meta.yaml')
        self.status = self.load_meta()  # type: Dict[str, bool]

        os.makedirs(self.avenue, exist_ok=True)

    def load_meta(self):
        if os.path.exists(self.meta_path):
            return handler.yaml_load(self.meta_path)
        return {}

    def save_meta(self, status):
        # Save the status to the meta file
        self.status = status
        handler.yaml_save(status, self.meta_path)

    def has_processed(self, link):
        return self.status.get(link, False)

    def extract_meta(self):
        # https://dblp.org/db/conf/aaai/index.html -> extract conf and aaai
        parts = self.index_url.split('/')
        avenue = parts[-3] + '-' + parts[-2]
        return avenue


    def fetch(self):
        # 获取会议主页
        response = requests.get(self.index_url, headers=utils.headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'lxml')
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None

    def parse(self, soup):
        links = soup.find_all('a', class_='toc-link')
        return [link['href'] for link in links if 'href' in link.attrs]

    def crawl(self):
        soup = self.fetch()
        if soup is None:
            return

        links = self.parse(soup)
        current_status = dict()

        for link in links:
            if self.has_processed(link) and not self.always_update:
                current_status[link] = True
                continue

            # 处理每个链接
            crawler = PageCrawler(link)
            crawler.crawl()
            current_status[link] = True

            time.sleep(10)

        self.save_meta(current_status)


# 示例用法
# crawler = AvenueCrawler('https://dblp.org/db/conf/aaai/index.html')
# crawler.crawl()
