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
        self.avenue_dir = os.path.join('data', self.avenue)
        self.meta_path = os.path.join(self.avenue_dir, 'meta.yaml')
        self.meta_parse_path = os.path.join(self.avenue_dir, 'meta-parse.yaml')

        self.dl_status = self.load_meta(self.meta_path)  # type: Dict[str, bool]
        self.parse_status = self.load_meta(self.meta_parse_path)  # type: Dict[str, bool]

        os.makedirs(self.avenue_dir, exist_ok=True)

    @staticmethod
    def load_meta(path):
        if os.path.exists(path):
            return handler.yaml_load(path)
        return {}

    def save_meta(self, status):
        # Save the status to the meta file
        self.dl_status = status
        handler.yaml_save(status, self.meta_path)

    def save_meta_parse(self, status):
        self.parse_status = status
        handler.yaml_save(status, self.meta_parse_path)

    def has_downloaded(self, link):
        return self.dl_status.get(link, False)

    def has_parsed(self, link):
        return self.parse_status.get(link, False)

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

    def crawl(self, skip_parse=False):
        soup = self.fetch()
        if soup is None:
            return

        links = self.parse(soup)
        current_dl_status = dict()
        current_status_parse = dict()

        for link in links:
            crawler = PageCrawler(link)

            if self.has_downloaded(link) and not self.always_update:
                soup = None
            else:
                soup = crawler.crawl()
            current_dl_status[link] = True
            self.save_meta(current_dl_status)

            time.sleep(1)

            if skip_parse or (self.has_parsed(link) and not self.always_update):
                continue

            if soup is None:
                content = crawler.load_html()
                soup = BeautifulSoup(content, 'lxml')

            crawler.parse(soup)
            current_status_parse[link] = True
            self.save_meta_parse(current_status_parse)
