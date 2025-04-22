import argparse
import time

import handler
from avenue_crawler import AvenueCrawler

avenues = handler.yaml_load('avenue.yaml')
avenues = {avenue.upper(): link for avenue, link in avenues.items()}

parser = argparse.ArgumentParser()
parser.add_argument('--avenues', type=str, required=True, help='Avenue names')
parser.add_argument('--skip-parse', action='store_true', help='Skip parsing')
args = parser.parse_args()

crawling_avenues = args.avenues.split('+')
crawling_avenues = [avenue.upper() for avenue in crawling_avenues]

for avenue in crawling_avenues:
    if avenue not in avenues:
        print('Unknown avenue', avenue)
        continue

    link = avenues[avenue]
    print(f'Crawling {avenue} from {link}')
    crawler = AvenueCrawler(link)
    crawler.crawl(skip_parse=args.skip_parse)

    time.sleep(10)
