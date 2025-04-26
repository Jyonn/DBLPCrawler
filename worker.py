import argparse

import handler
from venue_crawler import VenueCrawler

venues = handler.yaml_load('venue.yaml')
venues = {venue.upper(): link for venue, link in venues.items()}

parser = argparse.ArgumentParser()
parser.add_argument('--venues', type=str, required=True, help='Avenue names')
parser.add_argument('--skip-parse', action='store_true', help='Skip parsing')
parser.add_argument('--strict-prefix', action='store_true', help='Strict venue name')
args = parser.parse_args()

crawling_venues = args.venues.split('+')
crawling_venues = [venue.upper() for venue in crawling_venues]

for venue in crawling_venues:
    if venue not in venues:
        print('Unknown venue', venue)
        continue

    link = venues[venue]
    print(f'Crawling {venue} from {link}')
    crawler = VenueCrawler(link)
    crawler.crawl(skip_parse=args.skip_parse)

    # time.sleep(10)
