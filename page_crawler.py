import os
import requests
from bs4 import BeautifulSoup
import yaml

import utils


class PageCrawler:
    def __init__(self, index_url):
        self.index_url = index_url  # https://dblp.org/db/conf/aaai/aaai2025.html
        self.avenue, self.name = self.extract_meta()  # Extract conf-aaai, and aaai2025

        os.makedirs(self.avenue, exist_ok=True)

    def extract_meta(self):
        # https://dblp.org/db/conf/aaai/aaai2025.html -> extract conf, aaai, and aaai2025
        parts = self.index_url.split('/')
        avenue = parts[-3] + '-' + parts[-2]
        name = parts[-1].split('.')[0]
        return avenue, name

    def fetch(self):
        response = requests.get(self.index_url, headers=utils.headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'lxml')  # 使用 lxml 解析器
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None

    def parse(self, soup):
        tracks = {}
        current_track = None

        # Traverse through all elements under id="main"
        main_content = soup.find(id='main')
        if not main_content:
            return {}

        for element in main_content.find_all(['header', 'ul']):
            if element.name == 'header' and element.get('class') == ['h2']:
                # New track starts here
                track_name = element.find('h2').get_text(strip=True)
                current_track = track_name
                tracks[current_track] = []
            elif element.name == 'ul' and 'publ-list' in element.get('class', []):
                if current_track is None:
                    continue

                # This is a list of papers for the current track
                for li in element.find_all('li'):
                    cite = li.find('cite')
                    if cite:
                        # Extract author and title information
                        title = cite.find_all('span', itemprop='name')[-1].get_text(strip=True)
                        authors = self._extract_authors(cite)
                        tracks[current_track].append({
                            'title': title,
                            'authors': authors,
                        })

        return tracks

    def _extract_authors(self, cite):
        authors = []
        author_elements = cite.find_all('span', itemprop='author')
        for author_element in author_elements:
            author_name = author_element.find('span', itemprop='name').get_text(strip=True)
            author_link = author_element.find('a', itemprop='url')['href'] \
                if author_element.find('a', itemprop='url') else None
            author_pid = self._extract_pid(author_link)
            authors.append({
                'name': author_name,
                'pid': author_pid,
            })
        return authors

    @staticmethod
    def _extract_pid(author_link):
        if author_link:
            pid_parts = author_link.split('/pid/')[1].split('.html')[0].split('/')
            return f'{pid_parts[0]}-{pid_parts[1]}'
        else:
            return None  # If no PID is found, return None

    def save_html(self, page_content):
        # Save the raw HTML content
        html_filename = os.path.join(self.avenue, self.name + '.html')
        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(page_content)
        print(f"Saved HTML to {html_filename}")

    def save_yaml(self, tracks_info):
        # Save the parsed data to YAML
        yaml_filename = os.path.join(self.avenue, self.name + '.yaml')
        with open(yaml_filename, 'w', encoding='utf-8') as file:
            yaml.dump(tracks_info, file, allow_unicode=True)
        print(f"Saved YAML to {yaml_filename}")

    def crawl(self):
        soup = self.fetch()
        if soup is None:
            return {}
        tracks_info = self.parse(soup)
        self.save_html(soup.prettify())  # Save HTML content
        self.save_yaml(tracks_info)  # Save parsed data to YAML
        return tracks_info


# Example usage
# index_url = f'https://dblp.org/db/conf/aaai/aaai2025.html'

# Ensure the directory exists

# crawler = DblpCrawler(index_url)
# tracks_info = crawler.crawl()
#
# # Display the extracted information
# for track, papers in tracks_info.items():
#     print(f"Track: {track}")
#     for paper in papers:
#         authors = ", ".join([author['name'] for author in paper['authors']])
#         print(f"  Title: {paper['title']}")
#         print(f"  Authors: {authors}")
#         print()
