import os
import requests
from bs4 import BeautifulSoup

import handler
import parser
import utils


class PageCrawler:
    def __init__(self, index_url):
        self.index_url = index_url  # https://dblp.org/db/conf/aaai/aaai2025.html
        self.venue_type, self.venue_name, self.page_name = parser.parse_link(self.index_url)
        self.venue_dir = os.path.join(utils.root_dir, f'{self.venue_type}-{self.venue_name}')

        os.makedirs(self.venue_dir, exist_ok=True)

    def fetch(self):
        response = requests.get(self.index_url, headers=utils.headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'lxml')  # 使用 lxml 解析器
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None

    @property
    def html_path(self):
        return os.path.join(self.venue_dir, self.page_name + '.html')

    @property
    def yaml_path(self):
        return os.path.join(self.venue_dir, self.page_name + '.yaml')

    def save_html(self, page_content):
        # Save the raw HTML content
        handler.file_write(self.html_path, page_content)
        print(f"Saved HTML to {self.html_path}")

    def load_html(self):
        return handler.file_read(self.html_path)

    def save_yaml(self, tracks_info):
        # Save the parsed data to YAML
        handler.yaml_save(tracks_info, self.yaml_path)
        print(f"Saved YAML to {self.yaml_path}")

    def crawl(self, strict_prefix=False):
        if strict_prefix and not self.page_name.startswith(self.venue_name):
            print(f"Invalid page name: {self.page_name} for the venue: {self.venue_name}, skipping.")
            return None
        soup = self.fetch()
        if soup is None:
            return None
        self.save_html(soup.prettify())  # Save HTML content
        return soup

    def parse(self, soup):
        page_data = parser.parse(soup)
        self.save_yaml(page_data)  # Save parsed data to YAML
