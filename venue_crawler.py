import os
import time
from typing import Dict

import requests
from bs4 import BeautifulSoup

import handler
import utils
from page_crawler import PageCrawler


class VenueType:
    CONF = 'conf'
    JOURNAL = 'journals'

    ALL = [CONF, JOURNAL]

    @staticmethod
    def parse_conf_links(soup):
        links = soup.find_all('a', class_='toc-link')
        return [link['href'] for link in links if 'href' in link.attrs]

    @staticmethod
    def parse_journals_links(soup):
        main_div = soup.find('div', id='main')
        uls = []
        for child in main_div.children:
            if child.name == 'ul':
                uls.append(child)

        links = []
        for ul in uls:
            current_links = ul.find_all('a')
            current_links = [link['href'] for link in current_links if 'href' in link.attrs]
            links.extend(current_links)
        return links

    @classmethod
    def parse_links(cls, soup, venue_type):
        func = getattr(cls, f'parse_{venue_type}_links')
        return func(soup)


class VenueCrawler:
    """Crawl conference or journal pages from DBLP"""

    def __init__(
            self,
            index_url,
            always_update=False,
            strict_prefix=False,
    ):
        """
        :param index_url: venue index page, e.g., https://dblp.org/db/conf/aaai/index.html
        :param always_update: crawl even if already downloaded
        :param strict_prefix: crawl when page name starts with the venue type, e.g., https://dblp.org/db/conf/aaai/aaaixxx.html
        """

        self.index_url = index_url
        self.always_update = always_update
        self.strict_prefix = strict_prefix

        self.venue_type, self.venue_name = self.extract_meta()  # Extract conf-aaai
        assert self.venue_type in VenueType.ALL, ValueError(f'Invalid venue type: {self.venue_type}')

        self.venue_dir = os.path.join(utils.root_dir, f'{self.venue_type}-{self.venue_name}')
        self.meta_download_path = os.path.join(self.venue_dir, '.meta.download.yaml')
        self.meta_parse_path = os.path.join(self.venue_dir, '.meta.parse.yaml')

        self.download_status = self.load_meta(self.meta_download_path)  # type: Dict[str, bool]
        self.parse_status = self.load_meta(self.meta_parse_path)  # type: Dict[str, bool]

        os.makedirs(self.venue_dir, exist_ok=True)

    @staticmethod
    def load_meta(path):
        print(f'Attempting to load meta from {path}')
        if os.path.exists(path):
            return handler.yaml_load(path)
        return {}

    def has_downloaded(self, link):
        return self.download_status.get(link, False)

    def downloaded(self, link):
        self.download_status[link] = True
        handler.yaml_save(self.download_status, self.meta_download_path)

    def has_parsed(self, link):
        return self.parse_status.get(link, False)

    def parsed(self, link):
        self.parse_status[link] = True
        handler.yaml_save(self.parse_status, self.meta_parse_path)

    def extract_meta(self):
        # https://dblp.org/db/conf/aaai/aaai2025.html
        parts = self.index_url.split('/')
        venue_type = parts[-3]
        venue_name = parts[-2]
        return venue_type, venue_name

    def fetch(self):
        # 获取会议主页
        response = requests.get(self.index_url, headers=utils.headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'lxml')
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None

    def crawl(self, skip_parse=False):
        soup = self.fetch()
        if soup is None:
            return

        links = VenueType.parse_links(soup, self.venue_type)

        for link in links:
            crawler = PageCrawler(link)

            if self.has_downloaded(link) and not self.always_update:
                soup = None
            else:
                soup = crawler.crawl(strict_prefix=self.strict_prefix)
                if soup is None:
                    continue

                time.sleep(1)
            self.downloaded(link)

            if skip_parse or (self.has_parsed(link) and not self.always_update):
                continue

            if soup is None:
                content = crawler.load_html()
                soup = BeautifulSoup(content, 'lxml')

            crawler.parse(soup)
            self.parsed(link)
